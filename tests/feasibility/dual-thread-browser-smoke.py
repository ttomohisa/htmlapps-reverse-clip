#!/usr/bin/env python3
"""Real end-to-end ST + MT standalone smoke on a COOP/COEP HTTP server.

Runs in GitHub Actions Ubuntu with Python playwright, Chrome, ffmpeg/ffprobe.
This is not a phone, GitHub Pages SW activation, or direct file:// test.
"""
from __future__ import annotations

import functools
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import tempfile
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST), **kwargs)

    def end_headers(self):
        # Match Browser Kitty: isolate only the selected MT app routes.
        if self.path.split("?")[0] in ("/index.mt.html", "/index.mt.self-extract.html"):
            self.send_header("Cross-Origin-Opener-Policy", "same-origin")
            self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
            self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        super().end_headers()

    def log_message(self, *args):
        pass


def fixture(directory: Path) -> Path:
    images = directory / "frames"
    images.mkdir()
    for i in range(20):
        rgb = bytes([20 + i * 6, 18, 15])
        (images / f"{i:03d}.ppm").write_bytes(b"P6\n160 90\n255\n" + rgb * (160 * 90))
    target = directory / "source.mp4"
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-framerate", "10",
        "-i", str(images / "%03d.ppm"), "-c:v", "libx264",
        "-preset", "ultrafast", "-crf", "22", "-pix_fmt", "yuv420p", str(target)], check=True)
    return target


def hd_fixture(directory: Path) -> Path:
    """Generate native 1280x720 source without writing thousands of MB of PPMs."""
    target = directory / "hd-source.mp4"
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", "testsrc2=size=1280x720:rate=10",
        "-t", "2", "-c:v", "libx264", "-preset", "ultrafast", "-crf", "30",
        "-pix_fmt", "yuv420p", str(target)], check=True)
    return target


def validate_hd_mp4(filename: Path):
    validate_mp4(filename)
    data = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height", "-of", "json", str(filename)], text=True))
    video = data["streams"][0]
    assert (video["width"], video["height"]) == (1280, 720), data


def validate_mp4(filename: Path):
    data = json.loads(subprocess.check_output(["ffprobe", "-v", "error",
        "-show_entries", "stream=codec_type,codec_name,nb_frames:format=duration",
        "-of", "json", str(filename)], text=True))
    videos = [s for s in data["streams"] if s.get("codec_type") == "video"]
    assert len(videos) == 1 and len(data["streams"]) == 1, data
    assert videos[0]["codec_name"] == "h264", data
    assert 14 <= int(videos[0]["nb_frames"]) <= 16, data
    assert .9 <= float(data["format"]["duration"]) <= 1.1, data


