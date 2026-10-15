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


def vfr_fixture(directory:Path)->Path:
    """A truly variable-frame-rate MP4, not a CFR video with changed metadata."""
    target=directory/"vfr-markers.mp4"
    source=str(directory/"markers"/"%03d.ppm")
    subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error",
        "-framerate","15","-i",source,
        "-vf",r"select=not(eq(mod(n\,7)\,0)+eq(mod(n\,11)\,0))",
        "-fps_mode","vfr","-c:v","libx264","-preset","ultrafast",
        "-crf","18","-pix_fmt","yuv420p",str(target)],check=True)
    report=json.loads(subprocess.check_output(["ffprobe","-v","error",
        "-select_streams","v:0","-show_entries","frame=best_effort_timestamp_time",
        "-of","json",str(target)],text=True))
    times=[float(x["best_effort_timestamp_time"]) for x in report["frames"]]
    intervals=[round(b-a,2) for a,b in zip(times,times[1:])]
    assert len(times)<45 and max(intervals)>=.13, (len(times),intervals)
    return target


def black_fixture(directory:Path)->Path:
    target=directory/"black-source.mp4"
    subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error",
        "-f","lavfi","-i","color=c=black:s=160x90:r=15",
        "-t","2","-c:v","libx264","-pix_fmt","yuv420p",
        "-preset","ultrafast",str(target)],check=True)
    return target


def portrait_fixture(directory:Path)->Path:
    target=directory/"portrait-source.mp4"
    subprocess.run(["ffmpeg","-y","-hide_banner","-loglevel","error",
        "-f","lavfi","-i","testsrc2=size=90x160:rate=15",
        "-t","2","-c:v","libx264","-pix_fmt","yuv420p",
        "-preset","ultrafast",str(target)],check=True)
    return target


def decoded_red_pixels(path:Path)->list[int]:
    raw=subprocess.check_output(["ffmpeg","-v","error","-i",str(path),
        "-vf","scale=1:1:flags=neighbor,format=rgb24","-fps_mode",
        "passthrough","-f","rawvideo","-pix_fmt","rgb24","pipe:1"])
    assert len(raw)%3==0,len(raw)
    return list(raw[::3])


def validate_vfr_seam(path:Path)->None:
    colors=decoded_red_pixels(path)
    assert len(colors)==28,len(colors)
    assert min(colors)>12,("Unexpected black frame in marked VFR output",colors)
    assert colors[14]-colors[0]>30,("Forward VFR content did not advance",colors)
    assert colors[15]-colors[-1]>30,("Reverse VFR content did not return",colors)
    assert all(b>=a-8 for a,b in zip(colors[:14],colors[1:15])), \
        ("Forward VFR content reversed unexpectedly",colors)
    assert all(b<=a+8 for a,b in zip(colors[15:-1],colors[16:])), \
        ("VFR return content moved forward unexpectedly",colors)
    assert all(abs(b-a)<55 for a,b in zip(colors,colors[1:])), \
        ("Unexpected gap across VFR concat boundary",colors)


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
    page.locator("#flowEditButton").click()
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
    return path


def main():
    with tempfile.TemporaryDirectory(prefix="reverse-pingpong-smoke-") as temp:
        directory=Path(temp)
        short=source_fixture(directory)
        long=long_fixture(directory)
        vfr=vfr_fixture(directory)
        black=black_fixture(directory)
        portrait=portrait_fixture(directory)
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
                        # The 0.5s shortest possible selection must actually
                        # render 8 forward and 6 return frames without stutter.
                        mini=list(range(8))+list(range(6,0,-1))
                        export(page,directory,mode,0,.5,14,mini)

                        # Changing conversion mode discards the old result,
                        # while preserving names intentionally edited by users.
                        page.locator("#reverseFilename").fill("personal-name")
                        page.locator("#flowEditButton").click()
                        page.locator("#modeInput").select_option("reverse")
                        assert page.locator("#resultArea").is_hidden()
                        assert page.locator("#reverseFilename").input_value()=="personal-name"
                        page.locator("#modeInput").select_option("pingpong")
                        assert page.locator("#reverseFilename").input_value()=="personal-name"
                        # After changing mode, the previous result is
                        # correctly hidden, so its filename input is not
                        # interactable. Re-selecting the source intentionally
                        # restores the mode-specific default before export.
                        page.locator("#sourceInput").set_input_files(str(short))
                        page.locator("#reversePanel").wait_for(state="visible",timeout=20000)
                        assert page.locator("#reverseFilename").input_value()=="marker-15fps-pingpong"

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

                        # Real VFR: source timestamps are irregular, so
                        # 15fps resampling can naturally repeat *source*
                        # content; do not incorrectly demand a new input
                        # frame at every output timestamp. Still require
                        # a decodable, monotonic forward/return movement and
                        # no unexpectedly inserted black/large seam gap.
                        page.locator("#sourceInput").set_input_files(str(vfr))
                        page.locator("#reversePanel").wait_for(state="visible",timeout=20000)
                        assert page.locator("#modeInput").input_value()=="pingpong"
                        vfr_result=export(page,directory,mode,.4,1.4,28)
                        validate_vfr_seam(vfr_result)
                        print(f"[PASS] {mode}: true VFR input and forward/return join",flush=True)

                        # Legitimately black input must not confuse the frame
                        # counter or get rejected as a blank output.
                        page.locator("#sourceInput").set_input_files(str(black))
                        page.locator("#reversePanel").wait_for(state="visible",timeout=20000)
                        black_result=export(page,directory,mode,.4,1.4,28)
                        colors=decoded_red_pixels(black_result)
                        assert len(colors)==28 and max(colors)<13,("black source changed",colors)
                        print(f"[PASS] {mode}: intentional black frames survive joined H.264",flush=True)

                        # Portrait phone-style media must retain dimensions
                        # while making a real native H.264 MP4.
                        page.locator("#sourceInput").set_input_files(str(portrait))
                        page.locator("#reversePanel").wait_for(state="visible",timeout=20000)
                        portrait_result=export(page,directory,mode,.4,1.4,28)
                        stream=json.loads(subprocess.check_output([
                            "ffprobe","-v","error","-select_streams","v:0",
                            "-show_entries","stream=width,height",
                            "-of","json",str(portrait_result)],text=True))["streams"][0]
                        assert (stream["width"],stream["height"])==(90,160),stream
                        print(f"[PASS] {mode}: native portrait 90x160 ping-pong",flush=True)

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
