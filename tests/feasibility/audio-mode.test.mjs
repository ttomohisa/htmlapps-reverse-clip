import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=p=>readFileSync(new URL('../../'+p,import.meta.url),'utf8');
const html=read('src/index.template.html');
const builder=read('build-standalone.ps1');
const lock=JSON.parse(read('reverse-runtime.lock.json'));
const cfg=JSON.parse(read('app.config.json'));

test('v0.7 retains v0.5 audio UI and starts disabled unless an audited AAC MP4 mux is pinned',()=>{
  assert.equal(cfg.version,'0.7.0');
  assert.ok(html.includes('id="audioInput" disabled'));
  assert.ok(html.includes('id="audioReverseOption" value="reverse"'));
  assert.ok(html.includes("const AUDIO_MUX_ENABLED = __AUDIO_MUX_ENABLED__"));
  assert.ok(builder.includes("$audioMuxEnabled = $reverseFeatures -contains 'audio-mux'"));
  assert.ok(builder.includes('"__AUDIO_MUX_ENABLED__"'));
  assert.equal(Array.isArray(lock.features)&&lock.features.includes('audio-mux'),
    Boolean(lock.features?.includes('audio-mux')),'audio capability must be explicitly locked');
});
test('audio selection never silently changes silent-only output or retains stale output',()=>{
  assert.ok(html.includes("$('#audioInput').value='none'"));
  assert.ok(html.includes("$('#audioInput').addEventListener('change',onAudioModeChanged)"));
  assert.ok(html.includes('function onAudioModeChanged()'));
  assert.ok(html.includes('state.audioPresent=null'));
  assert.ok(html.includes('state.audioChecked=false'));
  assert.ok(html.includes("showToast(translate('audioUnavailable'));return;"));
  assert.ok(html.includes("fps:OUTPUT_FPS,audio:wantsAudio?'reverse':'none'"));
  assert.ok(html.includes("'--audio-segment'"));
  assert.ok(html.includes("'--mux-audio'"));
  assert.ok(html.includes('function inspectSourceAudio()'));
});
test('bilingual audio status text avoids falsely promising final functionality',()=>{
  for(const s of ['音声なし（既定）','音声も逆再生','音声付き出力は開発中です',
    'No audio (default)','Reverse audio too','Audio export is under development'])
    assert.ok(html.includes(s),s);
});