def main():
    with tempfile.TemporaryDirectory(prefix="reverse-dual-real-") as temp:
        source = fixture(Path(temp))
        hd_source = hd_fixture(Path(temp))
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_port}"
        try:
            with sync_playwright() as playwright:
                import os
                kwargs = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
                if os.getenv("CHROMIUM_EXE"):
                    kwargs["executable_path"] = os.environ["CHROMIUM_EXE"]
                browser = playwright.chromium.launch(**kwargs)
                try:
                    for mode, html in (("single-thread", "index.html"),
                                       ("multi-thread", "index.mt.html")):
                        page = browser.new_page(viewport={"width": 390, "height": 844},
                            accept_downloads=True)
                        errors = []
                        external = []
                        page.on("pageerror", lambda error: errors.append(str(error)))
                        page.on("request", lambda request: external.append(request.url)
                            if not request.url.startswith((base, "blob:", "data:")) else None)
                        response = page.goto(f"{base}/{html}", wait_until="domcontentloaded",
                            timeout=30000)
                        assert response and response.status == 200
                        isolated = page.evaluate("globalThis.crossOriginIsolated === true")
                        shared = page.evaluate("typeof SharedArrayBuffer === 'function'")
                        assert isolated == (mode == "multi-thread"), (mode, isolated)
                        if mode == "multi-thread":
                            assert shared, (mode, shared)
                        assert ("MT" if mode == "multi-thread" else "ST") in page.locator("#runtimeModeLabel").inner_text()
                        page.locator("#sourceInput").set_input_files(str(source))
                        page.locator("#reversePanel").wait_for(state="visible", timeout=10000)
                        page.locator("#rangeStart").fill("0")
                        page.locator("#rangeStart").dispatch_event("change")
                        page.locator("#rangeEnd").fill("1")
                        page.locator("#rangeEnd").dispatch_event("change")
                        assert page.locator("#reverseButton").is_enabled(), (
                            mode, page.locator("#rangeNotice").inner_text())
                        page.locator("#reverseButton").click()
                        page.wait_for_function("""() =>
                          !document.querySelector('#resultArea').hidden ||
                          !document.querySelector('#reverseErrorDetails').hidden""",
                          timeout=90000)
                        if page.locator("#reverseErrorDetails").is_visible():
                            raise AssertionError(f"{mode} error: " +
                                page.locator("#reverseErrorDetail").inner_text())
                        assert page.locator("#resultVideo").evaluate(
                            "(video) => video.duration") >= .9
                        with page.expect_download(timeout=10000) as download:
                            page.locator("#saveReverseButton").click()
                        target = Path(temp) / f"{mode}-result.mp4"
                        download.value.save_as(target)
                        validate_mp4(target)

                        # A real cancellation can land while loadEmbedded() is
                        # awaiting WASM initialization. A runner that resolves
                        # after the abort must be disposed without ever running.
                        page.evaluate("""() => {
                          window.__originalFFmpeg = window.BrowserFFmpeg;
                          window.__lateLoads = 0;
                          window.__lateDisposals = 0;
                          window.__lateRuns = 0;
                          window.BrowserFFmpeg = {
                            loadEmbedded: async () => {
                              window.__lateLoads++;
                              await new Promise(resolve => setTimeout(resolve, 900));
                              return {
                                dispose() { window.__lateDisposals++; },
                                run() { window.__lateRuns++; throw new Error('stale runner executed'); }
                              };
                            }
                          };
                        }""")
                        page.locator("#reverseButton").click()
                        page.wait_for_function("() => window.__lateLoads === 1", timeout=15000)
                        page.locator("#cancelReverseButton").click()
                        page.wait_for_function("() => window.__lateDisposals === 1", timeout=15000)
                        assert page.evaluate("window.__lateRuns === 0"), mode
                        assert page.locator("#resultArea").is_hidden(), mode
                        assert page.locator("#reverseButton").is_enabled(), mode
                        print(f"[PASS] {mode} cancel during delayed runtime initialization disposes stale runner",
                              flush=True)

                        # Changing the source during an await must likewise
                        # invalidate the job and dispose *its own* late runner.
                        page.locator("#reverseButton").click()
                        page.wait_for_function("() => window.__lateLoads === 2", timeout=15000)
                        page.locator("#sourceInput").set_input_files(str(source))
                        page.wait_for_function("() => window.__lateDisposals === 2", timeout=15000)
                        page.locator("#reversePanel").wait_for(state="visible", timeout=10000)
                        assert page.evaluate("window.__lateRuns === 0"), mode
                        assert page.locator("#resultArea").is_hidden(), mode
                        page.evaluate("window.BrowserFFmpeg = window.__originalFFmpeg")
                        print(f"[PASS] {mode} source change disposes late runner without stale output",
                              flush=True)

                        # Re-run an actual MP4 export after the two cancellations.
                        page.locator("#rangeStart").fill("0")
                        page.locator("#rangeStart").dispatch_event("change")
                        page.locator("#rangeEnd").fill("1")
                        page.locator("#rangeEnd").dispatch_event("change")
                        assert page.locator("#reverseButton").is_enabled(), mode
                        page.locator("#reverseButton").click()
                        page.wait_for_function("""() =>
                          !document.querySelector('#resultArea').hidden ||
                          !document.querySelector('#reverseErrorDetails').hidden""",
                          timeout=90000)
                        if page.locator("#reverseErrorDetails").is_visible():
                            raise AssertionError(f"{mode} retry error: " +
                                page.locator("#reverseErrorDetail").inner_text())
                        with page.expect_download(timeout=10000) as download2:
                            page.locator("#saveReverseButton").click()
                        retry_target = Path(temp) / f"{mode}-after-cancel.mp4"
                        download2.value.save_as(retry_target)
                        validate_mp4(retry_target)
                        print(f"[PASS] {mode} real MP4 conversion recovers after cancel/source switch",
                              flush=True)

                        # Explicit HD 720p-class pilot: the source is truly
                        # 1280x720 (not the old long-edge 720px preset).
                        page.locator("#sourceInput").set_input_files(str(hd_source))
                        page.locator("#reversePanel").wait_for(state="visible", timeout=10000)
                        page.locator("#rangeStart").fill("0")
                        page.locator("#rangeStart").dispatch_event("change")
                        page.locator("#rangeEnd").fill("1")
                        page.locator("#rangeEnd").dispatch_event("change")
                        page.locator("#qualityInput").select_option("1280")
                        assert page.locator("#reverseButton").is_enabled(), (
                            mode, page.locator("#rangeNotice").inner_text())
                        assert "720p" in page.locator("#qualityInput").locator("option:checked").inner_text()
                        page.locator("#reverseButton").click()
                        page.wait_for_function("""() =>
                          !document.querySelector('#resultArea').hidden ||
                          !document.querySelector('#reverseErrorDetails').hidden""",
                          timeout=120000)
                        if page.locator("#reverseErrorDetails").is_visible():
                            raise AssertionError(f"{mode} HD pilot: " +
                                page.locator("#reverseErrorDetail").inner_text())
                        with page.expect_download(timeout=10000) as hd_download:
                            page.locator("#saveReverseButton").click()
                        hd_output = Path(temp) / f"{mode}-hd720.mp4"
                        hd_download.value.save_as(hd_output)
                        validate_hd_mp4(hd_output)
                        print(f"[PASS] {mode} 1-second native 1280x720 HD pilot export",
                              flush=True)

                        # v0.2.0 Foundation: replacing a *successful* source
                        # must clear the previous result and never leave an old
                        # download enabled. Every error path can recover.
                        page.locator("#sourceInput").set_input_files({
                            "name": "not-a-video.txt", "mimeType": "text/plain",
                            "buffer": b"this is not a video"
                        })
                        assert page.locator("#loadStatus").get_attribute("data-phase") == "error"
                        assert "MP4" in page.locator("#loadStatus").inner_text()
                        assert page.locator("#resultArea").is_hidden(), mode
                        assert page.locator("#reversePanel").is_hidden(), mode

                        # Switching languages must preserve the *error*, not
                        # misdescribe it as an empty or ready source.
                        page.locator("#languageButton").click()
                        assert page.locator("#loadStatus").get_attribute("data-phase") == "error"
                        assert "MP4" in page.locator("#loadStatus").inner_text()
                        page.locator("#languageButton").click()

                        page.locator("#sourceInput").set_input_files({
                            "name": "empty.mp4", "mimeType": "video/mp4",
                            "buffer": b""
                        })
                        assert page.locator("#loadStatus").get_attribute("data-phase") == "error"
                        assert page.locator("#resultArea").is_hidden(), mode

                        page.locator("#sourceInput").set_input_files({
                            "name": "broken.mp4", "mimeType": "video/mp4",
                            "buffer": b"not a real mp4 container"
                        })
                        page.locator("#loadStatus[data-phase='error']").wait_for(timeout=10000)
                        assert page.locator("#resultArea").is_hidden(), mode

                        page.locator("#sourceInput").set_input_files(str(source))
                        page.locator("#loadStatus[data-phase='ready']").wait_for(timeout=10000)
                        assert page.locator("#reversePanel").is_visible(), mode
                        assert page.locator("#reverseButton").is_enabled(), mode
                        print(f"[PASS] {mode} Foundation lifecycle rejects/replaces invalid media",
                              flush=True)

                        assert not errors, (mode, errors)
                        assert not external, (mode, external)
                        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth"), mode
                        print(f"[PASS] {mode} real standalone browser video reverse+download; "
                              f"isolated={isolated}, SAB={shared}", flush=True)
                        page.close()
                finally:
                    browser.close()
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    main()
