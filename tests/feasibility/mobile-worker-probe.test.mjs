import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const html=readFileSync(new URL('../../src/index.template.html',import.meta.url),'utf8');
const from=html.indexOf('function probeMobileWorkerRead(');
const to=html.indexOf('function prepareMobileInput(',from);
assert.ok(from>0&&to>from,'Mobile Worker input probe must be present');
const source=html.slice(from,to);

function harness(response='yes') {
  const observed={created:0,terminated:0,revoked:[],posted:[],timeouts:0};
  class FakeBlob {
    constructor(parts,options) { this.parts=parts;this.type=options.type; }
  }
  class FakeWorker {
    constructor(url) {
      if(response==='constructor-error')throw new Error('No Worker available');
      observed.created++;
      this.url=url;
    }
    postMessage(file) {
      observed.posted.push(file);
      if(response==='yes'||response==='no')queueMicrotask(()=>{
        this.onmessage?.({data:{ok:response==='yes'}});
      });
      if(response==='post-error')throw new Error('Cannot clone provider File');
    }
    terminate() {observed.terminated++;}
  }
  const context={
    Worker:FakeWorker,Blob:FakeBlob,
    URL:{createObjectURL:()=> 'blob:probe-test',revokeObjectURL:x=>observed.revoked.push(x)},
    setTimeout:(fn,ms)=>{observed.timeouts++;return setTimeout(fn,ms);},
    clearTimeout,Math,Promise
  };
  const probe=runInNewContext(source+'\nprobeMobileWorkerRead',{...context},{timeout:1000});
  return {probe,observed};
}

test('local Android File passes a tiny Worker test without sending or reading full bytes',async()=>{
  const {probe,observed}=harness('yes');
  const file={size:12345678,arrayBuffer(){throw new Error('full-file copy forbidden')}};
  const passed=await probe(file,new AbortController().signal);
  assert.equal(passed,true);
  assert.equal(observed.posted.length,1);
  assert.strictEqual(observed.posted[0],file);
  assert.equal(observed.terminated,1);
  assert.deepEqual(observed.revoked,['blob:probe-test']);
});

test('photo provider Worker read rejection retains bounded fallback decision',async()=>{
  const {probe,observed}=harness('no');
  assert.equal(await probe({size:1234},new AbortController().signal),false);
  assert.equal(observed.terminated,1);
  assert.deepEqual(observed.revoked,['blob:probe-test']);
  const section=html.slice(html.indexOf('function prepareMobileInput('),html.indexOf('function isWorkerFileReadError('));
  assert.ok(section.includes("if(canRead){"));
  assert.ok(section.includes("state.inputTransport='workerfs'"));
  assert.ok(section.includes('const copy=await copySelectedFile(file,generation);'));
  assert.ok(section.includes("state.inputTransport='memory'"));
  assert.ok(section.includes('file.size > INPUT_MEMORY_LIMIT'));
});

test('cancel aborts the outstanding Worker without reviving a replaced source',async()=>{
  const {probe,observed}=harness('pending');
  const controller=new AbortController();
  const pending=probe({size:16},controller.signal);
  controller.abort();
  assert.equal(await pending,false);
  assert.equal(observed.terminated,1);
  assert.deepEqual(observed.revoked,['blob:probe-test']);
  assert.ok(html.includes('if(state.inputProbeController)state.inputProbeController.abort();'));
  assert.ok(html.includes("!sourceIsCurrent(file,generation)||state.sourcePhase!=='inspecting'"));
  assert.ok(html.includes('if(state.inputProbeController===controller)state.inputProbeController=null;'));
});

test('disabled Worker, already-aborted probe and postMessage failure all fail closed',async()=>{
  const before=new AbortController();
  before.abort();
  const direct=harness('yes');
  assert.equal(await direct.probe({size:5},before.signal),false);
  assert.equal(direct.observed.created,0);
  for(const response of ['constructor-error','post-error']) {
    const {probe,observed}=harness(response);
    assert.equal(await probe({size:5}),false,response);
    assert.equal(observed.revoked.length,1,response);
    assert.equal(observed.terminated,response==='post-error'?1:0,response);
  }
});

test('worker probe reads only head and tail, and cleans up timeout/event/URL',()=>{
  assert.match(source,/readAsArrayBuffer\(file\.slice\(0,32\)\)/);
  assert.match(source,/readAsArrayBuffer\(file\.slice\(Math\.max\(0,file\.size-32\),file\.size\)\)/);
  assert.ok(source.includes('timer=setTimeout(()=>finish(false),2500)'));
  assert.ok(source.includes("worker.onerror=()=>finish(false)"));
  assert.ok(source.includes("worker.onmessageerror=()=>finish(false)"));
  assert.ok(source.includes('signal?.removeEventListener(\'abort\',abort);'));
  assert.ok(source.includes('URL.revokeObjectURL(url)'));
});
