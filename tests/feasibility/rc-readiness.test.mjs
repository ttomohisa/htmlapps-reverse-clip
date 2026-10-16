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
  assert.match(rc,/P0 — mandatory/);
  assert.match(rc,/P1 \/ P2 — not unconditional initial-release blockers/);
  assert.match(rc,/initial Windows Chrome\/Android Chrome|Android Chrome H\.264/);
  assert.match(rc,/720p10s \/ 1080p5s/);
  assert.match(read('docs/release/REVISED_ACCEPTANCE_SCOPE.md'),/P0/);
  assert.match(rc,/actual screenshots/i);
  assert.match(rc,/iPhone/);
  assert.match(read('docs/release/REVISED_ACCEPTANCE_SCOPE.md'),/iPhoneは今回の公開対象としない/);
  assert.match(rc,/conditional local whole-file copy/);
  assert.match(rc,/64MiB/);
});
test('temporary pinned WASM does not masquerade as permanent GPL corresponding source',()=>{
  assert.equal(lock.kind,'experimental-dual-github-actions-artifact');
  assert.equal(lock.status,'temporary-not-release');
  assert.equal(lock.builderVersion,'1.10.6');
  assert.ok(lock.variants['single-thread'].assets['ffmpeg.wasm']);
  assert.ok(lock.variants['multi-thread'].assets['ffmpeg.wasm']);
  assert.match(rc,/source-complete GPL Builder distribution/);
  assert.match(read('README.md'),/v0\.9\.0 RC PREPARATION/);
  assert.match(read('README.ja.md'),/v0\.9\.0 公開前RC準備版/);
  assert.match(read('README-FIRST.txt'),/v0\.9\.0 — RC PREPARATION ONLY/);
  assert.match(read('VERIFY_OFFLINE.md'),/v0\.9\.0 RC PREPARATION/);
  assert.match(read('APP_SPEC.md'),/v0\.9\.0 RC準備中/);
});

test('reducing stress does not weaken input memory, privacy or stale-result safety',()=>{
  const html=read('src/index.template.html');
  assert.match(html,/connect-src 'none'/);
  assert.match(html,/const INPUT_MEMORY_LIMIT = 64 \* 1024 \* 1024;/);
  assert.match(html,/if \(file\.size > INPUT_MEMORY_LIMIT\)/);
  assert.match(html,/if \(!MOBILE_INPUT \|\| file\.size > INPUT_MEMORY_LIMIT\) return false;/);
  assert.match(html,/if\(file\.size>INPUT_MEMORY_LIMIT\)/);
  assert.match(html,/sourceIsCurrent\(file, generation\)/);
  assert.match(html,/function resetConversion\(\)/);
  assert.match(html,/function flowResultReady\(\)/);
  const policy=read('docs/release/REVISED_ACCEPTANCE_SCOPE.md');
  assert.match(policy,/64MiB以下/);
  assert.match(policy,/720p10秒/);
});
