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
    with page.expect_download(timeout=15000) as download:
        page.locator("#saveReverseButton").click()
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
                    # The third case exercises the 64 MiB in-memory input
                    # transport with a simulated Android UA. It is explicitly
                    # NOT physical-device or Android Chrome evidence.
                    cases = [
                        ("single-thread", "index.html", None),
                        ("multi-thread", "index.mt.html", None),
                        ("st-mobile-ua", "index.html", ANDROID_UA),
                    ]
                    for name, html_name, user_agent in cases:
                        opts = {"viewport": {"width": 390, "height": 800},
                                "accept_downloads": True}
                        if user_agent:
                            opts["user_agent"] = user_agent
                        context = browser.new_context(**opts)
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
                        page.locator("#sourceInput").set_input_files(str(source))
                        page.locator("#reversePanel").wait_for(state="visible", timeout=30000)

                        first = test_conversion(page, temp, f"{name}-10s", 0, 10, 150)
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
                            page.locator("#reverseButton").click()
                            page.locator("#cancelReverseButton").click()
                            page.wait_for_timeout(250)
                            assert page.locator("#resultArea").is_hidden()
                            assert not page.locator("#saveReverseButton").is_visible()
                        else:
                            # Android-UA is only a transport regression case.
                            # The real device's memory/performance remains unknown.
                            assert page.evaluate("""() =>
                                navigator.userAgent.includes('Android')""")

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
