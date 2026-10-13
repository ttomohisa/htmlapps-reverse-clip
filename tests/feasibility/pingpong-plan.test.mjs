import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

// The exact same pure function that the ST/MT standalone HTML executes.
const html=readFileSync(new URL('../../src/index.template.html',import.meta.url),'utf8');
const lo=html.indexOf('function planReverseFrames(');
const hi=html.indexOf('function outputDimensions(',lo);
assert.ok(lo>=0 && hi>lo,'Timeline planner not found');
const planModeFrames=runInNewContext(html.slice(lo,hi)+'\nplanModeFrames',{},{timeout:1000});

function validatePingpong(start,end,fps=15){
  const plan=planModeFrames(start,end,'pingpong',fps);
  const first=Math.round(start*fps);
  const last=Math.round(end*fps);
  const n=last-first;
  const expected=[
    ...Array.from({length:n},(_,i)=>first+i),
    ...Array.from({length:n-2},(_,i)=>last-2-i)
  ];
  const frames=[];
  for(const part of plan.segments){
    assert.equal(part.direction==='forward'||part.direction==='reverse',true);
    assert.ok(part.frames>=2 && part.frames<=2*fps,part);
    assert.ok(part.duration>0 && part.duration<=2+1e-5,part);
    const from=Math.round(part.start*fps);
    if(part.direction==='forward'){
      for(let i=0;i<part.frames;i++)frames.push(from+i);
    }else{
      for(let i=part.frames-1;i>=0;i--)frames.push(from+i);
    }
  }
  assert.deepEqual(frames,expected,'invalid frame order at source, turnaround or loop boundary');
  assert.equal(plan.frameCount,2*n-2);
  assert.equal(plan.sourceFrames,n);
  assert.equal(plan.segments.length,Math.ceil(n/(2*fps))*2);
  assert.equal(plan.mode,'pingpong');
  assert.ok(Math.abs(plan.expectedDuration - (2*n-2)/fps)<1e-10);
  assert.equal(frames[0],first);
  assert.equal(frames[n-1],last-1);
  assert.equal(frames[n],last-2);
  assert.equal(frames.at(-1),first+1);
  for(let i=1;i<frames.length;i++)
    assert.equal(Math.abs(frames[i]-frames[i-1]),1,'stutter or skipped frame: '+i);
  assert.ok(plan.segments.length<=16);
  return plan;
}

test('0.5s minimum ping-pong has one 8-frame forward and six-frame return',()=>{
  const p=validatePingpong(0,.5);
  assert.equal(p.sourceFrames,8);
  assert.equal(p.frameCount,14);
  assert.deepEqual(Array.from(p.segments,x=>x.frames),[8,6]);
});
test('1s 15fps marker timeline contains no duplicated turning or loop frame',()=>{
  const p=validatePingpong(0,1);
  assert.equal(p.frameCount,28);
  assert.deepEqual(Array.from(p.segments,x=>x.frames),[15,13]);
});
test('31-frame selection is balanced: no isolated 1-frame endpoint chunks',()=>{
  const p=validatePingpong(0,31/15);
  assert.deepEqual(Array.from(p.segments,x=>x.frames),[16,15,14,15]);
  assert.equal(p.frameCount,60);
});
test('5s selection (75 frames) emits 148 frames and <=6 chunks',()=>{
  const p=validatePingpong(.5,5.5);
  assert.equal(p.frameCount,148);
  assert.equal(p.segments.length,6);
});
test('10s maximum (150 frames) emits 298 frames in exactly ten 2s-bounded chunks',()=>{
  const p=validatePingpong(0,10);
  assert.equal(p.frameCount,298);
  assert.equal(p.segments.length,10);
});
test('all tenths-of-second ranges avoid duplicate turn/end frames and 1-frame chunks',()=>{
  for(let n=5;n<=100;n++)validatePingpong(.1,.1+n/10);
});
test('non-aligned source start/end still share one frame-exact timeline',()=>{
  validatePingpong(.13,3.47);
  validatePingpong(1.53,11.53);
  validatePingpong(.03,.53);
});
test('reverse mode is still the original single-direction planner',()=>{
  const p=planModeFrames(0,1,'reverse',15);
  assert.equal(p.mode,'reverse');
  assert.equal(p.sourceFrames,p.frameCount);
  assert.equal(p.frameCount,15);
  assert.deepEqual(Array.from(p.segments,x=>x.frames),[15]);
});
test('invalid modes and out-of-range selections fail closed',()=>{
  assert.throws(()=>planModeFrames(0,1,'not-a-mode',15),/Unknown conversion mode/);
  for(const [start,end]of [[-1,1],[0,.2],[0,10.2],[0,Infinity]])
    assert.throws(()=>planModeFrames(start,end,'pingpong',15),/Select 0\.5/);
});
test('UI gate and directional CLI are only enabled by the verified binary lock',()=>{
  const build=readFileSync(new URL('../../build-standalone.ps1',import.meta.url),'utf8');
  assert.ok(build.includes("'__PINGPONG_ENABLED__'")||
            build.includes('"__PINGPONG_ENABLED__"'));
  assert.ok(html.includes('const PINGPONG_ENABLED = __PINGPONG_ENABLED__;'));
  assert.ok(html.includes("mode==='pingpong'?['--direction',chunk.direction]"));
  assert.ok(html.includes("'--expected-frames',String(plan.frameCount)"));
  assert.ok(html.includes('modeAvailable'));
  assert.ok(html.includes("if(mode==='pingpong' && !PINGPONG_ENABLED)"));
});
