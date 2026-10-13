#!/usr/bin/env python3
"""Actual ST/MT Chrome ping-pong MP4 acceptance, gated by locked Builder bytes.

Unlike a timeline-math-only test, the enabled path performs real WASM
encode/remux, browser preview, MP4 download, ffprobe and decoded frame-order
checks. Until an approved runtime is SHA-pinned, both UIs must stay disabled.
This is desktop Chrome, never physical Android acceptance.
"""
from __future__ import annotations

import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import tempfile
import threading

from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
DIST=ROOT/"dist"
LOCK=json.loads((ROOT/"reverse-runtime.lock.json").read_text())
ENABLED="pingpong" in LOCK.get("features", [])


class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,directory=str(DIST),**kwargs)

    def end_headers(self):
        if self.path.split("?")[0]=="/index.mt.html":
            self.send_header("Cross-Origin-Opener-Policy","same-origin")
            self.send_header("Cross-Origin-Embedder-Policy","require-corp")
            self.send_header("Cross-Origin-Resource-Policy","same-origin")
        super().end_headers()

    def log_message(self,*args):
        pass


def source_fixture(directory:Path, frames=45)->Path:
    images=directory/"markers"
    images.mkdir()
    for i in range(frames):
        rgb=bytes((20+i*5,18,15))
        (images/f"{i:03}.ppm").write_bytes(b"P6\n160 90\n255\n"+rgb*(160*90))
    target=directory/"marker-15fps.mp4"
    subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error",
        "-framerate","15","-i",str(images/"%03d.ppm"),"-c:v","libx264",
        "-preset","ultrafast","-crf","18","-pix_fmt","yuv420p",str(target)],check=True)
    return target


def long_fixture(directory:Path)->Path:
    target=directory/"long-15fps.mp4"
    subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error",
        "-f","lavfi","-i","testsrc2=size=160x90:rate=15","-t","12",
        "-c:v","libx264","-preset","ultrafast","-crf","24",
        "-pix_fmt","yuv420p",str(target)],check=True)
    return target


def verify_mp4(path:Path, expected_frames:int,ordered_indices=None):
    report=json.loads(subprocess.check_output([
      "ffprobe","-v","error","-show_entries",
      "stream=codec_type,codec_name,nb_frames:format=duration",
      "-of","json",str(path)],text=True))
    assert len(report["streams"])==1,report
    assert report["streams"][0]["codec_type"]=="video",report
    assert report["streams"][0]["codec_name"]=="h264",report
    assert int(report["streams"][0]["nb_frames"])==expected_frames,report
    assert abs(float(report["format"]["duration"])-expected_frames/15)<.07,report
    if ordered_indices is not None:
        raw=subprocess.check_output(["ffmpeg","-v","error","-i",str(path),
          "-vf","scale=1:1:flags=neighbor,format=rgb24","-fps_mode",
          "passthrough","-f","rawvideo","-pix_fmt","rgb24","pipe:1"])
        measured=list(raw[::3])
        assert len(measured)==expected_frames,(len(measured),expected_frames)
        expected=[20+5*i for i in ordered_indices]
        assert all(abs(v-e)<=14 for v,e in zip(measured,expected)),list(zip(measured,expected))
        first=len(ordered_indices)//2+1
        assert measured[first-1]>measured[first]+2,(measured[first-1],measured[first])
        assert measured[-1]>measured[0]+2,(measured[-1],measured[0])


def export(page, directory,mode,start,end,expected_frames,indices=None):
    page.locator("#rangeStart").fill(str(start))
    page.locator("#rangeStart").dispatch_event("change")
    page.locator("#rangeEnd").fill(str(end))
    page.locator("#rangeEnd").dispatch_event("change")
    assert page.locator("#reverseButton").is_enabled(),page.locator("#rangeNotice").inner_text()
    page.locator("#reverseButton").click()
    page.wait_for_function("""() =>
      !document.querySelector('#resultArea').hidden ||
      !document.querySelector('#reverseErrorDetails').hidden""",timeout=150000)
    if page.locator("#reverseErrorDetails").is_visible():
        raise AssertionError("pingpong "+mode+" failed: "+
           page.locator("#reverseErrorDetail").inner_text())
    assert page.locator("#resultInfo").inner_text()
    actual=page.locator("#resultVideo").evaluate("(v)=>v.duration")
    assert abs(actual-expected_frames/15)<.09,(actual,expected_frames)
    with page.expect_download(timeout=15000) as d:
        page.locator("#saveReverseButton").click()
    assert d.value.suggested_filename.endswith("-pingpong.mp4"),d.value.suggested_filename
    path=Path(directory)/f"{mode}-{expected_frames}.mp4"
    d.value.save_as(path)
    verify_mp4(path,expected_frames,indices)
    print(f"[PASS] {mode}: real ping-pong {expected_frames} frames, saved and inspected",flush=True)


