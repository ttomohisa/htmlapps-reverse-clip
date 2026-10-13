#!/usr/bin/env python3
"""Actual file:// standalone ST MP4 smoke, including self-extracting HTML.

This verifies the app's core offline promise, not a merely mocked app UI.
The video, JS, WASM, and output all stay local; no HTTP server is launched.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import tempfile

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"


def source_mp4(directory: Path) -> Path:
    output = directory / "local-input.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=10",
        "-t", "2", "-c:v", "libx264", "-preset", "ultrafast",
        "-crf", "28", "-pix_fmt", "yuv420p", str(output)
    ], check=True)
    return output


def validate(path: Path) -> None:
    metadata = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=codec_name,width,height,nb_frames:format=duration",
        "-of", "json", str(path)
    ], text=True))
    streams = metadata["streams"]
    assert len(streams) == 1 and streams[0]["codec_name"] == "h264", metadata
    assert 14 <= int(streams[0]["nb_frames"]) <= 16, metadata
    assert .9 <= float(metadata["format"]["duration"]) <= 1.1, metadata


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="reverse-st-file-smoke-") as tmp:
        src = source_mp4(Path(tmp))
        with sync_playwright() as pw:
            kwargs = {
                "headless": True,
                "args": ["--no-sandbox", "--disable-dev-shm-usage"]
            }
            if os.environ.get("CHROMIUM_EXE"):
                kwargs["executable_path"] = os.environ["CHROMIUM_EXE"]
            browser = pw.chromium.launch(**kwargs)
            try:
                for name in ("index.html", "index.self-extract.html"):
                    html = DIST / name
                    assert html.is_file() and html.stat().st_size > 100000
                    context = browser.new_context(
                        viewport={"width": 390, "height": 800},
                        accept_downloads=True
                    )
                    page = context.new_page()
                    errors: list[str] = []
                    remote: list[str] = []
                    page.on("pageerror", lambda e: errors.append(str(e)))
                    page.on("request", lambda req: remote.append(req.url)
                            if req.url.startswith(("http://", "https://")) else None)
                    page.goto(html.resolve().as_uri(), wait_until="domcontentloaded",
                              timeout=45000)
                    page.locator("#sourceInput").wait_for(timeout=20000)
                    assert page.evaluate("location.protocol") == "file:"
                    assert page.evaluate("globalThis.crossOriginIsolated") is False
                    assert "ST" in page.locator("#runtimeModeLabel").inner_text()
                    page.locator("#sourceInput").set_input_files(str(src))
                    page.locator("#reversePanel").wait_for(state="visible", timeout=15000)
                    page.locator("#rangeStart").fill("0")
                    page.locator("#rangeStart").dispatch_event("change")
                    page.locator("#rangeEnd").fill("1")
                    page.locator("#rangeEnd").dispatch_event("change")
                    assert page.locator("#reverseButton").is_enabled(), (
                        name, page.locator("#rangeNotice").inner_text()
                    )
                    page.locator("#reverseButton").click()
                    page.wait_for_function("""() =>
                      !document.querySelector('#resultArea').hidden ||
                      !document.querySelector('#reverseErrorDetails').hidden""",
                      timeout=90000)
                    if page.locator("#reverseErrorDetails").is_visible():
                        raise AssertionError(name + ": " +
                            page.locator("#reverseErrorDetail").inner_text())
                    with page.expect_download(timeout=15000) as download:
                        page.locator("#saveReverseButton").click()
                    output = Path(tmp) / (name + ".mp4")
                    download.value.save_as(output)
                    validate(output)
                    assert not errors, (name, errors)
                    assert not remote, (name, remote)
                    print(f"[PASS] direct file:// {name}: reversed H.264 MP4 saved offline",
                          flush=True)
                    context.close()
            finally:
                browser.close()


if __name__ == "__main__":
    main()
