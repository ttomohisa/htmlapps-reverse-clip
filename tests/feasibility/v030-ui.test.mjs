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
    "maxSpan=$('#qualityInput').value==='1920'?5:MAX_CLIP_SECONDS",
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

test('MT or ST frame-count failures stay fail-closed and expose actionable diagnostics',()=>{
  assert.ok(html.includes('reverseFrameMismatch'));
  assert.ok(html.includes("'Reverse frame count mismatch: expected=") ||
            html.includes('Reverse frame count mismatch: expected='));
  assert.ok(html.includes("$('#reverseErrorDetails').open=true;"));
  assert.ok(html.includes("'Stage: '+currentStage+' · Runtime: '"));
  assert.ok(html.includes("'Chunk: '+(currentChunkIndex+1)"));
  for(const key of ['failedChunkIndex','failedChunkStart','failedChunkDuration',
                    'expectedFrames','actualFrames',"errorCode:'frame-count-mismatch'"]){
    assert.ok(html.includes(key), key);
  }
  assert.ok(html.includes("$('#reverseErrorDetails').open=false;"));
  assert.ok(html.includes('An incomplete video will not be saved.'));
  assert.ok(html.includes('不完全な動画は保存されません'));
  assert.ok(html.includes("throw new Error('MP4 segment failed validation ("));
});

test('mobile workflow navigation and saved-result step are implemented with native controls',()=>{
  for(const id of [
    'rcWorkflow','rcFlowNav','flowVideoButton','flowEditButton',
    'flowResultButton','flowAnnouncement','selectedSourceSummary',
    'selectedSourceText','flowGoEditButton','flowBackToEditButton',
    'resultDimensions','flowSaveHint'
  ]){
    assert.equal(html.split('id="'+id+'"').length-1,1,id+' must exist exactly once');
  }
  assert.ok(html.includes('data-flow-step="video"'));
  for(const step of ['video','edit','result']){
    assert.ok(html.includes('data-flow-target="'+step+'"'));
    assert.ok(html.includes('data-flow-step="'+step+'"]'));
  }
  assert.ok(html.includes('aria-current="step"'));
  assert.ok(html.includes('position:sticky;top:var(--header-height)'));
  assert.ok(html.includes('#rcWorkflow[data-flow-step="result"] #reversePanel > :not(#resultArea)'));
  assert.ok(!html.includes('position:fixed;bottom:0'));
  for(const marker of [
    "function updateFlowNavigation()","function setFlowStep(step,",
    "if(phase==='ready') updateFlowNavigation()",
    "setFlowStep('edit');",
    "if(flowStep==='edit')setFlowStep('result')",
    "if(step==='result'&&!flowResultReady())return false",
    "if (flowStep === 'result' && !canResult) flowStep=canEdit?'edit':'video",
    "if(step===flowStep) button.setAttribute('aria-current','step')",
    "$('#flowSaveHint').hidden=false",
    "$('#flowSaveHint').hidden=true",
    "document.querySelectorAll('[data-i18n]')"
  ]) assert.ok(html.includes(marker),marker);
});

test('responsive step headings follow Video/Edit/Result and recover on desktop resize',()=>{
  assert.ok(html.includes('id="workspaceBody" data-i18n="workspaceBody"'));
  assert.ok(html.includes("'workspaceTitle':flowStep==='edit'?'flowEditTitle':'flowResultTitle'"));
  assert.ok(html.includes("'workspaceBody':flowStep==='edit'?'flowEditBody':'flowResultBody'"));
  assert.ok(html.includes("window.addEventListener('resize',updateFlowNavigation);"));
  for(const title of ['flowEditTitle','flowResultTitle','flowEditBody','flowResultBody']){
    assert.equal(html.split('"'+title+'":').length-1,2,title+' must be bilingual');
  }
});

test('JA/EN workflow labels and actual output metadata are present; saving does not promise OS success',()=>{
  for(const label of [
    '"flowVideo": "動画"','"flowEdit": "編集"','"flowResult": "結果"',
    '"flowVideo": "Video"','"flowEdit": "Edit"','"flowResult": "Result"',
    '"flowSaveHint": "保存先はブラウザーのダウンロードから確認してください。',
    '"flowSaveHint": "Check your browser',
    '"flowOutputDimensions": "出力：{width} × {height}px・{fps}fps"',
    '"flowOutputDimensions": "Output: {width} × {height}px · {fps}fps"'
  ]) assert.ok(html.includes(label),label);
  assert.ok(html.includes("state.conversion.outputWidth"));
  assert.ok(html.includes("width:resultVideo.videoWidth,height:resultVideo.videoHeight"));
  assert.ok(html.includes('逆再生MP4のダウンロードを開始しました。'));
  assert.ok(html.includes('Ping-pong MP4 download started.'));
  assert.ok(!html.includes('逆再生MP4を保存しました。'));
});

test('optional diagnosis and development explanations are collapsed but accessible',()=>{
  for(const id of ['diagnosticsDetails','developmentDetails','openDiagnosticsButton']){
    assert.equal(html.split('id="'+id+'"').length-1,1,id);
  }
  assert.ok(html.includes('<details id="diagnosticsDetails" class="rc-advanced">'));
  assert.ok(html.includes('<details id="developmentDetails" class="rc-advanced">'));
  assert.ok(html.includes('"diagnosticsSummary": "困ったときの診断"'));
  assert.ok(html.includes('"diagnosticsSummary": "Troubleshooting and diagnostics"'));
  assert.ok(html.includes('"openDiagnostics": "診断ログを保存する"'));
  assert.ok(html.includes('details.open=true;'));
  assert.ok(html.includes("details.querySelector('summary').focus({preventScroll:true});"));
  assert.ok(html.includes("$('#openDiagnosticsButton').hidden=false;"));
  assert.ok(html.includes("$('#openDiagnosticsButton').hidden=true;"));
  // Moved to a disclosure, not removed: the original diagnostic export,
  // JS/WASM test and technical status still exist exactly once.
  for(const id of ['downloadReportButton','probeButton','seekButton','probeReport',
                   'guaranteesTitle','guaranteesBody','buildVersion']){
    assert.equal(html.split('id="'+id+'"').length-1,1,id);
  }
});
