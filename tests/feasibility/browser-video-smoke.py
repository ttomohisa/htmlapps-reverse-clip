#!/usr/bin/env python3
"""Real Chrome long-clip frame-order regression for both standalone ST and MT.

Serve the exact CI-built HTML over localhost HTTP, with COOP/COEP only on MT.
Verify 10s frame order, repeated export, fractional segment boundaries, and
the Android mobile-file input path (simulated UA only, NOT an Android phone).
Needs Playwright, Chrome and native ffmpeg/ffprobe. No external media fixtures.
"""
import hashlib
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import threading
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
ANDROID_UA = ("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/154.0.0.0 Mobile Safari/537.36")

def run(*args):
    return subprocess.check_output(args, stderr=subprocess.PIPE)

def create_source(workdir):
    frames = workdir / "frames"
    frames.mkdir()
    for i in range(150):
        color = bytes([20 + i, 8, 8])
        (frames / f"{i:03}.ppm").write_bytes(b"P6\n160 90\n255\n" + color * (160 * 90))
    output = workdir / "15-seconds.mp4"
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
        "-framerate", "10", "-i", str(frames / "%03d.ppm"),
        "-c:v", "libx264", "-preset", "ultrafast", "-crf", "14",
        "-pix_fmt", "yuv420p", str(output)], check=True)
    return output

def inspect_mp4(output, frames, duration):
    report = json.loads(run("ffprobe", "-v", "error", "-show_entries",
        "stream=codec_type,codec_name,nb_frames:format=duration", "-of", "json", str(output)))
    video = [s for s in report["streams"] if s.get("codec_type") == "video"]
    assert len(video) == 1 and len(report["streams"]) == 1, report
    assert video[0]["codec_name"] == "h264", report
    assert int(video[0]["nb_frames"]) == frames, report
    assert abs(float(report["format"]["duration"]) - duration) < 0.07, report
    data = run("ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(output),
        "-vf", "scale=1:1:flags=neighbor,format=rgb24",
        "-fps_mode", "passthrough", "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1")
    colors = list(data[::3])
    assert len(colors) == frames, len(colors)
    assert all(a >= b - 4 for a, b in zip(colors, colors[1:])), (
        "Frame order increased across a reverse segment boundary", colors[:20], colors[-20:])
    return hashlib.sha256(output.read_bytes()).hexdigest()

def test_conversion(page, workdir, prefix, start, end, frames):
    # A successful conversion lands on Result. Return to Edit for the
    # next selection without losing or reusing stale generated output.
    assert page.locator("#flowEditButton").is_enabled()
    page.locator("#flowEditButton").click()
    assert page.locator("#rcWorkflow").get_attribute("data-flow-step") == "edit"
    assert page.locator("#workspaceTitle").inner_text() in ("区間と出力を編集", "Edit section and output")
    page.locator("#rangeStart").fill(str(start))
    page.locator("#rangeStart").dispatch_event("change")
    page.locator("#rangeEnd").fill(str(end))
    page.locator("#rangeEnd").dispatch_event("change")
    page.locator("#qualityInput").select_option("360")
    assert page.locator("#reverseButton").is_enabled(), (
        page.locator("#rangeNotice").inner_text())
    began = time.monotonic()
    page.locator("#reverseButton").click()
    page.wait_for_function("""() =>
      !document.querySelector('#resultArea').hidden ||
      !document.querySelector('#reverseErrorDetails').hidden""", timeout=150000)
    if page.locator("#reverseErrorDetails").is_visible():
        raise AssertionError(page.locator("#reverseErrorDetail").inner_text())
    assert page.locator("#rcWorkflow").get_attribute("data-flow-step") == "result"
    assert page.locator("#flowResultButton").get_attribute("aria-current") == "step"
    assert page.locator("#workspaceTitle").inner_text() in ("結果を確認・保存", "Preview and save result")
    assert page.locator("#resultDimensions").is_visible()
    assert "15fps" in page.locator("#resultDimensions").inner_text()
    assert page.locator("#flowSaveHint").is_hidden()
    with page.expect_download(timeout=15000) as download:
        page.locator("#saveReverseButton").click()
    assert page.locator("#flowSaveHint").is_visible()
    result = workdir / f"{prefix}.mp4"
    download.value.save_as(result)
    expected_seconds = frames / 15
    checksum = inspect_mp4(result, frames, expected_seconds)
    print(f"PASS {prefix}: {frames} frames / {expected_seconds:.3f}s "
          f"SHA-256={checksum} elapsed={time.monotonic()-began:.2f}s", flush=True)
    return checksum

class IsolationHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST), **kwargs)

    def end_headers(self):
        if self.path.split("?")[0] == "/index.mt.html":
            self.send_header("Cross-Origin-Opener-Policy", "same-origin")
            self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
            self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        super().end_headers()

    def log_message(self, *args):
        pass


