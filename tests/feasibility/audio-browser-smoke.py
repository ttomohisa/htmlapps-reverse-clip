#!/usr/bin/env python3
"""Real local-only ST/MT audio acceptance, gated by pinned binary capabilities.

When audio-mux is absent this verifies the feature remains inaccessible. Once
SHA-pinned, exercise actual H264+AAC encoding, download, decoded waveform
direction, ping-pong soundtrack, silent-input fallback and cancel/save safety.
Desktop Chrome is NOT proof of real Android/iPhone performance.
"""
from __future__ import annotations
from array import array
import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import subprocess
import sys
import tempfile
import threading

from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[2]
DIST=ROOT/"dist"
LOCK=json.loads((ROOT/"reverse-runtime.lock.json").read_text())
ENABLED="audio-mux" in LOCK.get("features",[])
SAMPLE_RATE=48000


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


def generate_sources(directory:Path):
    voiced=directory/"audio-input.mp4"
    silent=directory/"silent-input.mp4"
    # The 0–0.5s audio interval is 300Hz; 0.5–1.0s is 990Hz.
    # After reverse, those halves must trade places. Ping-pong is
    # 300→990→990→300 without a duplicated endpoint frame.
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","lavfi","-i","testsrc2=size=160x90:rate=15:duration=2.4",
        "-f","lavfi","-i","sine=frequency=300:sample_rate=48000:duration=0.5",
        "-f","lavfi","-i","sine=frequency=990:sample_rate=48000:duration=0.5",
        "-filter_complex","[1:a][2:a]concat=n=2:v=0:a=1[a]",
        "-map","0:v:0","-map","[a]","-c:v","libx264",
        "-preset","ultrafast","-crf","24","-pix_fmt","yuv420p",
        "-c:a","aac","-b:a","96k",str(voiced)],check=True)
    subprocess.run(["ffmpeg","-hide_banner","-loglevel","error","-y",
        "-f","lavfi","-i","testsrc2=size=160x90:rate=15:duration=2.4",
        "-c:v","libx264","-preset","ultrafast","-crf","24",
        "-pix_fmt","yuv420p","-an",str(silent)],check=True)
    return voiced,silent


def mp4_info(path:Path, frames:int, audio:bool, duration:float):
    data=json.loads(subprocess.check_output(
       ["ffprobe","-v","error",
        "-show_entries","stream=codec_name,codec_type,nb_frames,duration,channels:format=duration",
        "-of","json",str(path)],text=True))
    videos=[x for x in data["streams"] if x["codec_type"]=="video"]
    audios=[x for x in data["streams"] if x["codec_type"]=="audio"]
    assert len(videos)==1 and videos[0]["codec_name"]=="h264",data
    assert int(videos[0]["nb_frames"])==frames,(frames,data)
    assert (len(audios)==1)==audio,data
    if audios:
        assert audios[0]["codec_name"]=="aac",data
        assert 1<=int(audios[0]["channels"])<=2,data
        if audios[0].get("duration"):
            assert abs(float(audios[0]["duration"])-duration)<.16,data
    assert abs(float(data["format"]["duration"])-duration)<.16,data


def decoded_pcm(path:Path):
    out=subprocess.check_output(["ffmpeg","-v","error","-i",str(path),
        "-map","0:a:0","-ac","1","-ar",str(SAMPLE_RATE),
        "-f","s16le","-acodec","pcm_s16le","pipe:1"])
    samples=array("h")
    samples.frombytes(out)
    if sys.byteorder!="little":samples.byteswap()
    return samples


def crossings(samples,t0,t1):
    begin=round(t0*SAMPLE_RATE)
    end=round(t1*SAMPLE_RATE)
    section=samples[begin:end]
    assert len(section)>5000,(len(section),len(samples))
    assert max(section)-min(section)>200,"unexpected silence in audio"
    return sum(1 for a,b in zip(section,section[1:]) if (a<0)<= (b>=0) and (a<0)!=(b<0))


def verify_audio_direction(path:Path, mode:str):
    samples=decoded_pcm(path)
    assert len(samples)>SAMPLE_RATE*.8,len(samples)
    if mode=="reverse":
        first=crossings(samples,.15,.35)
        last=crossings(samples,.65,.85)
        assert first>last*2,(first,last)
    elif mode=="pingpong":
        low0=crossings(samples,.15,.35)
        high0=crossings(samples,.65,.85)
        high1=crossings(samples,1.05,1.25)
        low1=crossings(samples,1.50,1.70)
        assert high0>low0*2 and high1>low1*2,(low0,high0,high1,low1)
    else:raise ValueError(mode)


