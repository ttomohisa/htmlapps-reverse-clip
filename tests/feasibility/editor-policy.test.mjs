import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
const html=readFileSync(new URL('../../src/index.template.html',import.meta.url),'utf8');
function policy(){
 const start=html.indexOf('function editorOutputPolicy('), end=html.indexOf('// EDITOR POLICY END',start);
 assert.ok(start>=0 && end>start,'editor policies are defined');
 return runInNewContext(html.slice(start,end)+'\n({editorOutputPolicy,timelineViewport,boundaryAtTime,validSourceRange})');
}
test('30fps is allowed only for <=720px and <=5s, default 15fps keeps existing limits',()=>{
 const {editorOutputPolicy:p}=policy();
 assert.equal(p(720,30,5).valid,true);
 assert.equal(p(720,30,5.1).valid,false);
 assert.equal(p(1280,30,1).valid,false);
 assert.equal(p(1920,15,5).valid,true);
 assert.equal(p(1920,15,5.1).valid,false);
 assert.equal(p(720,15,10).valid,true);
 assert.equal(p(720,60,1).valid,false);
 assert.equal(p(720,30,.4).valid,false);
});
test('zoom contains selection, clamps to source and returns full extent when off',()=>{
 const {timelineViewport:v}=policy();
 for(const [duration,start,end] of [[300,140,145],[300,0,1],[300,298,300],[1,0,1]]){
  const w=v(duration,start,end,true);
  assert.ok(w.start>=0 && w.end<=duration);
  assert.ok(w.start<=start && w.end>=end);
 }
 assert.equal(v(300,140,145,false).end,300);
 assert.equal(v(300,140,145,false).start,0);
 assert.ok(v(300,140,145,true).end-v(300,140,145,true).start<=15);
});
test('current-position marking never shifts the opposite boundary or silently clamps',()=>{
 const {boundaryAtTime:b}=policy();
 assert.equal(b('start',1.26,0,3,10).start,1.3);
 assert.equal(b('end',2.34,0,3,10).end,2.3);
 assert.equal(b('start',2.9,0,3,10),null);
 assert.equal(b('end',.1,0,3,10),null);
 assert.equal(b('end',11,0,3,10),null);
});
test('30fps reverse and ping-pong preserve every selected frame and omit duplicate endpoints',()=>{
 const from=html.indexOf('function planReverseFrames('),to=html.indexOf('function outputDimensions(',from);
 const plan=runInNewContext(html.slice(from,to)+'\nplanModeFrames');
 for(const seconds of [.5,1,2.1,5])for(const mode of ['reverse','pingpong']){
  const p=plan(2,2+seconds,mode,30,60),n=Math.round(seconds*30),first=60;
  const actual=[];
  for(const part of p.segments){
   const start=Math.round(part.start*30);
   for(let i=0;i<part.frames;i++)actual.push(start+(part.direction==='forward'?i:part.frames-1-i));
  }
  const expected=mode==='reverse'?Array.from({length:n},(_,i)=>first+n-1-i):[
   ...Array.from({length:n},(_,i)=>first+i),...Array.from({length:n-2},(_,i)=>first+n-2-i)];
  assert.deepEqual(actual,expected);
  assert.equal(p.expectedDuration,expected.length/30);
 }
});

test('the editor accepts a half-second selection with fractional endpoints',()=>{
 const start=html.indexOf('function rangeInfo()');
 const end=html.indexOf('function sourceIsCurrent(',start);
 assert.ok(start>=0 && end>start);
 const settings=new Map([
  ['rangeStart',{value:'0.2'}],['rangeEnd',{value:'0.7'}],
  ['qualityInput',{value:'720'}],['modeInput',{value:'reverse'}],['audioInput',{value:'none'}],
 ]);
 const state={ready:true};
 const context={
  $:selector=>{
   const id=selector.slice(1);
   if(!settings.has(id)) settings.set(id,{setAttribute(){}});
   return settings.get(id);
  },
  state, video:{duration:8}, MAX_CLIP_SECONDS:10,
  PINGPONG_ENABLED:true, AUDIO_MUX_ENABLED:true, conversionController:null,
  timelineZoom:false, selectedFps:()=>30, outputDimensions:()=>({width:640,height:360}),
  ...policy(),
  chunkFrameLimit:()=>60, planModeFrames:()=>({
   segments:[{frames:15}],expectedDuration:.5,selectedStart:.2,selectedEnd:.7,
  }),
  syncTrimControls(){}, scheduleThumbnails(){},
  activeTimelineViewport:()=>({start:0,end:8}),
  translate:key=>key, format:key=>key, threadingReady:()=>true,
 };
 runInNewContext(html.slice(start,end)+'\nrangeInfo();',context);
 assert.equal(settings.get('reverseButton').disabled,false);
 assert.equal(settings.get('draftButton').disabled,false);
});


