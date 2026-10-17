import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
const read=p=>fs.readFileSync(new URL('../../'+p,import.meta.url),'utf8');
const lock=JSON.parse(read('coi-serviceworker.lock.json'));
const vendor=read('vendor/coi-serviceworker/coi-serviceworker.js');
test('MIT COI worker is SHA-256 pinned',()=>{
  assert.equal(lock.version,'0.1.7');
  assert.equal(lock.commit,'7b1d2a092d0d2dd2b7270b6f12f13605de26f214');
  assert.equal(crypto.createHash('sha256').update(vendor).digest('hex'),lock.sha256);
  assert.match(read('licenses/coi-serviceworker-MIT.txt'),/MIT License/);
});
test('ST/MT build plan is separate from Pages SW',()=>{
  const build=read('build-standalone.ps1');
  const prepare=read('scripts/prepare-pages.ps1');
  const src=read('src/index.template.html');
  for(const token of ['multiThreadOutput','__RUNTIME_VARIANT__','-Variant $Variant','reverse-runtime/$Variant'])
    assert.ok(build.includes(token),'build missing '+token);
  assert.ok(src.includes('threading:RUNTIME_VARIANT'));
  assert.ok(src.includes('function threadingReady()'));
  for(const token of ['pages-dist',"'mt'",'coi-serviceworker.js','window.coi','coepDegrade: () => false'])
    assert.ok(prepare.includes(token),'Pages staging missing '+token);
  assert.ok(prepare.includes('globalThis.crossOriginIsolated === false'));
});
test('generated ST/MT have separate runtime bundles',()=>{
  if(!fs.existsSync('dist/index.html')) return;
  const st=fs.readFileSync('dist/index.html','utf8');
  const mt=fs.readFileSync('dist/index.mt.html','utf8');
  assert.ok(st.includes('const RUNTIME_VARIANT = "single-thread";'));
  assert.ok(mt.includes('const RUNTIME_VARIANT = "multi-thread";'));
  for(const html of [st,mt]) {
    assert.ok(html.includes("connect-src 'none'"));
    assert.ok(!html.includes('coi-serviceworker.js'));
    assert.ok(html.includes('threading:RUNTIME_VARIANT'));
    assert.ok(!html.includes('__RUNTIME_VARIANT__'));
  }
  assert.ok(fs.existsSync('dist/index.self-extract.html'));
  assert.ok(fs.existsSync('dist/index.mt.self-extract.html'));
});
test('Pages serves ST root and MT only under /mt/',()=>{
  if (!fs.existsSync('pages-dist/index.html')) return;
  const st=fs.readFileSync('pages-dist/index.html','utf8');
  const mt=fs.readFileSync('pages-dist/mt/index.html','utf8');
  const sw=fs.readFileSync('pages-dist/mt/coi-serviceworker.js','utf8');
  assert.ok(st.includes('const RUNTIME_VARIANT = "single-thread";'));
  assert.ok(!st.includes('coi-serviceworker.js'));
  assert.ok(mt.includes('const RUNTIME_VARIANT = "multi-thread";'));
  assert.ok(mt.includes('globalThis.crossOriginIsolated === false'));
  assert.ok(mt.includes('sw.src = "./coi-serviceworker.js";'));
  assert.equal(sw,vendor);
  assert.ok(fs.existsSync('pages-dist/.nojekyll'));
});
