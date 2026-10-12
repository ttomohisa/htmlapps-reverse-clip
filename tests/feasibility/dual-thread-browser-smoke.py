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
