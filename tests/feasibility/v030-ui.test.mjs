import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';

const read = p => readFileSync(new URL('../../'+p,import.meta.url),'utf8');
const html=read('src/index.template.html');
const icon=read('assets/favicon.svg');
const config=JSON.parse(read('app.config.json'));

test('v1.0 UI uses product copy without development gate jargon',()=>{
  assert.equal(config.version,'1.0.0');
  assert.match(config.description,/forward-and-back MP4.*browser/);
  assert.match(config.descriptionJa,/動画はブラウザ内で処理します/);
  assert.doesNotMatch(config.description,/PREPARATION|G2|G3|not released/);
  assert.match(read('docs/release/RC_CHECKLIST.md'),/Gate G3 NOT PASSED/);
  assert.match(read('DEVELOPMENT_PLAN.md'),/v0\.7\.0 development approved by owner; G2 carried forward/);
  assert.match(read('docs/feasibility/G2.md'),/G2 NOT PASSED/);
  assert.match(read('CHANGELOG.md'),/\[0\.7\.0\].*not released/);
});

test('v0.8 input hardening distinguishes short but decodable source and discloses fidelity limits',()=>{
  for(const key of ['sourceTooShort','sourceCompatibilitySummary','sourceCompatibilityBody',
                    'sourceAudioSelectionNote']){
    assert.equal(html.split('"'+key+'":').length-1,2,key+' must be available in JA/EN');
  }
  assert.ok(html.includes("video.duration > 0 && video.duration < .5"));
  assert.ok(html.includes("failSource('sourceTooShort');"));
  assert.ok(html.includes('id="sourceCompatibilityDetails"'));
  assert.ok(html.includes('data-i18n="sourceCompatibilityBody"'));
  assert.ok(html.includes('HDR/10-bit input is not automatically identified or color-preserved.'));
  assert.ok(html.includes('出力は15fpsで、元のフレームレートは維持しません。'));
  assert.ok(html.includes('Multiple audio tracks cannot be selected.'));
});

test('v0.3.0 version and exact supplied 64px favicon/brand icon',()=>{
  assert.equal(config.version,'1.0.0');
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
    "setFlowStep('edit',{focus:true});",
    "if(flowStep==='edit')setFlowStep('result',{focus:true})",
    "if(step==='result'&&!flowResultReady())return false",
    "if (flowStep === 'result' && !canResult) flowStep=canEdit?'edit':'video",
    "if(step===flowStep) button.setAttribute('aria-current','step')",
    "$('#flowSaveHint').hidden=false",
    "$('#flowSaveHint').hidden=true",
    "document.querySelectorAll('[data-i18n]')"
  ]) assert.ok(html.includes(marker),marker);
});

test('mobile result playback pauses when hidden; typed range changes revoke stale MP4 immediately',()=>{
  assert.ok(html.includes("if(flowStep==='result'&&step!=='result')$('#resultVideo').pause();"));
  assert.ok(html.includes("$('#'+id).addEventListener('input',onOutputSettingsEdited);"));
  assert.ok(html.includes("$('#'+id).addEventListener('change',onOutputSettingsEdited);"));
  assert.ok(html.includes("$('#qualityInput').addEventListener('change',onOutputSettingsEdited);"));
});

test('unsaved results use localized confirmation and automatic transitions restore focus',()=>{
  assert.ok(html.includes('id="workspaceTitle" tabindex="-1"'));
  assert.ok(html.includes("function setFlowStep(step,{scroll=true,focus=false}={})"));
  assert.ok(html.includes("if(onMobile&&focus)$('#workspaceTitle').focus({preventScroll:true});"));
  for(const key of ['flowReplaceTitle','flowReplaceMessage','flowReplaceConfirm','helpNoteReplace']){
    assert.equal(html.split('"'+key+'":').length-1,2,'JA/EN key: '+key);
  }
  assert.ok(html.includes("if(flowResultReady()&&!resultDownloadStarted){"));
  assert.ok(html.includes("const approved=await AppConfirm.ask({"));
  assert.ok(html.includes("if(!approved||attempt!==sourceSelectionSequence){"));
  assert.ok(html.includes("sourceSelectionSequence+=1;"));
  assert.ok(html.includes("resultDownloadStarted=true; // Request, not proof of OS save completion."));
  assert.ok(html.includes("resultDownloadStarted=false;"));
  assert.ok(html.includes("setFlowStep('result',{focus:true});"));
  assert.ok(html.includes("$('#flowBackToEditButton').addEventListener('click',()=>setFlowStep('edit',{focus:true}))"));
});

