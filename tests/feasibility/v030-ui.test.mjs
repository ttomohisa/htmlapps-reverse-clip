import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';

const read = p => readFileSync(new URL('../../'+p,import.meta.url),'utf8');
const html=read('src/index.template.html');
const icon=read('assets/favicon.svg');
const config=JSON.parse(read('app.config.json'));

test('v0.3.0 version and exact supplied 64px favicon/brand icon',()=>{
  assert.match(config.version,/^0\.(3|[4-9]|[1-9][0-9]+)\.[0-9]+$/,'v0.3 foundation must persist in later milestones');
  assert.equal(createHash('sha256').update(icon).digest('hex'),
    'd0ed25d1c017d253aaf48a3d482e6d60b97e6386edff5fa97bbf13e041af0f7e');
  assert.match(icon,/viewBox="0 0 64 64"/);
  assert.match(icon,/<rect width="64" height="64" rx="16" fill="#16624f"/);
  assert.equal(html.split('__APP_ICON_DATA_URI__').length-1,2);
});
test('language button reads JA; app-specific header and privacy copy are bilingual',()=>{
  assert.ok(html.includes("language === 'ja' ? 'EN' : 'JA'"));
  assert.ok(!html.includes("language === 'ja' ? 'EN' : '日本語'"));
  assert.ok(html.includes('"brandMeta": "好きな区間を逆再生MP4に"'));
  assert.ok(html.includes('"localBadge": "完全ローカル処理"'));
  assert.ok(html.includes('"localBadge": "Fully local processing"'));
  assert.ok(!html.includes('"footer": "逆再生の技術検証版"'));
  assert.match(html,/<footer><span id="footerName">Reverse Clip<\/span> · <span data-i18n="footerLicense">/);
});
test('selection handles, keyboard input, half-open interval plan and source playback are wired',()=>{
  for(const marker of ['id="trimStartSlider"','id="trimEndSlider"',
    'id="trimSelectedTrack"','id="previewSelectionButton"',
    "addEventListener('input',()=>moveTrimHandle(which))",
    "maxSpan=$('#qualityInput').value==='1280'?5:MAX_CLIP_SECONDS",
    'function previewSelectedSource()','function syncTrimControls()']) {
    assert.ok(html.includes(marker),marker);
  }
  assert.ok(html.includes("$('#rangeStart').value=start.toFixed(1)"));
  assert.ok(html.includes("$('#rangeEnd').value=end.toFixed(1)"));
  assert.ok(html.includes("video.currentTime=start"));
  assert.ok(html.includes("video.currentTime>=end-.025"));
});
test('help dialog stops background scroll and restores it on all closure paths',()=>{
  for(const marker of ["body.help-modal-open { position: fixed",
    "html.help-modal-open { overflow: hidden",
    'function lockHelpBackground()','function unlockHelpBackground()',
    "helpDialog.addEventListener('close',unlockHelpBackground)",
    'document.body.style.top=',
    'window.scrollTo(0,restoreY)',
    'overscroll-behavior: contain']) {
    assert.ok(html.includes(marker),marker);
  }
  assert.ok(html.includes("helpDialog.showModal()"));
});
