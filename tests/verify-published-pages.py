#!/usr/bin/env python3
"""Smoke the *published* GitHub Pages test: ST root and service-worker-isolated MT.

Runs only after a successful Pages deploy. Uses locally generated media and
requires Playwright Chrome plus native ffmpeg/ffprobe. Not a phone acceptance.
"""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import time
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright, Error as PlaywrightError
from presentation_vfr_fixture import make_presentation_vfr_fixture


def mt_is_ready(page):
    try:
        return page.evaluate("""() =>
            globalThis.crossOriginIsolated === true &&
            typeof SharedArrayBuffer === 'function' &&
            Boolean(navigator.serviceWorker?.controller)
        """)
    except PlaywrightError:
        # The pinned COI worker can trigger a first-visit reload.
        return False


def main():
    base = os.environ["PAGES_URL"].strip().rstrip("/")
    u = urlparse(base)
    assert u.scheme == "https" and u.hostname == "ttomohisa.github.io", base
    assert u.path.rstrip("/") == "/htmlapps-reverse-clip", base

    with tempfile.TemporaryDirectory(prefix="reverse-live-pages-") as tmp:
        source = Path(tmp) / "synthetic.mp4"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-f", "lavfi", "-i", "testsrc2=size=160x90:rate=15:duration=2",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24",
            "-pix_fmt", "yuv420p", str(source),
        ], check=True, timeout=40)
        with sync_playwright() as playwright:
            launch = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
            if os.environ.get("CHROMIUM_EXE"):
                launch["executable_path"] = os.environ["CHROMIUM_EXE"]
            browser = playwright.chromium.launch(**launch)
            context = browser.new_context(accept_downloads=True)
            errors = []
            external = []
            context.on("page", lambda p: p.on("pageerror", lambda e: errors.append(str(e))))
            try:
                root = context.new_page()
                response = root.goto(base + "/", wait_until="domcontentloaded", timeout=45000)
                assert response and response.status == 200
                assert root.evaluate("globalThis.crossOriginIsolated") is False
                assert "ST" in root.locator("#runtimeModeLabel").text_content()
                print("[PASS] Published root serves non-isolated ST", flush=True)

                mt = context.new_page()
                mt.on("request", lambda r: external.append(r.url)
                      if r.url.startswith(("https://", "http://")) and
                      urlparse(r.url).netloc != u.netloc else None)
                try:
                    response = mt.goto(base + "/mt/", wait_until="domcontentloaded", timeout=45000)
                    assert response and response.status == 200
                except PlaywrightError:
                    # Some browsers report navigation interruption on SW reload.
                    pass
                deadline = time.monotonic() + 50
                while time.monotonic() < deadline and not mt_is_ready(mt):
                    mt.wait_for_timeout(450)
                if not mt_is_ready(mt):
                    mt.reload(wait_until="domcontentloaded", timeout=30000)
                    deadline = time.monotonic() + 20
                    while time.monotonic() < deadline and not mt_is_ready(mt):
                        mt.wait_for_timeout(450)
                assert mt_is_ready(mt), "Live GitHub Pages /mt/ lacks service-worker isolation/SAB"
                assert "MT" in mt.locator("#runtimeModeLabel").text_content()
                print("[PASS] Published /mt/ has COI service worker, SAB, MT runtime", flush=True)

                mt.locator("#sourceInput").set_input_files(str(source))
                mt.locator("#reversePanel").wait_for(state="visible", timeout=30000)
                mt.locator("#rangeStart").fill("0")
                mt.locator("#rangeStart").dispatch_event("change")
                mt.locator("#rangeEnd").fill("1")
                mt.locator("#rangeEnd").dispatch_event("change")
                mt.locator("#qualityInput").select_option("360")
                mt.locator("#modeInput").select_option("reverse")
                assert mt.locator("#reverseButton").is_enabled(), mt.locator("#rangeNotice").inner_text()
                mt.locator("#reverseButton").click()
                mt.wait_for_function("""() =>
                    !document.querySelector('#resultArea').hidden ||
                    !document.querySelector('#reverseErrorDetails').hidden
                """, timeout=150000)
                if mt.locator("#reverseErrorDetails").is_visible():
                    raise AssertionError(mt.locator("#reverseErrorDetail").inner_text())
                with mt.expect_download(timeout=15000) as dl:
                    mt.locator("#saveReverseButton").click()
                output = Path(tmp) / "published-mt-output.mp4"
                dl.value.save_as(output)
                probe = json.loads(subprocess.check_output([
                    "ffprobe", "-v", "error", "-show_entries",
                    "stream=codec_type,codec_name,nb_frames:format=duration",
                    "-of", "json", str(output),
                ], timeout=30))
                videos = [s for s in probe["streams"] if s.get("codec_type") == "video"]
                assert len(videos) == 1 and videos[0]["codec_name"] == "h264", probe
                assert int(videos[0]["nb_frames"]) == 15, probe
                assert abs(float(probe["format"]["duration"]) - 1) <= .07, probe
                assert not external, ("Unexpected media uploads/network requests", external)
                assert not errors, ("Uncaught page errors", errors)
                print("[PASS] Published MT converts and downloads a 15-frame/1s H.264 MP4", flush=True)

                # This is the user-reported failure class: a Presentation
                # Video Maker/WebCodecs-style H.264 High track stores 39
                # variable-duration samples across 37.806089 seconds.
                # Older WAsm decoded the 0.067s-start return chunk as 9/28
                # frames. Enforce 30 forward + 28 return, not an incomplete
                # silently padded output or a hidden ST downgrade.
                sparse = make_presentation_vfr_fixture(Path(tmp), "320x180")
                mt.locator("#sourceInput").set_input_files(str(sparse))
                mt.locator("#reversePanel").wait_for(state="visible", timeout=30000)
                mt.locator("#qualityInput").select_option("360")
                mt.locator("#modeInput").select_option("pingpong")
                mt.locator("#rangeStart").fill("0")
                mt.locator("#rangeStart").dispatch_event("change")
                mt.locator("#rangeEnd").fill("2")
                mt.locator("#rangeEnd").dispatch_event("change")
                assert mt.locator("#reverseButton").is_enabled(), mt.locator("#rangeNotice").inner_text()
                mt.locator("#reverseButton").click()
                mt.wait_for_function("""() =>
                    !document.querySelector('#resultArea').hidden ||
                    !document.querySelector('#reverseErrorDetails').hidden
                """, timeout=150000)
                if mt.locator("#reverseErrorDetails").is_visible():
                    raise AssertionError("Published MT sparse-VFR regression: " +
                                         mt.locator("#reverseErrorDetail").inner_text())
                assert mt.locator("#resultArea").is_visible()
                with mt.expect_download(timeout=15000) as sparse_dl:
                    mt.locator("#saveReverseButton").click()
                sparse_out = Path(tmp) / "published-mt-sparse-pingpong.mp4"
                sparse_dl.value.save_as(sparse_out)
                sparse_info = json.loads(subprocess.check_output([
                    "ffprobe", "-v", "error", "-show_entries",
                    "stream=codec_type,codec_name,nb_frames:format=duration",
                    "-of", "json", str(sparse_out)
                ], timeout=30))
                v = [stream for stream in sparse_info["streams"]
                     if stream.get("codec_type") == "video"]
                assert len(v) == 1 and v[0]["codec_name"] == "h264", sparse_info
                assert int(v[0]["nb_frames"]) == 58, sparse_info
                assert abs(float(sparse_info["format"]["duration"]) - 58/15) < .08, sparse_info
                subprocess.run(["ffmpeg", "-v", "error", "-xerror",
                                "-i", str(sparse_out), "-map", "0:v:0",
                                "-f", "null", "-"], check=True,
                               timeout=30, stdout=subprocess.DEVNULL)
                assert not external and not errors, (external, errors)
                print("[PASS] Published real MT sparse-VFR 37.806s/39-sample"
                      " input: 30+28 = 58 frames, 2s Ping-pong, fully decoded", flush=True)

                # Verify the same page can create a longer 10-second
                # low-fps ping-pong immediately after the 2s case. This
                # catches some per-segment/shared-WASM memory exhaustion.
                mt.locator("#rangeEnd").fill("10")
                mt.locator("#rangeEnd").dispatch_event("change")
                assert mt.locator("#reverseButton").is_enabled()
                mt.locator("#reverseButton").click()
                mt.wait_for_function("""() =>
                    !document.querySelector('#resultArea').hidden ||
                    !document.querySelector('#reverseErrorDetails').hidden
                """, timeout=180000)
                if mt.locator("#reverseErrorDetails").is_visible():
                    raise AssertionError("Published 10s MT sparse-video failure: "
                                         + mt.locator("#reverseErrorDetail").inner_text())
                with mt.expect_download(timeout=15000) as dl_long:
                    mt.locator("#saveReverseButton").click()
                long_out = Path(tmp) / "published-mt-sparse-10s.mp4"
                dl_long.value.save_as(long_out)
                long_data = json.loads(subprocess.check_output([
                    "ffprobe", "-v", "error", "-show_entries",
                    "stream=codec_type,codec_name,nb_frames:format=duration",
                    "-of", "json", str(long_out),
                ], timeout=30))
                stream = [entry for entry in long_data["streams"]
                          if entry.get("codec_type") == "video"]
                assert len(stream) == 1 and stream[0]["codec_name"] == "h264", long_data
                assert int(stream[0]["nb_frames"]) == 298, long_data
                assert abs(float(long_data["format"]["duration"]) - 298 / 15) < .08, long_data
                subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-xerror",
                                "-i", str(long_out), "-map", "0:v:0",
                                "-f", "null", "-"], check=True,
                               timeout=60, stdout=subprocess.DEVNULL)
                assert not external and not errors, (external, errors)
                print("[PASS] Published genuine MT 10s sparse slide pingpong:"
                      " 298 H.264 frames fully decoded after 2s output", flush=True)

                root.reload(wait_until="domcontentloaded", timeout=30000)
                assert root.evaluate("globalThis.crossOriginIsolated") is False, "MT worker isolation leaked to ST root"
            finally:
                context.close()
                browser.close()


if __name__ == "__main__":
    main()