test('mobile processing stays on Edit until completion or cancellation',()=>{
  assert.ok(html.includes("const busy=Boolean(conversionController);"));
  assert.ok(html.includes("button.disabled=step==='video'?busy:step==='edit'?!canEdit:!canResult;"));
  assert.ok(html.includes("if(step==='video'&&conversionController)return false;"));
  assert.ok(html.includes("conversionController=controller;\n        updateFlowNavigation();"));
  assert.ok(html.includes("conversionController=null;\n            updateFlowNavigation();"));
  assert.ok(html.includes("#workspaceTitle{scroll-margin-top:calc(var(--header-height) + 14px)}"));
  assert.ok(html.includes("(focus?$('#workspaceTitle'):$('#rcFlowNav'))"));
  assert.ok(html.includes("root.style.scrollBehavior='auto';"));
  assert.ok(html.includes("}finally{root.style.scrollBehavior=previous;}"));
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
    '"flowSaveHint": "MP4のダウンロードを開始しました。',
    '"flowSaveHint": "MP4 download started.',
    '"flowOutputDimensions": "出力：{width} × {height}px・{fps}fps"',
    '"flowOutputDimensions": "Output: {width} × {height}px · {fps}fps"'
  ]) assert.ok(html.includes(label),label);
  assert.ok(html.includes("width:result.outputWidth,height:result.outputHeight"));
  assert.ok(html.includes('outputWidth:resultVideo.videoWidth,outputHeight:resultVideo.videoHeight'));
  assert.ok(html.includes('逆再生MP4のダウンロードを開始しました。'));
  assert.ok(html.includes('Ping-pong MP4 download started.'));
  assert.ok(!html.includes('逆再生MP4を保存しました。'));
});

test('v0.7 result, errors, and save guidance are fully localized without false claims',()=>{
  assert.ok(html.includes('function renderResultDetails()'));
  assert.ok(html.includes("const isPingpong=result.mode==='pingpong', withAudio=result.audio==='reverse';"));
  assert.ok(html.includes("size:humanSize(result.outputBytes),chunks:result.chunkCount"));
  assert.ok(html.includes("renderResultDetails();"));
  assert.ok(html.includes("conversionMessageKey=failureKey;"));
  assert.ok(html.includes("conversionMessageKey='reverseCancelled';"));
  assert.ok(html.includes("if(conversionMessageKey && !conversionController)"));
  assert.ok(html.includes("$('#flowAnnouncement').textContent=format('flowStepAnnouncement'"));
  assert.ok(html.includes('"helpStep3": "Choose Reverse or Ping-pong, output quality and optional reverse audio'));
  assert.ok(html.includes('"helpNoteBrowser": "Some Android photo/cloud providers cannot be read directly.'));
  assert.ok(!html.includes('Audio is not yet supported.'));
  assert.ok(html.includes('"reverseDescription": "15fps · silent by default'));
  assert.ok(html.includes('"reverseDescription": "15fps・音声なしが既定'));
  assert.ok(!html.includes('"reportSaved": "Diagnostic JSON download started."'));
  assert.ok(html.includes('"helpPrivacyBody": "Your video is processed in the browser'));
  assert.ok(html.includes('"helpPrivacyBody": "動画は端末内で処理し'));
  assert.ok(!html.includes('Files up to 64 MiB are copied into local browser memory for conversion'));
});

test('bilingual media labels and failed export focus are accessible',()=>{
  assert.ok(html.includes('data-i18n-aria-label="sourceVideoLabel"'));
  assert.ok(html.includes('data-i18n-aria-label="conversionProgressLabel"'));
  for(const key of ['sourceVideoLabel','resultReverseVideoLabel',
                    'resultPingpongVideoLabel','conversionProgressLabel']){
    assert.equal(html.split('"'+key+'":').length-1,2,'JA/EN label '+key);
  }
  const setResultLabel="translate(isPingpong?'resultPingpongVideoLabel':'resultReverseVideoLabel')";
  assert.equal(html.split(setResultLabel).length-1,2,
    'result media aria-label must track both mode and language');
  assert.ok(html.includes("const summary=$('#reverseErrorDetails > summary');"));
  assert.ok(html.includes("summary.focus({preventScroll:true});"));
  assert.ok(html.includes("summary.scrollIntoView({block:'nearest',behavior:'auto'});"));
  assert.ok(html.includes("if(window.matchMedia?.('(max-width:600px)').matches){"));
});

test('developer diagnostic and development panels are gone; relevant error details remain',()=>{
  for(const id of ['diagnosticsDetails','developmentDetails','openDiagnosticsButton',
                   'downloadReportButton','probeButton','seekButton','probeReport',
                   'guaranteesTitle','outputFilename']){
    assert.ok(!html.includes('id="'+id+'"'),id+' should not be in the product HTML');
  }
  for(const id of ['reverseErrorDetails','reverseErrorDetail','buildVersion']){
    assert.equal(html.split('id="'+id+'"').length-1,1,id+' must remain');
  }
  assert.ok(html.includes('data-i18n="errorDetailTitle"'));
  assert.ok(!html.includes('困ったときの診断'));
  assert.ok(!html.includes('開発中の機能と制限'));
  assert.ok(!html.includes('実機検証中です。'));
  assert.ok(html.includes('"introTitle": "動画の逆再生・往復再生"'));
  assert.ok(html.includes('"introTitle": "Reverse & ping-pong video"'));
  assert.ok(!html.includes('動画の逆再生・往復再生（実験版）'));
  assert.ok(html.includes("$('#versionBadge').textContent='v'+APP_CONFIG.version;"));
  assert.ok(html.includes("$('#reverseErrorDetails').open=true;"));
});
