import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
const html=readFileSync(new URL('../../src/index.template.html',import.meta.url),'utf8');
function policy(){
 const start=html.indexOf('function editorOutputPolicy('), end=html.indexOf('// EDITOR POLICY END',start);
 assert.ok(start>=0 && end>start,'editor policies are defined');
 return runInNewContext(html.slice(start,end)+'\n({editorOutputPolicy,timelineViewport,boundaryAtTime})');
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
