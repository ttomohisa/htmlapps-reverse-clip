import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

// Test the SAME pure planner that the standalone HTML executes.
const html = readFileSync(new URL('../../src/index.template.html',import.meta.url),'utf8');
const lo=html.indexOf('function planReverseFrames(');
const hi=html.indexOf('function outputDimensions(',lo);
assert.ok(lo>0 && hi>lo,'Missing app timeline planner');
const plan=runInNewContext(html.slice(lo,hi)+'\nplanReverseFrames',{},{timeout:1000});

function validate(start,end,fps=15){
  const p=plan(start,end,fps);
  let count=0,cursor=p.selectedEnd;
  for(const segment of p.segments){
    assert.ok(segment.frames>=2 && segment.frames<=2*fps);
    assert.ok(Math.abs(segment.start+segment.duration-cursor)<0.00001);
    cursor=segment.start;
    count+=segment.frames;
  }
  assert.ok(Math.abs(cursor-p.selectedStart)<0.00001);
  assert.equal(count,p.frameCount);
  assert.ok(Math.abs(p.expectedDuration-count/fps)<1e-10);
  assert.ok(Math.abs(p.selectedStart-start)<=.5/fps+.00001);
  assert.ok(Math.abs(p.selectedEnd-end)<=.5/fps+.00001);
  return p;
}
test('Android picker stage and Worker read recovery remain part of the app',()=>{
  assert.ok(html.includes('function prepareMobileInput(file)'));
  assert.ok(html.includes('function attachSourcePreview(blob)'));
  assert.ok(html.includes('function copySelectedFile(file, generation)'));
  assert.ok(html.includes('function isWorkerFileReadError(error)'));
});
test('single 1s segment remains supported',()=>{
  const p=validate(0,1);
  assert.equal(p.segments.length,1);
  assert.equal(p.frameCount,15);
});
test('5s splits at 2s boundaries, in reverse chronology',()=>{
  const p=validate(0,5);
  assert.equal(p.frameCount,75);
  assert.equal(p.segments.length,3);
  assert.deepEqual(Array.from(p.segments,s=>s.frames),[15,30,30]);
  assert.ok(p.segments[0].start>p.segments[1].start);
});
test('31 frames never produce an unsupported 1-frame tail',()=>{
  const p=validate(0,31/15);
  assert.equal(p.segments.length,2);
  assert.deepEqual(Array.from(p.segments,s=>s.frames),[2,29]);
});
test('10s uses exactly five 2-second reverse-chronological segments',()=>{
  const p=validate(0,10);
  assert.equal(p.frameCount,150);
  assert.equal(p.segments.length,5);
  assert.deepEqual(Array.from(p.segments,s=>s.frames),[30,30,30,30,30]);
  assert.equal(p.segments[0].start,8);
});
test('9.9s snaps to 149 encoded frames across five segments',()=>{
  const p=validate(0,9.9);
  assert.equal(p.frameCount,149);
  assert.deepEqual(Array.from(p.segments,s=>s.frames),[29,30,30,30,30]);
});
test('non-zero starting time can reverse a ten-second window',()=>{
  const p=validate(2.5,12.5);
  assert.equal(p.frameCount,150);
  assert.ok(Math.abs(p.segments[0].start - 10.533333) < 0.00001); // 2.5s snaps up to frame 38/15
});
test('every tenths-of-a-second duration yields contiguous safe boundaries',()=>{
  for(let i=5;i<=100;i++){
    const duration=i/10;
    const p=validate(.1,.1+duration);
    assert.ok(p.segments.length<=8);
  }
});
test('app passes expected frame counts to segment and join runners',()=>{
  assert.ok(html.includes("'--frames',String(chunk.frames)"));
  assert.ok(html.includes("'--expected-frames',String(plan.frameCount)"));
});
test('non-frame aligned bounds remain contiguous after rounding',()=>{
  const p=validate(.1,4.93);
  assert.ok(p.segments.length>=2&&p.segments.length<=3);
});
test('minimum 0.5-second range is accepted',()=>validate(0,.5));
test('invalid bounds are rejected',()=>{
  for(const [a,b] of [[-.1,.9],[0,.3],[0,10.1],[NaN,1],[0,Infinity]])
    assert.throws(()=>plan(a,b,15),/Select 0\.5/);
});

