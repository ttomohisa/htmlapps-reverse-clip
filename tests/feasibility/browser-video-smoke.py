#!/usr/bin/env python3
"""Opt-in offline Chromium regression for the actual embedded reverse WASM.

Use both CI-generated HTML variants. This script uses about:blank/page.set_content
because the test runner may block URL navigation; it is NOT a direct file:// test.
Needs Python playwright, Chromium, native ffmpeg/ffprobe; no network fixtures.
"""
import hashlib
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

def main():
    with tempfile.TemporaryDirectory(prefix="bk-reverse-10s-") as temp:
        temp = Path(temp)
        source = create_source(temp)
        with sync_playwright() as pw:
            options = dict(headless=True, args=["--no-sandbox", "--disable-dev-shm-usage"])
            if os.environ.get("CHROMIUM_EXE"):
                options["executable_path"] = os.environ["CHROMIUM_EXE"]
            browser = pw.chromium.launch(**options)
            checksums = []
            try:
                for variant, user_agent in (
                    ("index.html", None),
                    ("index.self-extract.html", ANDROID_UA)):
                    context = browser.new_context(
                        viewport={"width":390,"height":800},
                        accept_downloads=True, user_agent=user_agent)
                    page = context.new_page()
                    js_errors = []
                    network = []
                    page.on("pageerror", lambda e: js_errors.append(str(e)))
                    page.on("console", lambda m: js_errors.append(m.text)
                            if m.type == "error" else None)
                    page.on("request", lambda r: network.append(r.url))
                    page.set_content((DIST/variant).read_text(encoding="utf-8"),
                        wait_until="domcontentloaded", timeout=45000)
                    page.locator("#sourceInput").wait_for(timeout=15000)
                    page.locator("#sourceInput").set_input_files(str(source))
                    page.locator("#reversePanel").wait_for(state="visible", timeout=30000)
                    stem = variant.replace(".html", "")
                    checksum = test_conversion(page, temp, stem+"-10s", 0, 10, 150)
                    checksums.append(checksum)
                    if variant == "index.html":
                        # Repeating the same job must not carry stale result bytes.
                        repeated = test_conversion(page, temp, stem+"-10s-again", 0, 10, 150)
                        assert repeated == checksum
                        # Uneven duration and offset, 0.1..9.87 => 146 output frames.
                        test_conversion(page, temp, stem+"-fractional", 0.1, 9.87, 146)
                        # The original 5-second path must keep working.
                        test_conversion(page, temp, stem+"-5s", 0, 5, 75)
                        # Stop early: no incomplete MP4 may remain downloadable.
                        page.locator("#reverseButton").click()
                        page.locator("#cancelReverseButton").click()
                        page.wait_for_timeout(200)
                        assert page.locator("#resultArea").is_hidden()
                        assert not page.locator("#saveReverseButton").is_visible()
                    assert not page.evaluate("document.documentElement.scrollWidth > innerWidth")
                    assert not js_errors, js_errors
                    assert not [url for url in network
                        if url.startswith(("http://", "https://"))], network
                    print("PASS network/layout/JS", variant, flush=True)
                    context.close()
                assert checksums[0] == checksums[1], "HTML variants differ in 10s MP4"
            finally:
                browser.close()

if __name__ == "__main__":
    main()
