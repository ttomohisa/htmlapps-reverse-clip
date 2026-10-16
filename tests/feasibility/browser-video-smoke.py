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

def create_compat_sources(workdir):
    # Genuine short-but-decodable and 30/60fps MP4 fixtures. These are
    # generated locally during CI; no user media or network input.
    results = {}
    for label, fps, count in (("too-short", 15, 4),
                              ("fps30", 30, 60),
                              ("fps60", 60, 120)):
        target = workdir / f"{label}.mp4"
        subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", f"testsrc2=size=160x90:rate={fps}",
            "-frames:v", str(count), "-c:v", "libx264", "-preset", "ultrafast",
            "-pix_fmt", "yuv420p", str(target)], check=True)
        results[label] = target
    # A genuine H.264 QuickTime .mov container; a codec and a
    # container are different compatibility dimensions.
    mov=workdir/"h264.mov"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-i",str(results["fps30"]),"-map","0:v:0","-c","copy",str(mov)],
        check=True)
    results["mov"]=mov

    # A display-matrix rotated MOV is separate from a physically
    # portrait-encoded video. Its presentation metadata must not be
    # confused with coded width/height. Record both in the test.
    rotated=workdir/"h264-rotate90.mov"
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-display_rotation:v:0","90",
        "-i",str(mov),"-map","0:v:0","-c","copy",str(rotated)],check=True)
    results["rotated-mov"]=rotated
    rotate_info=json.loads(run("ffprobe","-v","error","-select_streams","v:0",
        "-show_entries","stream_side_data=rotation","-of","json",str(rotated)))
    rotations=[d.get("rotation") for x in rotate_info.get("streams",[])
               for d in x.get("side_data_list",[]) if "rotation" in d]
    assert any(abs(float(x))==90 for x in rotations),rotate_info

    # A plausible ISO BMFF ftyp/mdat prefix but missing moov and media
    # must pass sniffing and fail later in browser decode, not export.
    corrupt=workdir/"truncated-h264.mp4"
    corrupt.write_bytes(results["fps30"].read_bytes()[:128])
    assert corrupt.stat().st_size==128
    results["truncated"]=corrupt
    return results

def inspect_video_shape(path):
    report=json.loads(run("ffprobe","-v","error","-select_streams","v:0",
        "-show_entries","stream=width,height:stream_side_data=rotation",
        "-of","json",str(path)))
    streams=report.get("streams",[])
    assert len(streams)==1,report
    v=streams[0]
    return {"coded":[v["width"],v["height"]],
            "rotations":[d.get("rotation") for d in v.get("side_data_list",[])
                         if "rotation" in d]}

def inspect_compat_mp4(output, expected_frames=15):
    report = json.loads(run("ffprobe", "-v", "error",
        "-show_entries", "stream=codec_name,codec_type,nb_frames:format=duration",
        "-of", "json", str(output)))
    video = [s for s in report["streams"] if s.get("codec_type") == "video"]
    assert len(video) == 1 and video[0]["codec_name"] == "h264", report
    assert int(video[0]["nb_frames"]) == expected_frames, report
    assert abs(float(report["format"]["duration"]) - expected_frames / 15) < .07, report

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