def main():
    with tempfile.TemporaryDirectory(prefix="bk-reverse-10s-") as temp_dir:
        temp = Path(temp_dir)
        source = create_source(temp)
        server = ThreadingHTTPServer(("127.0.0.1", 0), IsolationHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        url_base = f"http://127.0.0.1:{server.server_port}"
        try:
            with sync_playwright() as pw:
                options = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
                if os.environ.get("CHROMIUM_EXE"):
                    options["executable_path"] = os.environ["CHROMIUM_EXE"]
                browser = pw.chromium.launch(**options)
                try:
                    # Simulate both Android local-file WorkerFS and provider
                    # fallback transports. This is NOT a physical phone test.
                    cases = [
                        ("single-thread", "index.html", None),
                        ("multi-thread", "index.mt.html", None),
                        ("st-mobile-ua", "index.html", ANDROID_UA),
                        ("st-mobile-provider-fallback", "index.html", ANDROID_UA),
                    ]
                    for name, html_name, user_agent in cases:
                        opts = {"viewport": {"width": 390, "height": 800},
                                "accept_downloads": True}
                        if user_agent:
                            opts["user_agent"] = user_agent
                        context = browser.new_context(**opts)
                        if name == "st-mobile-provider-fallback":
                            # Force only the tiny FileReaderSync probe to fail.
                            # The actual FFmpeg runner Worker runs normally,
                            # so an exported MP4 also tests the MEMFS fallback.
                            context.add_init_script(script="""(() => {
                              const NativeWorker = window.Worker;
                              window.Worker = class SimulatedProviderWorker extends NativeWorker {
                                postMessage(data, transfer) {
                                  if (data instanceof File) {
                                    queueMicrotask(() => this.onmessage?.({data:{ok:false}}));
                                    return;
                                  }
                                  return super.postMessage(data, transfer);
                                }
                              };
                            })();""")
                        page = context.new_page()
                        errors = []
                        external = []
                        page.on("pageerror", lambda e: errors.append(str(e)))
                        page.on("console", lambda m: errors.append(m.text)
                                if m.type == "error" else None)
                        page.on("request", lambda req: external.append(req.url)
                                if req.url.startswith(("https://", "http://")) and
                                   not req.url.startswith(url_base) else None)
                        result = page.goto(f"{url_base}/{html_name}", wait_until="domcontentloaded",
                                           timeout=45000)
                        assert result and result.status == 200
                        is_mt = name == "multi-thread"
                        assert page.evaluate("globalThis.crossOriginIsolated") == is_mt, name
                        assert page.evaluate("typeof SharedArrayBuffer === 'function'") == is_mt, name
                        assert page.locator("#rcWorkflow").get_attribute("data-flow-step") == "video"
                        assert page.locator("#flowVideoButton").get_attribute("aria-current") == "step"
                        assert page.locator("#flowEditButton").is_disabled()
                        assert page.locator("#flowResultButton").is_disabled()
                        assert page.locator("#dropZone").is_visible()
                        assert page.locator("#diagnosticsDetails").evaluate("el => !el.open")
                        assert page.locator("#developmentDetails").evaluate("el => !el.open")
                        assert page.locator("#probeButton").is_hidden()
                        assert page.locator("#guaranteesTitle").is_hidden()
                        page.locator("#sourceInput").set_input_files(str(source))
                        page.locator("#reversePanel").wait_for(state="visible", timeout=30000)
                        assert page.locator("#rcWorkflow").get_attribute("data-flow-step") == "edit"
                        assert page.locator("#workspaceTitle").inner_text() in ("区間と出力を編集", "Edit section and output")
                        assert page.locator("#dropZone").is_hidden()
                        assert page.locator("#flowResultButton").is_disabled()
                        page.locator("#flowVideoButton").click()
                        assert page.locator("#rcWorkflow").get_attribute("data-flow-step") == "video"
                        assert page.locator("#workspaceTitle").inner_text() in ("動画を読み込む", "Load a video")
                        assert page.locator("#selectedSourceSummary").is_visible()
                        assert "15-seconds.mp4" in page.locator("#selectedSourceText").inner_text()
                        page.locator("#flowGoEditButton").click()
                        assert page.locator("#rcWorkflow").get_attribute("data-flow-step") == "edit"

                        initial_frames = 15 if name == "st-mobile-provider-fallback" else 150
                        initial_seconds = 1 if name == "st-mobile-provider-fallback" else 10
                        first = test_conversion(page, temp, f"{name}-first",
                                                0, initial_seconds, initial_frames)
                        if name in ("single-thread", "multi-thread"):
                            # Both runtime variants must successfully decode,
                            # re-encode and save a second 10s job in the SAME tab.
                            second = test_conversion(page, temp, f"{name}-10s-repeat", 0, 10, 150)
                            if not is_mt:
                                # ST has historically been byte-reproducible;
                                # do not assume nondeterministic pthread scheduling
                                # gives MT identical bytes.
                                assert second == first, "ST repeated 10s MP4 bytes changed"
                            # Tests the 2s chunk boundaries from a non-zero start.
                            test_conversion(page, temp, f"{name}-fractional", .1, 9.87, 146)
                            test_conversion(page, temp, f"{name}-5s", 0, 5, 75)
                            # Cancel before starting a new job or shortly after
                            # its first chunk; no previous output may be retained.
                            # The 160x90 test fixture can finish before
                            # Playwright's click stability checks complete.
                            # Dispatch start+cancel in one JS task so the
                            # cancel is guaranteed to occur while async WASM
                            # setup is still pending (no artificial sleeps).
                            page.locator("#flowEditButton").click()
                            page.evaluate("""() => {
                                const start = document.querySelector('#reverseButton');
                                const cancel = document.querySelector('#cancelReverseButton');
                                if (start.disabled) throw new Error('reverse action disabled');
                                start.click();
                                if (cancel.hidden) throw new Error('cancel action was not exposed');
                                cancel.click();
                            }""")
                            page.wait_for_timeout(250)
                            assert page.locator("#resultArea").is_hidden()
                            assert page.locator("#flowResultButton").is_disabled()
                            assert not page.locator("#saveReverseButton").is_visible()
                        else:
                            # The app's own downloaded diagnostic must report
                            # the real transport selected by the input handler.
                            assert page.evaluate("""() =>
                                navigator.userAgent.includes('Android')""")
                            # Diagnostics were moved behind an explicit
                            # disclosure. Normal editing users need not see
                            # internal Worker/WASM controls on every visit.
                            assert page.locator("#diagnosticsDetails").evaluate(
                                "el => !el.open")
                            page.locator("#diagnosticsDetails > summary").click()
                            with page.expect_download(timeout=10000) as diagnostic:
                                page.locator("#downloadReportButton").click()
                            report_path = temp / f"{name}-diagnostic.json"
                            diagnostic.value.save_as(report_path)
                            raw_report = report_path.read_text(encoding="utf-8")
                            report = json.loads(raw_report)
                            expected_transport = ("memory" if name.endswith("provider-fallback")
                                                  else "workerfs")
                            assert report["source"]["transport"] == expected_transport, report["source"]
                            assert report["reverseConversion"]["inputTransport"] == expected_transport, report["reverseConversion"]
                            assert "15-seconds" not in raw_report
                            print(f"[PASS] simulated Android {name}: {expected_transport} "
                                  "real MP4, no source filename", flush=True)

                        if name == "single-thread":
                            # Responsive keyboard/tap/long filename regression.
                            # Replacing a source after export must invalidate the
                            # old Result and save immediately.
                            long_name = "とても長い動画のファイル名-" * 18 + ".mp4"
                            page.locator("#flowVideoButton").click()
                            page.locator("#sourceInput").set_input_files({
                                "name": long_name, "mimeType": "video/mp4",
                                "buffer": source.read_bytes()})
                            page.locator("#reversePanel").wait_for(state="visible", timeout=30000)
                            assert page.locator("#flowResultButton").is_disabled()
                            assert page.locator("#resultArea").is_hidden()
                            page.locator("#flowVideoButton").click()
                            assert long_name in page.locator("#selectedSourceText").inner_text()
                            original_edit = page.locator("#flowEditButton").inner_text()
                            original_result = page.locator("#flowResultButton").inner_text()
                            page.locator("#languageButton").click()
                            changed_edit = page.locator("#flowEditButton").inner_text()
                            changed_result = page.locator("#flowResultButton").inner_text()
                            assert {original_edit, changed_edit} == {"Edit", "編集"}
                            assert {original_result, changed_result} == {"Result", "結果"}
                            page.locator("#languageButton").click()
                            assert page.locator("#flowEditButton").inner_text() == original_edit
                            for width in (320, 360, 390):
                                page.set_viewport_size({"width": width, "height": 720})
                                assert not page.evaluate("""() =>
                                    document.documentElement.scrollWidth > innerWidth"""), width
                                for control in ("#flowVideoButton","#flowEditButton","#flowResultButton"):
                                    assert page.locator(control).bounding_box()["height"] >= 44, control
                                page.locator("#flowGoEditButton").click()
                                assert page.locator("#rcWorkflow").get_attribute("data-flow-step") == "edit"
                                assert page.locator("#reverseButton").is_visible()
                                page.locator("#flowVideoButton").click()
                            page.set_viewport_size({"width": 390, "height": 800})
                            print("[PASS] 320/360/390 widths, JA/EN mobile nav, "
                                  "long filename, stale-result invalidation", flush=True)

                        assert not page.evaluate("document.documentElement.scrollWidth > innerWidth")
                        assert not errors, (name, errors)
                        assert not external, (name, external)
                        print(f"PASS {name}: isolation={is_mt}, network/layout/JS", flush=True)
                        context.close()
                finally:
                    browser.close()
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    main()
