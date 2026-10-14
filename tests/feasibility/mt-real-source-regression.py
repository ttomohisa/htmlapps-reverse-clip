#!/usr/bin/env python3
"""Reproduce source-specific MT 30->24 frame loss using sparse video timestamps.

Owner's input is H.264 High, 1920x1080, duration 37.806s,
r_frame_rate=13/4, avg_frame_rate=877500/850637 (~1.03fps),
time_base=1/90000. ST succeeded; MT missed 6 frames in a 2s segment.
This test synthesizes separate 320p/1080p 39-frame source files near
these properties, plus conventional and boundary-gap VFR controls.
Actual decoded MP4 exports are verified: never accept 24/30 by silently
relaxing the frame-count guard. No user video data is required.
"""
from __future__ import annotations

import argparse
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import tempfile
import threading
from playwright.sync_api import sync_playwright
from presentation_vfr_fixture import make_presentation_vfr_fixture

ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST), **kwargs)

    def end_headers(self):
        if self.path.split("?")[0] == "/index.mt.html":
            self.send_header("Cross-Origin-Opener-Policy", "same-origin")
            self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
            self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        super().end_headers()

    def log_message(self, *_):
        pass


def create_fixture(tmp: Path, name: str) -> Path:
    result = tmp / (name + ".mp4")
    sparse = name.startswith("sparse-slide-")
    size = "1920x1080" if name == "sparse-slide-1080" else "320x180"
    base = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-threads", "2",
        "-f", "lavfi", "-i",
        f"testsrc2=size={size}:rate=" +
        ("13/4" if sparse else
         "12" if name == "low-12fps" else "30000/1001") +
        ":duration=37.90",
    ]
    if sparse:
        # 39 H.264 High VFR frames in ~37.85s at 90k time base.
        # A closely matched reproduction of the user's metadata:
        # r_frame_rate=13/4, avg_frame_rate~1.03, plus x264 B-frames.
        # Keep a pair of adjacent timestamps and several long holds.
        base += ["-vf",
                 "select='eq(n,0)+eq(n,1)+eq(n,5)+"
                 "if(gte(n,10),not(mod(n,3))*not(eq(n,30))*not(eq(n,60)),0)'",
                 "-fps_mode", "vfr"]
    if name == "irregular-vfr":
        # Drop 1 of 5 source frames, preserving actual timestamps.
        base += ["-vf", "select='not(eq(mod(n,5),0))'", "-fps_mode", "vfr"]
    if name == "boundary-gap-vfr":
        # A camera/recorder that emits no frames for half a second near
        # the 2s chunk boundary; the ST path has processed this locally.
        # Decoder frame threading and filter EOF must not truncate output.
        base += ["-vf", "select='not(between(t,1.53,2.04))'", "-fps_mode", "vfr"]
    base += [
        "-map", "0:v:0", "-c:v", "libx264", "-preset", "veryfast",
        "-bf", "3", "-g", "60", "-crf", "37" if sparse else "29",
        "-pix_fmt", "yuv420p", "-profile:v", "high",
        "-video_track_timescale", "90000",
        "-movflags", "+faststart", str(result),
    ]
    subprocess.run(base, check=True, timeout=130)
    assert result.stat().st_size > 5000, result
    if sparse:
        info = json.loads(subprocess.check_output([
            "ffprobe", "-v", "error", "-select_streams", "v:0",
            "-show_entries",
            "stream=codec_name,profile,width,height,nb_frames,r_frame_rate,"
            "avg_frame_rate,time_base,start_time,duration",
            "-of", "json", str(result)], timeout=30))["streams"][0]
        assert info["codec_name"] == "h264" and info["profile"] == "High", info
        assert info["time_base"] == "1/90000" and info["r_frame_rate"] == "13/4", info
        assert int(info["nb_frames"]) == 39 and 37.7 < float(info["duration"]) < 38, info
        assert 1.0 < eval_fraction(info["avg_frame_rate"]) < 1.1, info
        print("[MATCHED SOURCE]", name, json.dumps(info), flush=True)
    return result


def eval_fraction(text: str) -> float:
    from fractions import Fraction
    return float(Fraction(text))