def export(page,directory:Path,mode:str,with_audio:bool):
    page.locator("#rangeStart").fill("0")
    page.locator("#rangeStart").dispatch_event("change")
    page.locator("#rangeEnd").fill("1")
    page.locator("#rangeEnd").dispatch_event("change")
    page.locator("#modeInput").select_option(mode)
    page.locator("#audioInput").select_option("reverse" if with_audio else "none")
    assert page.locator("#reverseButton").is_enabled(),page.locator("#rangeNotice").inner_text()
    page.locator("#reverseButton").click()
    page.wait_for_function("""()=>
      !document.querySelector('#resultArea').hidden ||
      !document.querySelector('#reverseErrorDetails').hidden""",timeout=150000)
    if page.locator("#reverseErrorDetails").is_visible():
        raise AssertionError("A/V encode failed: "+
          page.locator("#reverseErrorDetail").inner_text())
    with page.expect_download(timeout=15000) as d:
        page.locator("#saveReverseButton").click()
    target=directory/f"{mode}-{'aac' if with_audio else 'silent'}.mp4"
    d.value.save_as(target)
    expected_frames=28 if mode=="pingpong" else 15
    mp4_info(target,expected_frames,with_audio,expected_frames/15)
    if with_audio:verify_audio_direction(target,mode)
    print(f"[PASS] {mode}: actual H.264 + {'AAC' if with_audio else 'no audio'} MP4,"
          f" {expected_frames} frames, decoded and saved",flush=True)


def main():
    with tempfile.TemporaryDirectory(prefix="reverse-v05-audio-") as temp:
        directory=Path(temp)
        voiced,silent=generate_sources(directory)
        server=ThreadingHTTPServer(("127.0.0.1",0),Handler)
        threading.Thread(target=server.serve_forever,daemon=True).start()
        base=f"http://127.0.0.1:{server.server_port}"
        try:
            with sync_playwright() as pw:
                opt={"headless":True,"args":["--no-sandbox","--disable-dev-shm-usage"]}
                if os.getenv("CHROMIUM_EXE"):opt["executable_path"]=os.environ["CHROMIUM_EXE"]
                browser=pw.chromium.launch(**opt)
                try:
                    for mode,html in (("ST","index.html"),("MT","index.mt.html")):
                        page=browser.new_page(accept_downloads=True,
                           viewport={"width":390,"height":844})
                        errors,remote=[],[]
                        page.on("pageerror",lambda e:errors.append(str(e)))
                        page.on("request",lambda r: remote.append(r.url)
                          if not r.url.startswith((base,"blob:","data:")) else None)
                        response=page.goto(base+"/"+html,wait_until="domcontentloaded")
                        assert response and response.status==200
                        assert page.evaluate("crossOriginIsolated")== (mode=="MT")
                        page.locator("#sourceInput").set_input_files(str(voiced))
                        page.locator("#reversePanel").wait_for(state="visible",timeout=10000)
                        assert page.locator("#audioInput").input_value()=="none"
                        if not ENABLED:
                            assert page.locator("#audioInput").is_disabled()
                            assert page.locator("#audioReverseOption").is_disabled()
                            print(f"[PASS] {mode}: unverified AAC export remains disabled",flush=True)
                            page.close()
                            continue

                        page.wait_for_function("() => !document.querySelector('#audioReverseOption').disabled",timeout=40000)
                        assert page.locator("#audioInput").is_enabled()
                        export(page,directory, "reverse", True)
                        export(page,directory, "pingpong", True)
                        page.locator("#sourceInput").set_input_files(str(silent))
                        page.locator("#reversePanel").wait_for(state="visible",timeout=10000)
                        page.wait_for_function("""() =>
                          !document.querySelector('#audioNotice').textContent.includes('確認しています') &&
                          !document.querySelector('#audioNotice').textContent.includes('Checking this')""",
                          timeout=40000)
                        assert page.locator("#audioReverseOption").is_disabled()
                        assert page.locator("#audioInput").input_value()=="none"
                        export(page,directory,"reverse",False)

                        # Invalidated output cannot be saved after a new job.
                        page.locator("#modeInput").select_option("pingpong")
                        assert page.locator("#resultArea").is_hidden()
                        page.evaluate("""() => {
                          document.querySelector('#reverseButton').click();
                          document.querySelector('#cancelReverseButton').click();
                        }""")
                        assert page.locator("#resultArea").is_hidden()
                        assert page.locator("#saveReverseButton").is_hidden()
                        assert not errors,(mode,errors)
                        assert not remote,(mode,remote)
                        page.close()
                finally:browser.close()
        finally:
            server.shutdown()
            server.server_close()


if __name__=="__main__":
    main()
