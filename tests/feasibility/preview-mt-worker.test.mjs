import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import worker from '../../scripts/preview-mt-worker.mjs';

const root=new URL('../../',import.meta.url);
const config=JSON.parse(readFileSync(new URL('wrangler.preview.jsonc',root),'utf8'));
const headerNames=[
  ['Cross-Origin-Opener-Policy','same-origin'],
  ['Cross-Origin-Embedder-Policy','require-corp'],
  ['Cross-Origin-Resource-Policy','same-origin'],
];
function makeAssets(status=200) {
  const calls=[];
  const env={ASSETS:{fetch:async request=>{
    calls.push(request.url);
    return new Response('const RUNTIME_VARIANT = "multi-thread";',{status,
      headers:{'Content-Type':'text/html; charset=utf-8',
        'Content-Security-Policy':"default-src 'self'; connect-src 'none'",
        'Cache-Control':'public, max-age=120'}});
  }}};
  return {env,calls};
}
test('Wrangler invokes the Preview Worker only for actual MT HTML entries',()=>{
  assert.equal(config.main,'./scripts/preview-mt-worker.mjs');
  assert.equal(config.assets.directory,'./dist');
  assert.equal(config.assets.binding,'ASSETS');
  assert.equal(config.assets.run_worker_first,true); // Worker-first all assets, isolate MT only.
});
test('both MT Preview HTML entries get isolation without changing CSP or body',async()=>{
  for(const path of config.assets.run_worker_first){
    const {env,calls}=makeAssets();
    const url='https://example.workers.dev'+path;
    const response=await worker.fetch(new Request(url),env);
    assert.equal(response.status,200);
    assert.equal(response.headers.get('X-RC-Preview-Worker'),'active');
    assert.deepEqual(calls,[url]);
    for(const [name,value] of headerNames)assert.equal(response.headers.get(name),value);
    assert.equal(response.headers.get('Content-Security-Policy'),
      "default-src 'self'; connect-src 'none'");
    assert.equal(response.headers.get('Cache-Control'),'public, max-age=120');
    assert.match(await response.text(),/RUNTIME_VARIANT = "multi-thread"/);
  }
});
test('ST root and unrelated assets never acquire isolation headers',async()=>{
  for(const path of ['/','/index.html','/favicon.svg','/index.mt.html/extra']){
    const {env}=makeAssets();
    const response=await worker.fetch(new Request('https://example.workers.dev'+path),env);
    for(const [name] of headerNames)assert.equal(response.headers.get(name),null);
    assert.equal(response.headers.get('X-RC-Preview-Worker'),'active');
  }
});
test('missing MT asset does not advertise a valid isolated page',async()=>{
  const {env}=makeAssets(404);
  const response=await worker.fetch(new Request('https://example.workers.dev/index.mt.html'),env);
  assert.equal(response.status,404);
  for(const [name] of headerNames)assert.equal(response.headers.get(name),null);
});
