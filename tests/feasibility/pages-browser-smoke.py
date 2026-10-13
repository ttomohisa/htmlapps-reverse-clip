#!/usr/bin/env python3
"""Exercise the actual GitHub Pages ST root and MT /mt/ Service Worker path.

Unlike dual-thread-browser-smoke.py, this HTTP server intentionally adds NO
COOP/COEP headers. Successful MT isolation therefore proves that the pinned
Pages same-origin COI Service Worker performed the navigation interception.
"""
from __future__ import annotations

import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import subprocess
import tempfile
import threading
import time

from playwright.sync_api import sync_playwright, Error as PlaywrightError

ROOT = Path(__file__).resolve().parents[2]
PAGES = ROOT / "pages-dist"


class PagesHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PAGES), **kwargs)

    def log_message(self, *args):
        pass


def fixture(work: Path) -> Path:
    frames = work / "frames"
    frames.mkdir()
    for i in range(20):
        rgb = bytes((30 + i * 8, 20, 15))
        (frames / f"{i:03d}.ppm").write_bytes(b"P6\n160 90\n255\n" + rgb * (160 * 90))
    out = work / "source.mp4"
    subprocess.run(
        ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
         "-framerate", "10", "-i", str(frames / "%03d.ppm"),
         "-c:v", "libx264", "-preset", "ultrafast", "-crf", "22",
         "-pix_fmt", "yuv420p", str(out)], check=True
    )
    return out


def validate_mp4(path: Path):
    data = json.loads(subprocess.check_output(
        ["ffprobe", "-v", "error", "-show_entries",
         "stream=codec_type,codec_name,nb_frames:format=duration",
         "-of", "json", str(path)], text=True
    ))
    streams = data["streams"]
    assert len(streams) == 1 and streams[0]["codec_type"] == "video", data
    assert streams[0]["codec_name"] == "h264", data
    assert 14 <= int(streams[0]["nb_frames"]) <= 16, data
    assert .9 <= float(data["format"]["duration"]) <= 1.1, data


def is_mt_isolated(page):
    try:
        return page.evaluate("""() =>
            globalThis.crossOriginIsolated === true &&
            typeof SharedArrayBuffer === 'function' &&
            Boolean(navigator.serviceWorker && navigator.serviceWorker.controller)
        """)
    except PlaywrightError:
        # The worker may cause the first /mt/ navigation to reload.
        return False


def main():
    assert (PAGES / "index.html").is_file(), "ST Pages output missing"
    assert (PAGES / "mt/index.html").is_file(), "MT Pages output missing"
    assert (PAGES / "mt/coi-serviceworker.js").is_file(), "COI worker missing"
    with tempfile.TemporaryDirectory(prefix="reverse-pages-coi-") as directory:
        source = fixture(Path(directory))
        server = ThreadingHTTPServer(("127.0.0.1", 0), PagesHandler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        base = f"http://127.0.0.1:{server.server_port}"
        try:
            with sync_playwright() as playwright:
                args = {"headless": True,
                        "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
                if os.getenv("CHROMIUM_EXE"):
                    args["executable_path"] = os.environ["CHROMIUM_EXE"]
                browser = playwright.chromium.launch(**args)
                try:
                    context = browser.new_context(viewport={"width": 390, "height": 844},
                        accept_downloads=True, service_workers="allow")
                    st = context.new_page()
                    response = st.goto(base + "/", wait_until="load", timeout=30000)
                    assert response and response.status == 200
                    assert st.evaluate("globalThis.crossOriginIsolated") is False
                    assert st.locator("#runtimeModeLabel").inner_text().find("ST") >= 0
                    assert st.evaluate("typeof SharedArrayBuffer") == "undefined"
                    print("[PASS] GitHub Pages ST root is available without isolation", flush=True)
                    st.close()

                    mt = context.new_page()
                    errors = []
                    mt.on("pageerror", lambda error: errors.append(str(error)))
                    response = mt.goto(base + "/mt/", wait_until="domcontentloaded", timeout=30000)
                    assert response and response.status == 200

                    # Give the same-origin worker time for first-install, claim
                    # and its first-visit reload. This must NOT rely on the
                    # local HTTP server setting COOP/COEP.
                    deadline = time.monotonic() + 12
                    while time.monotonic() < deadline and not is_mt_isolated(mt):
                        mt.wait_for_timeout(400)
                    if not is_mt_isolated(mt):
                        # On a fresh worker installation, coi-serviceworker
                        # sometimes becomes active after the initial registration
                        # reload callback. A user can refresh the MT page once.
                        mt.wait_for_function("""() =>
                            Boolean(navigator.serviceWorker?.controller)""", timeout=20000)
                        mt.reload(wait_until="domcontentloaded", timeout=30000)
                        deadline = time.monotonic() + 12
                        while time.monotonic() < deadline and not is_mt_isolated(mt):
                            mt.wait_for_timeout(400)
                        print("[INFO] MT isolation required one explicit page refresh", flush=True)
                    assert is_mt_isolated(mt), (
                        "GitHub Pages MT Service Worker failed to isolate /mt/ "
                        "even after registration and a refresh"
                    )
                    assert "MT" in mt.locator("#runtimeModeLabel").inner_text()
                    registrations = mt.evaluate("""async () =>
                        (await navigator.serviceWorker.getRegistrations())
                        .map(reg => new URL(reg.scope).pathname)""")
                    assert "/mt/" in registrations, registrations

                    mt.locator("#sourceInput").set_input_files(str(source))
                    mt.locator("#reversePanel").wait_for(state="visible", timeout=10000)
                    mt.locator("#rangeStart").fill("0")
                    mt.locator("#rangeStart").dispatch_event("change")
                    mt.locator("#rangeEnd").fill("1")
                    mt.locator("#rangeEnd").dispatch_event("change")
                    assert mt.locator("#reverseButton").is_enabled(), (
                        mt.locator("#rangeNotice").inner_text()
                    )
                    mt.locator("#reverseButton").click()
                    mt.wait_for_function("""() =>
                        !document.querySelector('#resultArea').hidden ||
                        !document.querySelector('#reverseErrorDetails').hidden""",
                        timeout=90000)
                    if mt.locator("#reverseErrorDetails").is_visible():
                        raise AssertionError(mt.locator("#reverseErrorDetail").inner_text())
                    with mt.expect_download(timeout=10000) as download:
                        mt.locator("#saveReverseButton").click()
                    saved = Path(directory) / "pages-mt-reversed.mp4"
                    download.value.save_as(saved)
                    validate_mp4(saved)
                    assert not errors, errors
                    print("[PASS] Pages MT first-visit COI worker and real reversed MP4",
                          flush=True)

                    # The /mt/ worker is scope-limited: root remains ST even
                    # after MT registration within the same browser context.
                    root = context.new_page()
                    response = root.goto(base + "/", wait_until="load", timeout=30000)
                    assert response and response.status == 200
                    assert root.evaluate("globalThis.crossOriginIsolated") is False
                    assert "ST" in root.locator("#runtimeModeLabel").inner_text()
                    print("[PASS] Pages ST remains unisolated after MT worker install",
                          flush=True)
                    context.close()
                finally:
                    browser.close()
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    main()
