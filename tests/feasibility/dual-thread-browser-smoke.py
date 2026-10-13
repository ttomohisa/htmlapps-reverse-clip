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
                        assert ("MT" if mode == "multi-thread" else "ST") in page.locator("#runtimeModeLabel").text_content()
                        page.locator("#sourceInput").set_input_files(str(source))
                        page.locator("#reversePanel").wait_for(state="visible", timeout=10000)
                        assert page.locator("#reverseFilename").input_value() == "source-reverse", mode
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

                        # v0.3.0: both real range handles control the numeric
                        # fields, keyboard arrows, highlighted selection and
                        # the *source* playback interval. No false reverse
                        # preview prior to creating the final video.
                        assert page.locator("#trimStartSlider").is_enabled()
                        assert page.locator("#trimEndSlider").is_enabled()
                        page.locator("#rangeStart").fill("0.5")
                        page.locator("#rangeStart").dispatch_event("change")
                        page.locator("#rangeEnd").fill("1.5")
                        page.locator("#rangeEnd").dispatch_event("change")
                        assert page.locator("#trimStartSlider").input_value() == "0.5"
                        assert page.locator("#trimEndSlider").input_value() == "1.5"
                        page.locator("#trimStartSlider").focus()
                        page.keyboard.press("ArrowRight")
                        assert abs(float(page.locator("#rangeStart").input_value())-.6)<.0001
                        page.keyboard.press("ArrowLeft")
                        assert abs(float(page.locator("#rangeStart").input_value())-.5)<.0001
                        page.locator("#trimEndSlider").focus()
                        page.keyboard.press("ArrowLeft")
                        assert abs(float(page.locator("#rangeEnd").input_value())-1.4)<.0001
                        page.keyboard.press("ArrowRight")
                        assert abs(float(page.locator("#rangeEnd").input_value())-1.5)<.0001
                        assert page.locator("#trimSelectedTrack").evaluate(
                          "el => parseFloat(el.style.width)") > 0

                        page.locator("#previewSelectionButton").click()
                        page.wait_for_function("""() => {
                          const v=document.querySelector('#sourceVideo');
                          return v.paused && v.currentTime>=1.45 && v.currentTime<=1.6;
                        }""",timeout=15000)
                        assert page.locator("#reverseButton").is_enabled()
                        page.locator("#reverseButton").click()
                        page.wait_for_function("""() =>
                          !document.querySelector('#resultArea').hidden ||
                          !document.querySelector('#reverseErrorDetails').hidden""",
                          timeout=90000)
                        if page.locator("#reverseErrorDetails").is_visible():
                            raise AssertionError(f"{mode} selected middle: " +
                                page.locator("#reverseErrorDetail").inner_text())
                        page.locator("#reverseFilename").fill("my-selected-part")
                        with page.expect_download(timeout=15000) as middle_download:
                            page.locator("#saveReverseButton").click()
                        assert middle_download.value.suggested_filename == "my-selected-part.mp4"
                        middle = Path(temp) / f"{mode}-middle-selection.mp4"
                        middle_download.value.save_as(middle)
                        validate_mp4(middle)
                        red = subprocess.check_output(
                            ["ffmpeg","-v","error","-i",str(middle),
                             "-vf","scale=1:1:flags=neighbor,format=rgb24",
                             "-f","rawvideo","-pix_fmt","rgb24","pipe:1"])
                        assert len(red)//3 == 15
                        assert red[0] > red[-3]+12, "middle section did not reverse actual frame order"
                        print(f"[PASS] {mode} v0.3 trim handles / keyboard / source preview / actual middle reversed MP4",
                              flush=True)

                        # End-of-file interval: the closed start and half-open
                        # end must render one second, never an extra tail frame.
                        page.locator("#rangeStart").fill("1.0")
                        page.locator("#rangeStart").dispatch_event("change")
                        page.locator("#rangeEnd").fill("2.0")
                        page.locator("#rangeEnd").dispatch_event("change")
                        page.locator("#reverseButton").click()
                        page.wait_for_function("""() =>
                          !document.querySelector('#resultArea').hidden ||
                          !document.querySelector('#reverseErrorDetails').hidden""",
                          timeout=90000)
                        if page.locator("#reverseErrorDetails").is_visible():
                            raise AssertionError(f"{mode} selected tail: " +
                                page.locator("#reverseErrorDetail").inner_text())
                        with page.expect_download(timeout=15000) as tail_download:
                            page.locator("#saveReverseButton").click()
                        tail=Path(temp) / f"{mode}-tail-selection.mp4"
                        tail_download.value.save_as(tail)
                        validate_mp4(tail)
                        print(f"[PASS] {mode} v0.3 clip ending exactly at source end",flush=True)

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
                        assert page.locator("#reverseFilename").input_value() == "hd-source-reverse", mode
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
                        assert "MP4/MOV" in page.locator("#loadStatus").inner_text(), mode
                        assert page.locator("#resultArea").is_hidden(), mode

                        # A plausible ftyp atom alone is insufficient: the
                        # browser decoder must still accept the video itself.
                        page.locator("#sourceInput").set_input_files({
                            "name": "fake-codec.mov", "mimeType": "video/quicktime",
                            "buffer": b"\x00\x00\x00\x18ftypisom" + b"\x00" * 24
                        })
                        page.locator("#loadStatus[data-phase='error']").wait_for(timeout=10000)
                        assert page.locator("#reversePanel").is_hidden(), mode

                        # Delayed reads from an old input cannot reactivate it.
                        page.evaluate("""() => {
                          window.__oldSlice = Blob.prototype.slice;
                          window.__lateSourceResolve = null;
                          Blob.prototype.slice = function(...args) {
                            if (this instanceof File &&
                                ['stale.mp4', 'hanging.mp4', 'cancelled.mp4'].includes(this.name))
                              return {arrayBuffer:()=>new Promise(resolve=>{
                                if(this.name==='stale.mp4')
                                  window.__lateSourceResolve=resolve;
                              })};
                            return window.__oldSlice.apply(this,args);
                          };
                        }""")
                        page.locator("#sourceInput").set_input_files({
                            "name":"stale.mp4", "mimeType":"video/mp4",
                            "buffer": b"\x00\x00\x00\x18ftypisom" + b"\x00" * 12
                        })
                        assert page.locator("#loadStatus").get_attribute("data-phase") == "inspecting"
                        page.locator("#sourceInput").set_input_files(str(source))
                        page.locator("#loadStatus[data-phase='ready']").wait_for(timeout=10000)
                        page.evaluate("""() => window.__lateSourceResolve(
                          new Uint8Array([0,0,0,24,102,116,121,112,105,115,111,109,
                            0,0,0,0,105,115,111,109,105,115,111,109]).buffer)""")
                        assert page.locator("#loadStatus").get_attribute("data-phase") == "ready"
                        assert page.locator("#sourceName").inner_text() == source.name
                        print(f"[PASS] {mode} old file inspection cannot replace the new source",
                              flush=True)

                        # Simulate a cloud/photo provider that never answers.
                        # The production 30s source timer is shortened only
                        # inside the test to keep the suite inexpensive.
                        page.evaluate("""() => {
                          window.__realTimeout = window.setTimeout;
                          window.setTimeout=(callback, delay, ...args)=>
                            window.__realTimeout(callback,delay===30000?350:delay,...args);
                        }""")
                        page.locator("#sourceInput").set_input_files({
                            "name": "hanging.mp4", "mimeType": "video/mp4",
                            "buffer": b"\x00\x00\x00\x18ftypisom" + b"\x00" * 12
                        })
                        page.locator("#loadStatus[data-phase='error']").wait_for(timeout=5000)
                        assert page.locator("#reversePanel").is_hidden(), mode
                        assert page.locator("#resultArea").is_hidden(), mode
                        page.locator("#languageButton").click()
                        assert page.locator("#loadStatus").get_attribute("data-phase") == "error"
                        assert len(page.locator("#loadStatus").inner_text()) > 10
                        page.locator("#languageButton").click()
                        page.evaluate("() => { window.setTimeout = window.__realTimeout }")
                        print(f"[PASS] {mode} stalled source loading times out",
                              flush=True)

                        # A user must be able to cancel a provider read without
                        # waiting for the automatic 30-second timeout.
                        page.locator("#sourceInput").set_input_files({
                            "name": "cancelled.mp4", "mimeType": "video/mp4",
                            "buffer": b"\x00\x00\x00\x18ftypisom" + b"\x00" * 12
                        })
                        assert page.locator("#cancelLoadButton").is_visible(), mode
                        page.locator("#cancelLoadButton").click()
                        assert page.locator("#loadStatus").get_attribute("data-phase") == "empty"
                        assert page.locator("#cancelLoadButton").is_hidden(), mode
                        assert page.locator("#reversePanel").is_hidden(), mode
                        assert page.locator("#resultArea").is_hidden(), mode
                        page.evaluate("() => { Blob.prototype.slice = window.__oldSlice }")
                        print(f"[PASS] {mode} user-cancelled provider read cannot leave stale results",
                              flush=True)

                        page.locator("#sourceInput").set_input_files(str(source))
                        page.locator("#loadStatus[data-phase='ready']").wait_for(timeout=10000)
                        assert page.locator("#reversePanel").is_visible(), mode
                        assert page.locator("#reverseButton").is_enabled(), mode

                        # The app accepts only one source. Two files dropped at
                        # once must be rejected rather than silently using the
                        # first file and discarding the second without warning.
                        page.evaluate("""() => {
                          const dt = new DataTransfer();
                          dt.items.add(new File(['one'], 'one.mp4', {type:'video/mp4'}));
                          dt.items.add(new File(['two'], 'two.mp4', {type:'video/mp4'}));
                          document.querySelector('#dropZone').dispatchEvent(
                            new DragEvent('drop',{bubbles:true,cancelable:true,dataTransfer:dt}));
                        }""")
                        assert page.locator("#loadStatus").get_attribute("data-phase") == "error"
                        assert page.locator("#resultArea").is_hidden(), mode
                        assert page.locator("#reversePanel").is_hidden(), mode
                        page.locator("#sourceInput").set_input_files(str(source))
                        page.locator("#loadStatus[data-phase='ready']").wait_for(timeout=10000)
                        print(f"[PASS] {mode} multiple dropped files rejected; valid source restored",
                              flush=True)
                        print(f"[PASS] {mode} Foundation lifecycle rejects/replaces invalid media",
                              flush=True)

                        # Foundation layout accepts narrow portrait phones
                        # as well as the default 390px viewport and desktop.
                        for viewport_width in (320, 360, 390, 1024):
                            page.set_viewport_size({"width": viewport_width, "height": 780})
                            assert page.evaluate(
                                "document.documentElement.scrollWidth <= innerWidth"
                            ), (mode, viewport_width)
                        # The provided icon must be shared by the favicon and
                        # brand image. The header describes the app, not ST/MT.
                        assert page.locator("link[rel=icon]").get_attribute("href") == \
                            page.locator("#appBrandIcon").get_attribute("src")
                        assert "ST/MT" not in page.locator(".brand-meta").inner_text()
                        assert " · " not in page.locator(".brand-meta").inner_text()

                        # The language-toggle text must be JA rather than 日本語,
                        # independent of which locale the test browser starts in.
                        first_label=page.locator("#languageButton").inner_text()
                        page.locator("#languageButton").click()
                        second_label=page.locator("#languageButton").inner_text()
                        assert {first_label,second_label} == {"JA","EN"}
                        assert page.locator(".local-badge span").inner_text() in (
                            "完全ローカル処理","Fully local processing")
                        page.locator("#languageButton").click()

                        # Both explicit Close and Escape must unlock the
                        # background while leaving the dialog body scrollable.
                        before_y=page.evaluate("""() => {
                          document.documentElement.style.scrollBehavior='auto';
                          window.scrollTo(0,document.documentElement.scrollHeight);
                          return window.scrollY;
                        }""")
                        page.locator("#helpButton").click()
                        assert page.locator("#helpDialog").is_visible()
                        assert page.evaluate("""() =>
                          document.body.classList.contains('help-modal-open') &&
                          document.documentElement.classList.contains('help-modal-open') &&
                          getComputedStyle(document.body).position==='fixed'""")
                        assert page.locator("#helpDialog .dialog-body").evaluate(
                            "el => el.scrollHeight >= el.clientHeight")
                        page.locator("#closeHelpButton").click()
                        page.wait_for_function("() => !document.querySelector('#helpDialog').open")
                        after_y=page.evaluate("window.scrollY")
                        assert abs(after_y-before_y)<=2,(mode,before_y,after_y)
                        page.locator("#helpButton").click()
                        page.keyboard.press("Escape")
                        page.wait_for_function("() => !document.querySelector('#helpDialog').open")
                        assert not page.evaluate("document.body.classList.contains('help-modal-open')")
                        print(f"[PASS] {mode} JA/EN, supplied icon and help scroll locking",flush=True)

                        assert not errors, (mode, errors)
                        assert not external, (mode, external)
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