def test_conversion(page, workdir, prefix, start, end, frames, invalidate_after=True):
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
    assert page.locator("#workspaceTitle").evaluate("(el) => document.activeElement === el"), prefix
    assert page.locator("#flowResultButton").get_attribute("aria-current") == "step"
    # Automatic focus should be visible below the sticky page header.
    heading_geometry=page.evaluate("""() => {
        const r=document.querySelector('#workspaceTitle').getBoundingClientRect();
        const h=document.querySelector('.app-header').getBoundingClientRect();
        return {top:r.top,bottom:r.bottom,headerBottom:h.bottom,
                viewport:innerHeight,scrollY:scrollY,
                maxScroll:document.documentElement.scrollHeight-innerHeight};
    }""")
    assert (heading_geometry["top"] >= heading_geometry["headerBottom"] - 2 and
            heading_geometry["bottom"] <= heading_geometry["viewport"]), (
                "hidden step heading", prefix, heading_geometry)
    page.wait_for_function("() => !document.querySelector('#flowVideoButton').disabled")
    assert page.locator("#workspaceTitle").inner_text() in ("結果を確認・保存", "Preview and save result")
    assert page.locator("#resultDimensions").is_visible()
    assert "15fps" in page.locator("#resultDimensions").inner_text()
    assert page.locator("#flowSaveHint").is_hidden()
    initial_lang=page.locator("html").get_attribute("lang")
    assert page.locator("#sourceVideo").get_attribute("aria-label") == (
        "元動画のプレビュー" if initial_lang=="ja" else "Source video preview")
    assert page.locator("#resultVideo").get_attribute("aria-label") == (
        "逆再生MP4のプレビュー" if initial_lang=="ja" else "Reversed MP4 preview")
    assert page.locator("#reverseProgress").get_attribute("aria-label") == (
        "MP4変換の進行状況" if initial_lang=="ja" else "MP4 conversion progress")
    if prefix in ("single-thread-first", "multi-thread-first"):
        # Switching JA/EN after real MP4 generation must re-render the
        # completed result's mode/audio/bytes, preserving the same Blob.
        original_lang = page.locator("html").get_attribute("lang")
        original_summary = page.locator("#resultInfo").inner_text()
        original_url = page.locator("#resultVideo").evaluate("(v) => v.currentSrc")
        page.locator("#languageButton").click()
        assert page.locator("html").get_attribute("lang") != original_lang
        switched_summary = page.locator("#resultInfo").inner_text()
        assert switched_summary != original_summary, (original_summary, switched_summary)
        if page.locator("html").get_attribute("lang") == "en":
            assert "silent video" in switched_summary, switched_summary
        else:
            assert "映像のみ" in switched_summary, switched_summary
        assert page.locator("#resultVideo").evaluate("(v) => v.currentSrc") == original_url
        assert page.locator("#resultVideo").get_attribute("aria-label") == (
            "逆再生MP4のプレビュー" if page.locator("html").get_attribute("lang")=="ja"
            else "Reversed MP4 preview")
        assert page.locator("#flowResultButton").is_enabled()
        page.locator("#languageButton").click()
        assert page.locator("#resultInfo").inner_text() == original_summary
        assert page.locator("html").get_attribute("lang") == original_lang
    if prefix == "single-thread-first":
        # An MP4 that was not downloaded must survive Cancel, including
        # its Blob URL. This is an actual browser dialog, not a JS mock.
        old_src = page.locator("#resultVideo").evaluate("(video) => video.currentSrc")
        page.locator("#flowVideoButton").click()
        page.locator("#sourceInput").set_input_files(str(workdir / "15-seconds.mp4"))
        page.locator("#appConfirmDialog").wait_for(state="visible")
        # A short phone/soft-keyboard viewport must not clip its sheet
        # or make its Cancel/Replace action unreachable.
        page.set_viewport_size({"width": 320, "height": 420})
        assert page.evaluate("""() => {
            const d=document.querySelector('#appConfirmDialog').getBoundingClientRect();
            return d.left >= -1 && d.right <= innerWidth+1 &&
                d.top >= -1 && d.bottom <= innerHeight+1;
        }"""), "confirmation dialog extends past short phone viewport"
        for selector in ("#appConfirmCancel", "#appConfirmOk"):
            assert page.locator(selector).bounding_box()["height"] >= 44, selector
        assert page.locator("#flowResultButton").is_enabled()
        page.locator("#appConfirmCancel").click()
        page.wait_for_function("""() =>
            document.querySelector('#rcWorkflow').dataset.flowStep === 'result'""")
        assert page.locator("#workspaceTitle").evaluate("(el) => document.activeElement === el")
        assert page.locator("#resultVideo").evaluate("(video) => video.currentSrc") == old_src
        # A rejected multi-file drop on Video must also keep the MP4.
        page.locator("#flowVideoButton").click()
        page.evaluate("""() => {
            const dt = new DataTransfer();
            dt.items.add(new File(['one'],'one.mp4',{type:'video/mp4'}));
            dt.items.add(new File(['two'],'two.mp4',{type:'video/mp4'}));
            document.querySelector('#dropZone').dispatchEvent(
                new DragEvent('drop',{bubbles:true,cancelable:true,dataTransfer:dt}));
        }""")
        assert page.locator("#rcWorkflow").get_attribute("data-flow-step") == "result"
        assert page.locator("#resultVideo").evaluate("(video) => video.currentSrc") == old_src
        assert page.locator("#flowResultButton").is_enabled()
        page.evaluate("window.AppToast.dismiss()")
        # The filename and explicit MP4 action remain reachable even
        # with little usable height (simulated software keyboard).
        page.locator("#reverseFilename").fill("完成版.mp4")
        assert not page.evaluate("document.documentElement.scrollWidth > innerWidth")
        page.locator("#saveReverseButton").scroll_into_view_if_needed()
        rect = page.locator("#saveReverseButton").bounding_box()
        assert rect and rect["height"] >= 44 and rect["x"] >= -1
        assert rect["x"] + rect["width"] <= 321, rect
        page.set_viewport_size({"width": 390, "height": 800})
    with page.expect_download(timeout=15000) as download:
        page.locator("#saveReverseButton").click()
    assert page.locator("#flowSaveHint").is_visible()
    hint = page.locator("#flowSaveHint").inner_text()
    assert ("ダウンロードを開始" in hint or "download started" in hint.lower()), hint
    if prefix == "single-thread-first":
        assert download.value.suggested_filename == "完成版.mp4", download.value.suggested_filename
    result = workdir / f"{prefix}.mp4"
    download.value.save_as(result)
    expected_seconds = frames / 15
    checksum = inspect_mp4(result, frames, expected_seconds)

    # Mobile output (including the AAC variant) must stop playback when
    # leaving Result. Navigating back should retain the same verified Blob.
    result_video = page.locator("#resultVideo")
    output_src = result_video.evaluate("(video) => video.currentSrc")
    result_video.evaluate("""async video => {
        video.loop = true;
        video.muted = true;
        await video.play();
    }""")
    assert not result_video.evaluate("(video) => video.paused"), prefix
    page.locator("#flowBackToEditButton").click()
    assert page.locator("#workspaceTitle").evaluate("(el) => document.activeElement === el"), prefix
    assert result_video.evaluate("(video) => video.paused"), prefix
    assert page.locator("#flowResultButton").is_enabled(), prefix
    page.locator("#flowResultButton").click()
    assert result_video.evaluate("(video) => video.currentSrc") == output_src, prefix
    assert page.locator("#saveReverseButton").is_enabled(), prefix
    result_video.evaluate("(video) => { video.loop = false; }")

    # Android file-provider scenarios inspect the completed conversion
    # diagnostics later; preserve their state until after that assertion.
    # Other scenarios check input-before-blur invalidation here.
    if invalidate_after:
        page.locator("#flowEditButton").click()
        page.locator("#rangeEnd").evaluate("""field => {
            field.value = '0.9';
            field.dispatchEvent(new Event('input', {bubbles:true}));
        }""")
        assert page.locator("#flowResultButton").is_disabled(), prefix
        assert page.locator("#resultArea").evaluate("(el) => el.hidden"), prefix
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
        compat = create_compat_sources(temp)
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
                        if name in ("single-thread","multi-thread"):
                            # Decodable sources below the 0.5s minimum must
                            # not be misclassified as corrupt or unsupported.
                            page.locator("#sourceInput").set_input_files(
                                str(compat["too-short"]))
                            page.locator("#loadStatus[data-phase='error']").wait_for(
                                timeout=10000)
                            assert ("0.5" in page.locator("#loadStatus").inner_text())
                            assert page.locator("#reversePanel").is_hidden()
                            assert page.locator("#flowResultButton").is_disabled()
                            before=page.locator("#loadStatus").inner_text()
                            page.locator("#languageButton").click()
                            assert "0.5" in page.locator("#loadStatus").inner_text()
                            assert page.locator("#loadStatus").inner_text() != before
                            page.locator("#languageButton").click()
                            assert page.locator("#loadStatus").inner_text() == before
                            print(f"[PASS] {name} decodable short input classified separately",
                                  flush=True)
                        page.locator("#sourceInput").set_input_files(str(source))
                        page.locator("#reversePanel").wait_for(state="visible", timeout=30000)
                        assert page.locator("#rcWorkflow").get_attribute("data-flow-step") == "edit"
                        assert page.locator("#workspaceTitle").evaluate("(el) => document.activeElement === el")
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
                                                0, initial_seconds, initial_frames,
                                                invalidate_after=name in ("single-thread", "multi-thread"))
                        if name in ("single-thread", "multi-thread"):
                            if name == "single-thread":
                                # Force a deterministic runtime-preflight
                                # failure (not an actual media/WASM defect).
                                # StandaloneAssets itself is Object.freeze()d:
                                # assigning its .has property does nothing.
                                # Replace the global facade with a shallow
                                # wrapper and verify that the mock is active.
                                page.evaluate("""() => {
                                    window.__v07RealAssets = window.StandaloneAssets;
                                    window.StandaloneAssets = {
                                        ...window.__v07RealAssets,
                                        has(dep,key) {
                                            if(dep==='reverse-wasm' && key==='coreWasm') return false;
                                            return window.__v07RealAssets.has(dep,key);
                                        }
                                    };
                                    if(window.StandaloneAssets.has('reverse-wasm','coreWasm'))
                                        throw new Error('missing-core test fixture did not take effect');
                                }""")
                                page.locator("#flowEditButton").click()
                                page.locator("#rangeStart").fill("0")
                                page.locator("#rangeEnd").fill("1")
                                assert page.locator("#reverseButton").is_enabled()
                                page.locator("#reverseButton").click()
                                page.locator("#reverseErrorDetails").wait_for(state="visible", timeout=15000)
                                page.wait_for_function("""() =>
                                    !document.querySelector('#flowVideoButton').disabled""")
                                assert page.locator("#reverseErrorDetails").evaluate("(el) => el.open")
                                assert page.locator("#reverseErrorDetails > summary").evaluate(
                                    "(el) => document.activeElement === el")
                                assert page.locator("#flowResultButton").is_disabled()
                                assert page.locator("#resultArea").is_hidden()
                                status = page.locator("#reverseStatus").inner_text()
                                page.locator("#languageButton").click()
                                translated_status = page.locator("#reverseStatus").inner_text()
                                assert translated_status != status, (status, translated_status)
                                assert "MP4" in translated_status
                                assert page.locator("#reverseErrorDetails").is_visible()
                                page.locator("#languageButton").click()
                                assert page.locator("#reverseStatus").inner_text() == status
                                page.evaluate("""() => {
                                    window.StandaloneAssets = window.__v07RealAssets;
                                    delete window.__v07RealAssets;
                                }""")
                                print("[PASS] v0.7 localized failure/diagnostics and real retry readiness",
                                      flush=True)
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
                            if name == "single-thread":
                                # Accepting a replacement after generating a
                                # *new* undownloaded MP4 must invalidate it.
                                page.locator("#flowEditButton").click()
                                page.locator("#rangeStart").fill("0")
                                page.locator("#rangeEnd").fill("1")
                                page.locator("#rangeEnd").dispatch_event("change")
                                assert page.locator("#reverseButton").is_enabled()
                                page.locator("#reverseButton").click()
                                page.wait_for_function("""() =>
                                    !document.querySelector('#resultArea').hidden ||
                                    !document.querySelector('#reverseErrorDetails').hidden""",
                                    timeout=120000)
                                assert page.locator("#resultArea").is_visible()
                                page.locator("#flowVideoButton").click()
                                page.locator("#sourceInput").set_input_files(str(source))
                                page.locator("#appConfirmDialog").wait_for(state="visible")
                                page.locator("#appConfirmOk").click()
                                page.locator("#reversePanel").wait_for(state="visible", timeout=30000)
                                assert page.locator("#flowResultButton").is_disabled()
                                assert page.locator("#resultArea").is_hidden()
                                assert page.locator("#sourceName").inner_text() == source.name
                                print("[PASS] unsaved MP4 replace-confirm cancel/approve and stale result clearing",
                                      flush=True)
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
                                const videoStep = document.querySelector('#flowVideoButton');
                                const resultStep = document.querySelector('#flowResultButton');
                                if (start.disabled) throw new Error('reverse action disabled');
                                start.click();
                                if (cancel.hidden) throw new Error('cancel action was not exposed');
                                if (!videoStep.disabled || !resultStep.disabled)
                                    throw new Error('Video/Result navigation enabled during conversion');
                                videoStep.click();
                                if (document.querySelector('#rcWorkflow').dataset.flowStep !== 'edit' ||
                                    cancel.hidden)
                                    throw new Error('conversion navigation hid Cancel');
                                cancel.click();
                                if (videoStep.disabled)
                                    throw new Error('Video step still locked after cancel');
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

                        if name in ("single-thread","multi-thread"):
                            # Compatibility: real H.264 input at 30fps or 60fps
                            # must produce 15fps, without silently claiming to
                            # preserve its original frame rate.
                            for label in ("fps30","fps60"):
                                page.locator("#flowVideoButton").click()
                                page.locator("#sourceInput").set_input_files(
                                    str(compat[label]))
                                page.locator("#reversePanel").wait_for(
                                    state="visible", timeout=10000)
                                page.locator("#flowEditButton").click()
                                assert page.locator("#sourceCompatibilityDetails").count() == 1
                                assert not page.locator("#sourceCompatibilityDetails").evaluate(
                                    "(el) => el.open")
                                page.locator("#sourceCompatibilityDetails > summary").click()
                                warning=page.locator("#sourceCompatibilityDetails").inner_text()
                                assert "15fps" in warning
                                page.locator("#rangeStart").fill("0")
                                page.locator("#rangeEnd").fill("1")
                                assert page.locator("#reverseButton").is_enabled()
                                page.locator("#reverseButton").click()
                                page.wait_for_function("""() =>
                                  !document.querySelector('#resultArea').hidden ||
                                  !document.querySelector('#reverseErrorDetails').hidden""",
                                  timeout=120000)
                                if page.locator("#reverseErrorDetails").is_visible():
                                    raise AssertionError(
                                        f"{name} {label}: " +
                                        page.locator("#reverseErrorDetail").text_content())
                                with page.expect_download(timeout=15000) as dl:
                                    page.locator("#saveReverseButton").click()
                                out_file=temp/f"{name}-{label}-compat.mp4"
                                dl.value.save_as(out_file)
                                inspect_compat_mp4(out_file)
                                print(f"[PASS] {name} {label} => 15fps H.264 MP4",
                                      flush=True)
                        if name in ("single-thread","multi-thread"):
                            # H.264 in MOV is an ordinary browser-supported
                            # container in Chrome, not automatic HEVC support.
                            for label in ("mov","rotated-mov"):
                                page.locator("#flowVideoButton").click()
                                page.locator("#sourceInput").set_input_files(
                                    str(compat[label]))
                                page.locator("#reversePanel").wait_for(
                                    state="visible",timeout=10000)
                                source_shape=page.locator("#sourceVideo").evaluate(
                                    "(v) => [v.videoWidth,v.videoHeight]")
                                assert all(dim>0 for dim in source_shape),source_shape
                                page.locator("#flowEditButton").click()
                                page.locator("#rangeStart").fill("0")
                                page.locator("#rangeEnd").fill("1")
                                assert page.locator("#reverseButton").is_enabled()
                                page.locator("#reverseButton").click()
                                page.wait_for_function("""() =>
                                    !document.querySelector('#resultArea').hidden ||
                                    !document.querySelector('#reverseErrorDetails').hidden""",
                                    timeout=120000)
                                if page.locator("#reverseErrorDetails").is_visible():
                                    raise AssertionError(
                                        f"{name} {label}: "+
                                        page.locator("#reverseErrorDetail").text_content())
                                with page.expect_download(timeout=15000) as dl:
                                    page.locator("#saveReverseButton").click()
                                out_file=temp/f"{name}-{label}-output.mp4"
                                dl.value.save_as(out_file)
                                inspect_compat_mp4(out_file)
                                rendered_shape=page.locator("#resultVideo").evaluate(
                                    "(v) => [v.videoWidth,v.videoHeight]")
                                file_shape=inspect_video_shape(out_file)
                                print(f"[OBSERVE] {name} {label}: source-rendered={source_shape}, "
                                      f"output-rendered={rendered_shape}, file={file_shape}, "
                                      f"input={inspect_video_shape(compat[label])}",
                                      flush=True)
                                if label=="mov":
                                    assert rendered_shape==source_shape,(
                                        "H.264 MOV source/export shape mismatch",
                                        source_shape,rendered_shape)
                            # A truncated file with plausible ftyp must fail
                            # decoder validation and never expose a stale MP4.
                            page.locator("#flowVideoButton").click()
                            page.locator("#sourceInput").set_input_files(
                                str(compat["truncated"]))
                            page.locator("#loadStatus[data-phase='error']").wait_for(
                                timeout=10000)
                            assert page.locator("#resultArea").is_hidden()
                            assert page.locator("#flowResultButton").is_disabled()
                            assert page.locator("#reversePanel").is_hidden()
                            assert page.locator("#loadStatus").inner_text() in (
                                "動画をプレビューできません。対応していない形式か破損している可能性があります。",
                                "This video cannot be previewed. The format may be unsupported or the file damaged.",
                                "MP4/MOVの動画データを確認できません。拡張子だけを変えたファイルは利用できません。",
                                "This does not have a recognizable MP4/MOV container header. Renaming a file is not a video conversion.")
                            print(f"[PASS] {name} H.264 MOV + rotated MOV decoded/exported; "
                                  "truncated plausible MP4 refused without stale Save",
                                  flush=True)
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
                                page.set_viewport_size({"width": width, "height": 568 if width == 320 else 720})
                                assert not page.evaluate("""() =>
                                    document.documentElement.scrollWidth > innerWidth"""), width
                                for control in ("#flowVideoButton","#flowEditButton","#flowResultButton",
                                                "#pickButton","#captureButton"):
                                    assert page.locator(control).bounding_box()["height"] >= 44, control
                                page.locator("#flowGoEditButton").click()
                                assert page.locator("#rcWorkflow").get_attribute("data-flow-step") == "edit"
                                assert page.evaluate("""() => {
                                    const r=document.querySelector('#workspaceTitle').getBoundingClientRect();
                                    const h=document.querySelector('.app-header').getBoundingClientRect();
                                    return r.top >= h.bottom-2 && r.bottom <= innerHeight;
                                }"""), ("heading offscreen in mobile", width)
                                assert page.locator("#reverseButton").is_visible()
                                assert page.locator("#reverseButton").bounding_box()["height"] >= 44
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
