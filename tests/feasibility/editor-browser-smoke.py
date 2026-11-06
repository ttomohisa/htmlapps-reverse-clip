"""Real ST/MT editor, draft and 30fps integration. Synthetic media only."""
import json, os, subprocess, tempfile, threading
from pathlib import Path
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[2]
class Handler(SimpleHTTPRequestHandler):
 def __init__(self,*a,**k):super().__init__(*a,directory=str(ROOT),**k)
 def log_message(self,*a):pass
 def end_headers(self):
  self.send_header('Cross-Origin-Opener-Policy','same-origin');self.send_header('Cross-Origin-Embedder-Policy','require-corp');super().end_headers()
def probe(path):
 return json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-of','json',str(path)]))['streams']
def main():
 with tempfile.TemporaryDirectory() as tmp:
  tmp=Path(tmp); source=tmp/'input.mp4'
  subprocess.run(['ffmpeg','-v','error','-y','-f','lavfi','-i','testsrc2=size=640x360:rate=30','-f','lavfi','-i','sine=frequency=440:sample_rate=48000','-t','12','-c:v','libx264','-preset','ultrafast','-pix_fmt','yuv420p','-c:a','aac',str(source)],check=True)
  server=ThreadingHTTPServer(('127.0.0.1',0),Handler);threading.Thread(target=server.serve_forever,daemon=True).start()
  try:
   with sync_playwright() as pw:
    browser=pw.chromium.launch(executable_path=os.getenv('CHROMIUM_EXE','/usr/bin/chromium'),args=['--no-sandbox'])
    for variant in os.getenv('EDITOR_VARIANTS','index.html,index.mt.html').split(','):
     context=browser.new_context(accept_downloads=True,locale='ja-JP',viewport={'width':390,'height':844})
     context.add_init_script("""window.shareCalls=[];window.shareOutcome='cancel';
      Object.defineProperty(navigator,'canShare',{value:({files})=>files?.[0] instanceof File,configurable:true});
      Object.defineProperty(navigator,'share',{value:async ({files})=>{window.shareCalls.push({name:files[0].name,size:files[0].size,type:files[0].type});
       if(window.shareOutcome==='cancel')throw new DOMException('Cancelled','AbortError');
       if(window.shareOutcome==='fail')throw new Error('Test failure');},configurable:true});""")
     page=context.new_page();errors=[];remote=[]
     page.on('pageerror',lambda e:errors.append(str(e)))
     page.on('request',lambda r:remote.append(r.url) if r.url.startswith('http') and not r.url.startswith('http://127.0.0.1:') else None)
     page.goto(f'http://127.0.0.1:{server.server_port}/dist/{variant}')
     page.locator('#sourceInput').set_input_files(source)
     page.wait_for_function("() => document.querySelector('#loadStatus').dataset.phase==='ready'")
     page.wait_for_function("() => document.querySelectorAll('#timelineFilmstrip img').length===8",timeout=30000)
     assert not page.locator('#modeInput').is_visible(),'internal select must stay hidden'
     # A failed zoom thumbnail decode must not retain imagery from another scale.
     page.evaluate("""() => { window.originalMediaLoad=HTMLMediaElement.prototype.load;
      HTMLMediaElement.prototype.load=function(){if(this.tagName==='VIDEO' && !this.id){queueMicrotask(()=>this.dispatchEvent(new Event('error')));}else window.originalMediaLoad.call(this);}; }""")
     page.locator('#timelineZoomButton').click()
     page.wait_for_function("() => document.querySelector('#trimPreviewNotice').textContent.includes('サムネイル')")
     assert page.locator('#timelineFilmstrip img').count()==0,'stale thumbnails must be cleared on zoom failure'
     assert page.locator('#rangeStart').is_enabled()
     page.evaluate('() => {HTMLMediaElement.prototype.load=window.originalMediaLoad;}')
     assert page.locator('#timelineZoomButton').get_attribute('aria-pressed')=='true'
     page.locator('#rangeStart').fill('2');page.locator('#rangeEnd').fill('4')
     view=page.locator('#trimStartSlider').evaluate('(v)=>[v.min,v.max]')
     page.locator('#trimStartSlider').focus();page.locator('#trimStartSlider').press('ArrowRight')
     assert page.locator('#rangeStart').input_value()=='2.1'
     assert page.locator('#trimStartSlider').evaluate('(v)=>[v.min,v.max]')==view,'zoom scale jumps while dragging'
     page.wait_for_function("() => Math.abs(document.querySelector('#sourceVideo').currentTime-2.1)<.02")
     page.locator('#markStartButton').click();assert page.locator('#rangeStart').input_value()=='2.1'
     page.locator('#rangeStart').fill('2')
     page.locator('#fpsInput').select_option('30')
     page.locator('#qualityInput').select_option('720')
     page.locator('#modePingpongButton').click()
     assert page.locator('#modePingpongButton').get_attribute('aria-pressed')=='true'
     page.wait_for_function("() => !document.querySelector('#audioInput').disabled",timeout=60000)
     page.locator('#audioInput').select_option('reverse')
     page.locator('#reverseButton').click()
     page.wait_for_function("() => !document.querySelector('#resultArea').hidden",timeout=120000)
     page.locator('#reverseFilename').fill('my-edited-result')
     with page.expect_download() as download:page.locator('#saveReverseButton').click()
     assert download.value.suggested_filename=='my-edited-result.mp4'
     out=tmp/f'{variant}.mp4';download.value.save_as(out)
     streams=probe(out);video=next(s for s in streams if s['codec_type']=='video')
     assert video['r_frame_rate']=='30/1' and int(video['nb_frames'])==118,video
     assert any(s['codec_type']=='audio' for s in streams)
     audio=next(s for s in streams if s['codec_type']=='audio')
     assert abs(float(audio['duration'])-float(video['duration']))<.15
     assert page.locator('#shareResultButton').is_visible()
     page.locator('#reverseFilename').fill('shared/name')
     page.locator('#shareResultButton').click()
     page.wait_for_function("() => !document.querySelector('#shareResultButton').disabled")
     call=page.evaluate('() => window.shareCalls[0]')
     assert call['name']=='shared-name.mp4' and call['type']=='video/mp4' and call['size']>500
     assert page.locator('#resultArea').is_visible(),'cancelled share discarded output'
     page.evaluate("() => {window.shareOutcome='fail';}");page.locator('#shareResultButton').click()
     page.wait_for_function("() => !document.querySelector('#shareResultButton').disabled")
     assert page.locator('#saveReverseButton').is_visible(),'failed share discarded output'
     page.locator('#loopResultInput').check();assert page.locator('#resultVideo').evaluate('(v)=>v.loop')
     page.locator('#flowBackToEditButton').click()
     page.locator('#draftButton').click()
     page.wait_for_function("() => !document.querySelector('#resultArea').hidden",timeout=120000)
     assert page.locator('#draftNotice').is_visible()
     assert not page.locator('#saveReverseButton').is_visible()
     with page.expect_download() as download:
      page.locator('#resultVideo').evaluate("v=>{const a=document.createElement('a');a.href=v.src;a.download='draft.mp4';a.click();}")
     draft=tmp/f'draft-{variant}.mp4';download.value.save_as(draft);draft_streams=probe(draft)
     dv=next(s for s in draft_streams if s['codec_type']=='video')
     assert dv['r_frame_rate']=='15/1' and max(int(dv['width']),int(dv['height']))<=360
     assert not any(s['codec_type']=='audio' for s in draft_streams)
     assert not page.locator('#shareResultButton').is_visible()
     page.locator('#createFinalButton').click()
     page.wait_for_function("() => !document.querySelector('#resultArea').hidden",timeout=120000)
     assert not page.locator('#draftNotice').is_visible() and page.locator('#saveReverseButton').is_visible()
     page.locator('#flowBackToEditButton').click();page.locator('#modeReverseButton').click()
     page.locator('#reverseButton').click()
     # Cancellation leaves no stale draft/final or thumbnail output.
     page.locator('#cancelReverseButton').click()
     assert not page.locator('#resultArea').is_visible()
     page.locator('#reverseButton').click()
     page.wait_for_function("() => !document.querySelector('#resultArea').hidden",timeout=120000)
     with page.expect_download() as download:page.locator('#saveReverseButton').click()
     reverse=tmp/f'reverse-{variant}.mp4';download.value.save_as(reverse)
     rv=next(s for s in probe(reverse) if s['codec_type']=='video')
     assert rv['r_frame_rate']=='30/1' and int(rv['nb_frames'])==60,rv
     # Compare the actual decoded frame content against source order.
     def pixels(path,filters):
      data=subprocess.check_output(['ffmpeg','-v','error','-i',str(path),'-vf',filters,'-fps_mode','passthrough','-f','rawvideo','-pix_fmt','rgb24','-'])
      return [data[i:i+43200] for i in range(0,len(data),43200)]
     original=pixels(source,'trim=start=2:end=4,setpts=PTS-STARTPTS,scale=160:90')
     for path,sequence in [(reverse,list(range(59,-1,-1))),(out,list(range(60))+list(range(58,0,-1)))]:
      actual=pixels(path,'scale=160:90')
      expected=[original[i] for i in sequence]
      assert len(actual)==len(expected)
      error=sum(sum(abs(a-b) for a,b in zip(frame,ref)) for frame,ref in zip(actual,expected))/(len(actual)*43200)
      assert error<8,('30fps frame sequence differs from selected source',error)
     # Return to edit and verify forbidden settings never silently change.
     page.locator('#flowBackToEditButton').click();page.locator('#qualityInput').select_option('1280')
     assert page.locator('#reverseButton').is_disabled()
     assert page.locator('#qualityInput').input_value()=='1280'
     page.locator('#qualityInput').select_option('720');page.locator('#rangeEnd').fill('8')
     assert page.locator('#reverseButton').is_disabled()
     page.locator('#rangeEnd').fill('4')
     page.locator('#timelineZoomButton').click();page.locator('#timelineZoomButton').click()
     page.wait_for_function("() => document.querySelectorAll('#timelineFilmstrip img').length===8")
     page.wait_for_function("() => !document.querySelector('#appToast').classList.contains('show')")
     for language in ['en','ja']:
      if page.locator('html').get_attribute('lang')!=language:page.locator('#languageButton').click()
      for width in [320,390,1360]:
       page.set_viewport_size({'width':width,'height':900 if width==1360 else 700})
       assert page.evaluate('document.documentElement.scrollWidth<=innerWidth'),(variant,language,width)
       if width in [390,1360] and variant=='index.html':
        folder=ROOT/'rc-evidence/editor';folder.mkdir(parents=True,exist_ok=True)
        page.evaluate('() => window.scrollTo(0,0)')
        page.screenshot(path=str(folder/f'{language}-{width}.png'),full_page=True)
     # Replace the source while a new thumbnail batch is queued, then fail import.
     page.locator('#timelineZoomButton').click()
     page.locator('#sourceInput').set_input_files({'name':'broken.mp4','mimeType':'video/mp4','buffer':b'not a movie'})
     page.wait_for_function("() => document.querySelector('#loadStatus').dataset.phase==='error'")
     assert page.locator('#timelineFilmstrip img').count()==0
     assert not page.locator('#resultArea').is_visible()
     page.locator('#sourceInput').set_input_files(source)
     page.wait_for_function("() => document.querySelector('#loadStatus').dataset.phase==='ready'")
     page.wait_for_function("() => document.querySelectorAll('#timelineFilmstrip img').length===8")
     assert not errors,errors
     assert not remote,remote
     print(json.dumps({'variant':variant,'30fpsFrames':video['nb_frames'],'draftWidth':dv['width'],'errors':errors,'external':remote}))
     context.close()
    browser.close()
  finally:server.shutdown()
if __name__=='__main__':main()