test('encoding locks all editor settings and output buttons',()=>{
 const start=html.indexOf('function rangeInfo()'),end=html.indexOf('function sourceIsCurrent(',start);
 const fields=new Map([
  ['rangeStart',{value:'0.2'}],['rangeEnd',{value:'0.7'}],
  ['qualityInput',{value:'720'}],['fpsInput',{value:'15'}],
  ['modeInput',{value:'reverse'}],['audioInput',{value:'reverse'}],
 ]);
 const $=selector=>{
  const key=selector.slice(1);
  if(!fields.has(key))fields.set(key,{setAttribute(){}});
  return fields.get(key);
 };
 const state={ready:true,audioPresent:true,audioChecked:true,inputTransport:'workerfs'};
 runInNewContext(html.slice(start,end)+'\nrangeInfo();',{
  $,state,video:{duration:6},MAX_CLIP_SECONDS:10,
  PINGPONG_ENABLED:true,AUDIO_MUX_ENABLED:true,conversionController:{},timelineZoom:false,
  selectedFps:()=>15,outputDimensions:()=>({width:640,height:360}),
  ...policy(),
  chunkFrameLimit:()=>30,planModeFrames:()=>({
   segments:[{frames:8}],expectedDuration:.5,selectedStart:.2,selectedEnd:.7,
  }),syncTrimControls(){},activeTimelineViewport:()=>({start:0,end:6}),
  translate:key=>key,format:key=>key,threadingReady:()=>true,
 });
 for(const id of ['rangeStart','rangeEnd','trimStartSlider','trimEndSlider','qualityInput',
   'fpsInput','selectFiveButton','markStartButton','markEndButton','timelineZoomButton','modeReverseButton',
   'modePingpongButton','modeInput','audioInput','audioReverseOption',
   'previewSelectionButton','draftButton','reverseButton']){
  assert.equal(fields.get(id).disabled,true,id+' was editable during conversion');
 }
 assert.equal(fields.get('restoreFpsButton').hidden,true);
});

test('invalid time fields clear a previous highlighted trim range',()=>{
 const a=html.indexOf('function syncTrimControls()'),b=html.indexOf('function moveTrimHandle(',a);
 const fields=new Map([
  ['rangeStart',{value:'0'}],['rangeEnd',{value:'5'}],
  ['trimStartSlider',{value:'0',min:'0',max:'10',setAttribute(){},removeAttribute(){}}],
  ['trimEndSlider',{value:'5',min:'0',max:'10',setAttribute(){},removeAttribute(){}}],
  ['trimSelectedTrack',{style:{left:'25%',width:'40%'}}],
  ['trimSummary',{textContent:''}],
 ]);
 const sync=runInNewContext(html.slice(a,b)+'\nsyncTrimControls;',{
  $:selector=>fields.get(selector.slice(1)),
  state:{ready:true},video:{duration:10},validSourceRange:policy().validSourceRange,
  activeTimelineViewport:()=>({start:0,end:10}),
  roundTrim:n=>Math.round(n*10)/10,
  format:()=> 'valid',translate:()=> 'invalid'
 });
 sync();
 assert.notEqual(fields.get('trimSelectedTrack').style.width,'0%');
 fields.get('rangeEnd').value='0.2';
 sync();
 assert.equal(fields.get('trimSelectedTrack').style.width,'0%');
 assert.equal(fields.get('trimSelectedTrack').style.left,'0%');
 assert.equal(fields.get('trimSummary').textContent,'invalid');
});

test('video and capture buttons have equal grid cells; fallback remains secondary',()=>{
 assert.match(html,/\.rc-drop \.button-row\{display:grid;grid-template-columns:repeat\(2,minmax\(0,1fr\)\)/);
 assert.match(html,/\.rc-drop \.button-row \.button\{display:flex;align-items:center;justify-content:center/);
 assert.match(html,/\.file-fallback-button \{ display:none;[^\n]*border:0;[^\n]*background:transparent;/);
});
