import sys,runpy,threading,tempfile,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];os.chdir(ROOT)
sys.path.insert(0,str(ROOT/'tests/feasibility'))
from rc_demo_media import make_rc_demo_video
from playwright.sync_api import sync_playwright
module=runpy.run_path('tests/feasibility/editor-browser-smoke.py')
server=module['ThreadingHTTPServer'](('127.0.0.1',0),module['Handler']);threading.Thread(target=server.serve_forever,daemon=True).start()
with tempfile.TemporaryDirectory() as tmp:
 src=make_rc_demo_video(Path(tmp)/'motion-sample.mp4')
 with sync_playwright() as pw:
  browser=pw.chromium.launch(executable_path=os.environ.get('CHROMIUM_EXE','/usr/bin/chromium'),args=['--no-sandbox'])
  for lang in ['ja','en']:
   for width in [1360,390]:
    ctx=browser.new_context(locale=lang+'-'+('JP' if lang=='ja' else 'US'),viewport={'width':width,'height':900 if width==1360 else 844});page=ctx.new_page()
    page.goto(f'http://127.0.0.1:{server.server_port}/dist/index.html');page.locator('#sourceInput').set_input_files(src)
    page.wait_for_function("() => document.querySelector('#loadStatus').dataset.phase==='ready'")
    page.locator('#rangeStart').fill('0.2');page.locator('#rangeEnd').fill('1.8');page.locator('#qualityInput').select_option('720');page.locator('#fpsInput').select_option('30');page.locator('#modePingpongButton').click()
    page.wait_for_function("() => document.querySelectorAll('#timelineFilmstrip img').length===8")
    page.locator('#sourceVideo').evaluate("async v => {await v.play();v.pause();v.currentTime=.7;}")
    page.wait_for_function("() => {const v=document.querySelector('#sourceVideo');return !v.seeking && v.readyState>=2 && Math.abs(v.currentTime-.7)<.02;}")
    page.wait_for_function("() => !document.querySelector('#appToast').classList.contains('show')")
    page.evaluate("() => window.scrollTo({top:document.querySelector('#sourceVideo').getBoundingClientRect().top+scrollY-150,behavior:'instant'})")
    page.wait_for_function("() => Math.abs(document.querySelector('#sourceVideo').getBoundingClientRect().top-150)<2")
    out='assets/screenshot'+('-mobile' if width==390 else '')+('-en' if lang=='en' else '')+'.png'
    page.screenshot(path=out);print(out,flush=True);ctx.close()
  browser.close()
server.shutdown()
