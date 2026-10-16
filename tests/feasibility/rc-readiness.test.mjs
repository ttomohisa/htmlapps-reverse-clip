import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
const read=p=>readFileSync(new URL('../../'+p,import.meta.url),'utf8');
const config=JSON.parse(read('app.config.json'));
const lock=JSON.parse(read('reverse-runtime.lock.json'));
const rc=read('docs/release/RC_CHECKLIST.md');
test('v0.9 RC preparation is not an approved release or passed gate',()=>{
  assert.equal(config.version,'0.9.0');
  assert.match(config.description,/RC PREPARATION.*G2.*G3.*OPEN/);
  assert.match(config.descriptionJa,/G2と公開前G3は未合格/);
  assert.match(rc,/PREPARATION \/ NOT APPROVED/);
  assert.match(rc,/Gate G3 NOT PASSED/);
  assert.match(read('docs/release/RELEASE_NOTES_DRAFT.md'),/NOT FOR PUBLICATION/);
  assert.match(read('CHANGELOG.md'),/\[0\.9\.0\].*not released/);
});
test('all 14 specified acceptance IDs are present with explicit blockers',()=>{
  for(let i=1;i<=14;i++)assert.ok(rc.includes('| A-'+String(i).padStart(2,'0')+' |'),'A-'+i);
  assert.match(rc,/KNOWN G2 DEVIATION/);
  assert.match(rc,/Actual screenshots/);
  assert.match(rc,/DEFERRED \/ NOT VERIFIED/);
});
test('temporary pinned WASM does not masquerade as permanent GPL corresponding source',()=>{
  assert.equal(lock.kind,'experimental-dual-github-actions-artifact');
  assert.equal(lock.status,'temporary-not-release');
  assert.equal(lock.builderVersion,'1.10.6');
  assert.ok(lock.variants['single-thread'].assets['ffmpeg.wasm']);
  assert.ok(lock.variants['multi-thread'].assets['ffmpeg.wasm']);
  assert.match(rc,/GPL corresponding-source/);
  assert.match(read('README.md'),/v0\.9\.0 RC PREPARATION/);
  assert.match(read('README.ja.md'),/v0\.9\.0 公開前RC準備版/);
});