def main():
    with tempfile.TemporaryDirectory(prefix="reverse-pingpong-smoke-") as temp:
        directory=Path(temp)
        short=source_fixture(directory)
        long=long_fixture(directory)
        server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        base=f"http://127.0.0.1:{server.server_port}"
        try:
            with sync_playwright() as pw:
                kw={"headless":True,"args":["--no-sandbox","--disable-dev-shm-usage"]}
                if os.getenv("CHROMIUM_EXE"):kw["executable_path"]=os.environ["CHROMIUM_EXE"]
                browser=pw.chromium.launch(**kw)
                try:
                    for mode,html in (("ST","index.html"),("MT","index.mt.html")):
                        page=browser.new_page(accept_downloads=True,
                          viewport={"width":390,"height":844})
                        errors,external=[],[]
                        page.on("pageerror",lambda e: errors.append(str(e)))
                        page.on("request",lambda r:external.append(r.url)
                           if not r.url.startswith((base,"blob:","data:")) else None)
                        response=page.goto(base+"/"+html,wait_until="domcontentloaded")
                        assert response and response.status==200
                        assert page.evaluate("globalThis.crossOriginIsolated")== (mode=="MT")
                        page.locator("#sourceInput").set_input_files(str(short))
                        page.locator("#reversePanel").wait_for(state="visible",timeout=20000)
                        assert page.evaluate("() => typeof PINGPONG_ENABLED === 'undefined'") is True, \
                          "feature gate should be lexical, not a global mutable variable"
                        unlocked=page.locator("#pingpongOption").is_enabled()
                        assert unlocked==ENABLED,(mode,unlocked,ENABLED)
                        if not ENABLED:
                            assert page.locator("#modeInput").is_disabled()
                            print(f"[PASS] {mode}: old pinned runtime cannot execute ping-pong",flush=True)
                            page.close()
                            continue

                        assert page.locator("#modeInput").is_enabled(),mode
                        assert page.locator("#reverseFilename").input_value()=="marker-15fps-reverse"
                        page.locator("#modeInput").select_option("pingpong")
                        assert page.locator("#reverseFilename").input_value()=="marker-15fps-pingpong"
                        assert "ping" in page.locator("#reverseButton").inner_text().lower() or \
                               "往復" in page.locator("#reverseButton").inner_text()

                        # N=15 => 0..14,13..1 : 28 output frames
                        # source range .4..1.4 is exactly frames 6..20.
                        indices=list(range(6,21))+list(range(19,6,-1))
                        export(page,directory,mode,.4,1.4,28,indices)

                        # Changing conversion mode discards the old result,
                        # while preserving names intentionally edited by users.
                        page.locator("#reverseFilename").fill("personal-name")
                        page.locator("#modeInput").select_option("reverse")
                        assert page.locator("#resultArea").is_hidden()
                        assert page.locator("#reverseFilename").input_value()=="personal-name"
                        page.locator("#modeInput").select_option("pingpong")
                        assert page.locator("#reverseFilename").input_value()=="personal-name"
                        page.locator("#reverseFilename").fill("marker-15fps-pingpong")

                        # 31 original frames => 60 output; balances endpoint
                        # pieces that could otherwise become one-frame segments.
                        thirty_one=list(range(31))+list(range(29,0,-1))
                        export(page,directory,mode,0,31/15,60,thirty_one)

                        # 150 original frames, five forward and five return
                        # chunks, 298 frames and 19.8667-second output.
                        page.locator("#sourceInput").set_input_files(str(long))
                        page.locator("#reversePanel").wait_for(state="visible",timeout=20000)
                        page.locator("#modeInput").select_option("pingpong")
                        export(page,directory,mode,0,10,298)

                        # Repeated-run and cancel should never expose a
                        # downloadable partial ping-pong MP4.
                        page.evaluate("""() => {
                          document.querySelector('#reverseButton').click();
                          document.querySelector('#cancelReverseButton').click();
                        }""")
                        assert page.locator("#resultArea").is_hidden()
                        assert page.locator("#saveReverseButton").is_hidden()
                        assert not errors,(mode,errors)
                        assert not external,(mode,external)
                        print(f"[PASS] {mode}: ping-pong repeat/cancel/zero external media traffic",flush=True)
                        page.close()
                finally:browser.close()
        finally:
            server.shutdown()
            server.server_close()


if __name__=="__main__":
    main()
