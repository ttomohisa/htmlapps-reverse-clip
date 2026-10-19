#!/usr/bin/env python3
"""Validate actual Cloudflare PR Preview MT isolation and a downloaded real MP4."""
import json
import os
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright


def main():
    root = os.environ["PREVIEW_URL"].strip().rstrip("/")
    parsed = urlparse(root)
    assert parsed.scheme == "https" and parsed.hostname.endswith(".workers.dev"), root
    with tempfile.TemporaryDirectory(prefix="reverse-live-mt-") as tmp:
        source = Path(tmp) / "synthetic.mp4"
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "lavfi",
            "-i", "testsrc2=size=160x90:rate=15:duration=2",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "24",
            "-pix_fmt", "yuv420p", str(source)
        ], check=True, timeout=40)
        with sync_playwright() as pw:
            kwargs = {"headless": True, "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
            if os.environ.get("CHROMIUM_EXE"):
                kwargs["executable_path"] = os.environ["CHROMIUM_EXE"]
            browser = pw.chromium.launch(**kwargs)
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            errors, external = [], []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.on("request", lambda r: external.append(r.url)
                    if r.url.startswith(("https://", "http://"))
                    and urlparse(r.url).netloc != parsed.netloc else None)
            try:
                response = page.goto(root + "/", wait_until="domcontentloaded", timeout=45000)
                assert response and response.status == 200, "Preview ST root did not return 200"
                assert not page.evaluate("globalThis.crossOriginIsolated"), "ST root was unexpectedly isolated"
                assert 'const RUNTIME_VARIANT = "single-thread";' in response.text(), "Wrong ST variant"
                print("[PASS] Deployed Preview ST is not cross-origin isolated", flush=True)

                response = page.goto(root + "/index.mt.html", wait_until="domcontentloaded", timeout=45000)
                assert response and response.status == 200, "Preview MT entry did not return 200"
                headers = {k.lower(): v.lower() for k, v in response.headers.items()}
                for key, value in (
                    ("cross-origin-opener-policy", "same-origin"),
                    ("cross-origin-embedder-policy", "require-corp"),
                    ("cross-origin-resource-policy", "same-origin"),
                ):
                    assert headers.get(key) == value, ("Wrong MT response header", key, headers.get(key))
                assert 'const RUNTIME_VARIANT = "multi-thread";' in response.text(), "Wrong MT variant"
                assert page.evaluate("globalThis.crossOriginIsolated === true"), "MT page is not isolated"
                assert page.evaluate("typeof SharedArrayBuffer === 'function'"), "MT page has no SAB"
                print("[PASS] Deployed Cloudflare MT: COOP+COEP+CORP+SAB+crossOriginIsolated", flush=True)

                page.locator("#sourceInput").set_input_files(str(source))
                page.locator("#reversePanel").wait_for(state="visible", timeout=30000)
                page.locator("#rangeStart").fill("0")
                page.locator("#rangeStart").dispatch_event("change")
                page.locator("#rangeEnd").fill("1")
                page.locator("#rangeEnd").dispatch_event("change")
                page.locator("#qualityInput").select_option("360")
                page.locator("#modeInput").select_option("reverse")
                assert page.locator("#reverseButton").is_enabled(), page.locator("#rangeNotice").inner_text()
                page.locator("#reverseButton").click()
                page.wait_for_function("""() =>
                    !document.querySelector('#resultArea').hidden ||
                    !document.querySelector('#reverseErrorDetails').hidden
                """, timeout=150000)
                if page.locator("#reverseErrorDetails").is_visible():
                    raise AssertionError(page.locator("#reverseErrorDetail").inner_text())
                assert page.locator("#resultArea").is_visible()
                with page.expect_download(timeout=15000) as download:
                    page.locator("#saveReverseButton").click()
                saved = Path(tmp) / "cloudflare-mt-output.mp4"
                download.value.save_as(saved)
                info = json.loads(subprocess.check_output([
                    "ffprobe", "-v", "error", "-show_entries",
                    "stream=codec_type,codec_name,nb_frames:format=duration",
                    "-of", "json", str(saved)
                ], timeout=30))
                videos = [s for s in info["streams"] if s.get("codec_type") == "video"]
                assert len(videos) == 1 and videos[0]["codec_name"] == "h264", info
                assert int(videos[0]["nb_frames"]) == 15, info
                assert abs(float(info["format"]["duration"]) - 1) <= .07, info
                assert not errors, ("Browser page errors", errors)
                assert not external, ("External requests", external)
                print("[PASS] Deployed isolated MT created and saved H.264 MP4, 15 frames / 1s", flush=True)
            finally:
                context.close()
                browser.close()


if __name__ == "__main__":
    main()