def transcode(page, source: Path, mode: str, label: str, temporary: Path,
             duration: float = 10):
    page.locator("#sourceInput").set_input_files(str(source))
    page.locator("#reversePanel").wait_for(state="visible", timeout=30000)
    page.locator("#qualityInput").select_option(
        "1280" if "sparse-slide-1080" in label or "pvm-webcodecs-1080" in label
        else "360")
    page.locator("#modeInput").select_option(mode)
    # Audio is already "none" by default; silent files intentionally disable
    # its selector, so Playwright must not wait for it to become enabled.
    assert page.locator("#audioInput").input_value() == "none"
    page.locator("#rangeStart").fill("0")
    page.locator("#rangeStart").dispatch_event("change")
    page.locator("#rangeEnd").fill(str(duration))
    page.locator("#rangeEnd").dispatch_event("change")
    assert page.locator("#reverseButton").is_enabled(), (
        label, page.locator("#rangeNotice").inner_text(),
        page.locator("#reverseStatus").inner_text())
    page.locator("#reverseButton").click()
    page.wait_for_function("""() =>
        !document.querySelector('#resultArea').hidden ||
        !document.querySelector('#reverseErrorDetails').hidden
    """, timeout=150000)
    if page.locator("#reverseErrorDetails").is_visible():
        raise AssertionError(
            f"Owner-like source {label} failed: "
            + page.locator("#reverseErrorDetail").inner_text())
    assert page.locator("#resultArea").is_visible(), label
    target = temporary / (label + ".mp4")
    with page.expect_download(timeout=15000) as download:
        page.locator("#saveReverseButton").click()
    download.value.save_as(target)
    metadata = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries",
        "stream=codec_type,codec_name,nb_frames:format=duration",
        "-of", "json", str(target)
    ], timeout=30))
    video = [s for s in metadata["streams"] if s.get("codec_type") == "video"]
    expected_source_frames = round(duration * 15)
    expected = 2*expected_source_frames-2 if mode == "pingpong" else expected_source_frames
    assert len(video) == 1 and video[0]["codec_name"] == "h264", metadata
    assert int(video[0]["nb_frames"]) == expected, metadata
    assert abs(float(metadata["format"]["duration"]) - expected / 15) < .08, metadata
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error", "-xerror",
                    "-i", str(target), "-map", "0:v:0", "-f", "null", "-"],
                   check=True, timeout=70, stdout=subprocess.DEVNULL)
    print("[PASS]", label, expected, "frames, real MP4 fully decoded", flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--phase", choices=("isolated", "repeat", "extended"),
        default="isolated",
        help="isolated: one browser per essential PVM test; repeat: three 720p-class"
             " 10s MT exports on one page; extended: legacy mixed-fixture endurance")
    args = parser.parse_args()
    assert (DIST / "index.html").is_file() and (DIST / "index.mt.html").is_file()
    with tempfile.TemporaryDirectory(prefix="reverse-mt-frames-") as temp:
        tmp = Path(temp)
        fixtures = {}
        if args.phase == "extended":
            fixtures = {name: create_fixture(tmp, name)
                        for name in ("cfr-2997", "irregular-vfr", "low-12fps",
                                     "boundary-gap-vfr", "sparse-slide-320",
                                     "sparse-slide-1080")}
        for size, label in (("320x180", "pvm-webcodecs-320"),
                            ("1920x1080", "pvm-webcodecs-1080")):
            f = make_presentation_vfr_fixture(tmp, size)
            info = json.loads(subprocess.check_output([
                "ffprobe", "-v", "error", "-select_streams", "v:0",
                "-show_entries", "stream=codec_name,profile,time_base,nb_frames,"
                "avg_frame_rate,duration", "-of", "json", str(f)],
                timeout=30))["streams"][0]
            assert info["codec_name"] == "h264" and info["profile"] == "High", info
            assert info["time_base"] == "1/90000" and int(info["nb_frames"]) == 39, info
            assert abs(float(info["duration"]) - 37.806089) < .00002, info
            assert abs(eval_fraction(info["avg_frame_rate"]) - 877500 / 850637) < .00001, info
            print("[MATCHED WEBCODECS TIMELINE]", label, info, flush=True)
            fixtures[label] = f

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_port}"
        launch = {"headless": True,
                  "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
        if os.environ.get("CHROMIUM_EXE"):
            launch["executable_path"] = os.environ["CHROMIUM_EXE"]

        def new_page(browser, runtime):
            page = browser.new_page(accept_downloads=True)
            path = "index.mt.html" if runtime == "MT" else "index.html"
            response = page.goto(f"{base}/{path}",
                                 wait_until="domcontentloaded", timeout=45000)
            assert response and response.status == 200, runtime
            isolated = page.evaluate("globalThis.crossOriginIsolated")
            assert isolated == (runtime == "MT"), (runtime, isolated)
            return page

        try:
            with sync_playwright() as pw:
                if args.phase == "isolated":
                    # Unrelated ST/MT conversions must not poison a fresh-user
                    # correctness result. Each case has a new Chrome process.
                    # The repeat phase independently examines accumulation.
                    cases = [
                        ("MT", "pvm-webcodecs-1080", "pingpong", 10),
                        ("MT", "pvm-webcodecs-1080", "reverse", 10),
                        ("MT", "pvm-webcodecs-320", "pingpong", 2),
                        ("ST", "pvm-webcodecs-1080", "pingpong", 10),
                        ("ST", "pvm-webcodecs-320", "pingpong", 2),
                    ]
                    for runtime, name, mode, duration in cases:
                        browser = pw.chromium.launch(**launch)
                        try:
                            page = new_page(browser, runtime)
                            transcode(page, fixtures[name], mode,
                                      f"{runtime}-{name}-{mode}-{duration}s-isolated",
                                      tmp, duration=duration)
                        finally:
                            browser.close()
                    print("[DONE] 5 isolated Chrome process PVM cases", flush=True)
                elif args.phase == "repeat":
                    # This is the explicit same-page memory/endurance gate:
                    # no reboot or hidden ST fallback, 3 real MT exports.
                    browser = pw.chromium.launch(**launch)
                    try:
                        page = new_page(browser, "MT")
                        for repeat in range(1, 4):
                            transcode(page, fixtures["pvm-webcodecs-1080"],
                                      "pingpong",
                                      f"MT-pvm-webcodecs-1080-pingpong-10s-repeat-{repeat}",
                                      tmp, duration=10)
                        print("[DONE] MT 3 successive 10s PVM exports", flush=True)
                    finally:
                        browser.close()
                else:
                    browser = pw.chromium.launch(**launch)
                    try:
                        for runtime in ("ST", "MT"):
                            page = new_page(browser, runtime)
                            try:
                                for source_name, fixture in fixtures.items():
                                    for mode in ("reverse", "pingpong"):
                                        durations = (2, 10) if source_name.startswith(
                                            "pvm-webcodecs-") else (10,)
                                        for duration in durations:
                                            transcode(page, fixture, mode,
                                                      f"{runtime}-{source_name}-{mode}-{duration}s",
                                                      tmp, duration=duration)
                            finally:
                                page.close()
                    finally:
                        browser.close()
                    print("[DONE] extended mixed-fixture endurance", flush=True)
        finally:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    main()
