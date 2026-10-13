#!/usr/bin/env python3
"""Opt-in v0.6 desktop HD endurance test against actual built standalone WASM.

Not a physical Android/iPhone measurement. Requires Chromium, Playwright,
ffmpeg and ffprobe. Builds reproducible 15fps 720p/1080p synthetic MP4 inputs,
downloads every output and checks exact frames/geometry/timing.
This test is intentionally NOT included in the regular PR CI: at 1080p it may
take many minutes and substantial RAM, particularly for single-thread WASM.
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
import time

from playwright.sync_api import sync_playwright

try:
    import psutil
except ImportError:
    psutil = None  # Optional process-tree RSS sampler; install to enable.


class MemorySampler:
    """Best-effort Chrome/Playwright subprocess RSS; NOT phone peak RAM.

    The aggregate may double-count shared pages and includes Playwright
    subprocesses. Use only for relative desktop regression investigations.
    """
    def __init__(self):
        self.peak = None
        self.stop_flag = threading.Event()
        self.worker = None

    def start(self):
        if psutil is None:
            return
        self.worker = threading.Thread(target=self._sample, daemon=True)
        self.worker.start()

    def _sample(self):
        parent = psutil.Process(os.getpid())
        while not self.stop_flag.is_set():
            total = 0
            for proc in parent.children(recursive=True):
                try:
                    total += proc.memory_info().rss
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            self.peak = max(self.peak or 0, total)
            self.stop_flag.wait(.25)

    def stop(self):
        self.stop_flag.set()
        if self.worker:
            self.worker.join(timeout=2)


ROOT = Path(__file__).resolve().parents[2]
DIST = ROOT / "dist"
FPS = 15
PROFILES = {"standard": (1280, 720, 10.0), "high": (1920, 1080, 5.0)}


class Handler(SimpleHTTPRequestHandler):
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


def make_input(directory: Path, profile: str, audio: bool) -> Path:
    w, h, seconds = PROFILES[profile]
    path = directory / f"v060-input-{profile}-{'aac' if audio else 'silent'}.mp4"
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-threads", "2",
        "-f", "lavfi", "-i", f"testsrc2=size={w}x{h}:rate={FPS}",
    ]
    if audio:
        cmd += ["-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000"]
    cmd += ["-t", str(seconds), "-c:v", "libx264", "-preset", "ultrafast",
            "-crf", "30", "-pix_fmt", "yuv420p", "-r", str(FPS)]
    if audio:
        cmd += ["-c:a", "aac", "-ar", "48000", "-ac", "2", "-b:a", "96k"]
    else:
        cmd += ["-an"]
    cmd.append(str(path))
    subprocess.run(cmd, check=True)
    return path


def probe_output(path: Path, profile: str, mode: str, audio: bool) -> dict:
    info = json.loads(subprocess.check_output([
        "ffprobe", "-v", "error", "-count_frames",
        "-show_entries",
        "stream=codec_type,codec_name,width,height,nb_read_frames:format=duration",
        "-of", "json", str(path)], text=True))
    video = [s for s in info["streams"] if s["codec_type"] == "video"]
    sound = [s for s in info["streams"] if s["codec_type"] == "audio"]
    w, h, seconds = PROFILES[profile]
    expected = round(seconds * FPS)
    if mode == "pingpong":
        expected = expected * 2 - 2
    assert len(video) == 1 and video[0]["codec_name"] == "h264", info
    assert (video[0]["width"], video[0]["height"]) == (w, h), info
    assert int(video[0]["nb_read_frames"]) == expected, info
    assert len(sound) == int(audio), info
    if audio:
        assert sound[0]["codec_name"] == "aac", info
    duration = float(info["format"]["duration"])
    assert abs(duration - expected / FPS) < .16, info
    # Force decoder to visit all frames, rather than trusting MP4 metadata.
    subprocess.run(["ffmpeg", "-hide_banner", "-loglevel", "error",
        "-xerror", "-i", str(path), "-map", "0:v:0", "-f", "null", "-"],
        check=True, stdout=subprocess.DEVNULL)
    return {"bytes": path.stat().st_size, "frames": expected,
            "width": w, "height": h, "duration": duration}


def set_range(page, seconds: float):
    page.locator("#rangeStart").fill("0")
    page.locator("#rangeStart").dispatch_event("change")
    page.locator("#rangeEnd").fill(str(seconds))
    page.locator("#rangeEnd").dispatch_event("change")


def run_profile(browser, base: str, directory: Path, runtime: str,
                profile: str, modes: list[str], runs: int, audio: bool,
                timeout_ms: int, cancel_retry: bool) -> list[dict]:
    html = "index.html" if runtime == "ST" else "index.mt.html"
    page = browser.new_page(viewport={"width": 390, "height": 844},
                            accept_downloads=True)
    errors, remote = [], []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on("request", lambda request: remote.append(request.url)
        if not request.url.startswith((base, "blob:", "data:")) else None)
    results = []
    try:
        response = page.goto(base + "/" + html, wait_until="domcontentloaded",
                             timeout=45000)
        assert response and response.status == 200
        assert bool(page.evaluate("crossOriginIsolated")) == (runtime == "MT")
        source = make_input(directory, profile, audio)
        page.locator("#sourceInput").set_input_files(str(source))
        page.locator("#reversePanel").wait_for(state="visible", timeout=30000)
        page.locator("#qualityInput").select_option(
            "1280" if profile == "standard" else "1920")
        set_range(page, PROFILES[profile][2])
        if audio:
            page.wait_for_function(
                "() => !document.querySelector('#audioReverseOption').disabled",
                timeout=timeout_ms)
            page.locator("#audioInput").select_option("reverse")
        else:
            assert page.locator("#audioInput").input_value() == "none"
        for mode in modes:
            page.locator("#modeInput").select_option(mode)
            for iteration in range(1, runs + 1):
                assert page.locator("#reverseButton").is_enabled(), (
                    runtime, profile, mode, page.locator("#rangeNotice").text_content())
                began = time.perf_counter()
                sampler = MemorySampler()
                sampler.start()
                try:
                    page.locator("#reverseButton").click()
                    page.wait_for_function("""() =>
                        !document.querySelector('#resultArea').hidden ||
                        !document.querySelector('#reverseErrorDetails').hidden
                    """, timeout=timeout_ms)
                finally:
                    sampler.stop()
                elapsed = time.perf_counter() - began
                if page.locator("#reverseErrorDetails").is_visible():
                    raise AssertionError(
                        "Conversion error: " +
                        (page.locator("#reverseErrorDetail").text_content() or "unknown"))
                with page.expect_download(timeout=15000) as download:
                    page.locator("#saveReverseButton").click()
                saved = directory / (
                    f"{runtime}-{profile}-{mode}-{'audio' if audio else 'silent'}"
                    f"-run{iteration}.mp4")
                download.value.save_as(str(saved))
                probe = probe_output(saved, profile, mode, audio)
                # Chrome-specific end-of-job JS heap only; NOT process peak RAM.
                heap = page.evaluate("""() => ({
                  available: !!performance.memory,
                  usedJSHeapSize: performance.memory?.usedJSHeapSize ?? null
                })""")
                item = {"runtime": runtime, "profile": profile, "mode": mode,
                    "audio": audio, "iteration": iteration,
                    "elapsedSeconds": round(elapsed, 2),
                    "jsHeapAfterBytes": heap["usedJSHeapSize"],
                    "sampledProcessTreePeakRssBytes": sampler.peak, **probe}
                results.append(item)
                print("[PASS]", json.dumps(item, ensure_ascii=False), flush=True)
            if cancel_retry:
                # Synchronous DOM clicks avoid Playwright's stability delay
                # hiding a cancellation race in short/fast conversions.
                page.evaluate("""() => {
                  document.querySelector('#reverseButton').click();
                  document.querySelector('#cancelReverseButton').click();
                }""")
                assert page.locator("#resultArea").is_hidden()
                assert page.locator("#saveReverseButton").is_hidden()
                assert page.locator("#reverseButton").is_enabled()
                # Recovery means a *real* subsequent MP4 must decode.
                page.locator("#reverseButton").click()
                page.wait_for_function("""() =>
                    !document.querySelector('#resultArea').hidden ||
                    !document.querySelector('#reverseErrorDetails').hidden
                """, timeout=timeout_ms)
                if page.locator("#reverseErrorDetails").is_visible():
                    raise AssertionError("Cancel recovery failed: " + (
                        page.locator("#reverseErrorDetail").text_content() or "unknown"))
                with page.expect_download(timeout=15000) as dl:
                    page.locator("#saveReverseButton").click()
                recovered = directory / (
                    f"{runtime}-{profile}-{mode}-recovery.mp4")
                dl.value.save_as(str(recovered))
                probe_output(recovered, profile, mode, audio)
                print("[PASS] cancel then retry produces decodable MP4",
                      runtime, profile, mode, flush=True)
        assert not errors, errors
        assert not remote, remote
    finally:
        page.close()
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=["standard", "high", "both"],
                        default="standard")
    parser.add_argument("--runtime", choices=["ST", "MT", "both"], default="ST")
    parser.add_argument("--mode", choices=["reverse", "pingpong", "both"],
                        default="both")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--audio", action="store_true")
    parser.add_argument("--cancel-retry", action="store_true")
    parser.add_argument("--timeout-ms", type=int, default=600000)
    parser.add_argument("--report", type=Path, default=None)
    args = parser.parse_args()
    if not 1 <= args.runs <= 10:
        parser.error("--runs must be 1–10")
    if not (DIST / "index.html").is_file() or not (DIST / "index.mt.html").is_file():
        parser.error("Build both pinned ST/MT standalone HTML variants first.")
    profiles = list(PROFILES) if args.profile == "both" else [args.profile]
    runtimes = ["ST", "MT"] if args.runtime == "both" else [args.runtime]
    modes = ["reverse", "pingpong"] if args.mode == "both" else [args.mode]

    with tempfile.TemporaryDirectory(prefix="reverse-v060-stress-") as temp:
        directory = Path(temp)
        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        base = f"http://127.0.0.1:{server.server_port}"
        try:
            with sync_playwright() as pw:
                options = {"headless": True,
                    "args": ["--no-sandbox", "--disable-dev-shm-usage"]}
                if os.getenv("CHROMIUM_EXE"):
                    options["executable_path"] = os.environ["CHROMIUM_EXE"]
                browser = pw.chromium.launch(**options)
                try:
                    measurements = []
                    for profile in profiles:
                        for runtime in runtimes:
                            measurements += run_profile(
                                browser, base, directory, runtime, profile,
                                modes, args.runs, args.audio,
                                args.timeout_ms, args.cancel_retry)
                finally:
                    browser.close()
        finally:
            server.shutdown()
            server.server_close()
    report = {"test": "desktop Chromium/Playwright; NOT mobile acceptance",
        "profiles": profiles, "runtimes": runtimes, "modes": modes,
        "repeatCount": args.runs, "aacAudio": args.audio,
        "peakDeviceRamMeasured": False,
        "estimatedProcessRssMethod": "psutil subtree RSS sampled every 250ms, may double-count shared pages"
            if psutil is not None else "not measured (psutil unavailable)",
        "results": measurements}
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print("[DONE]", len(measurements), "real decoded MP4 outputs",
          "(no phone/RSS acceptance claim)", flush=True)


if __name__ == "__main__":
    main()
