import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const read=p=>readFileSync(new URL('../../'+p,import.meta.url),'utf8');
const config=JSON.parse(read('app.config.json'));
const lock=JSON.parse(read('reverse-runtime.lock.json'));
const rc=read('docs/release/RC_CHECKLIST.md');
test('v0.9 RC preparation is not an approved release or passed gate',()=>{
  assert.equal(config.version,'0.9.0');
  assert.match(config.description,/forward-and-back MP4.*browser/);
  assert.match(config.descriptionJa,/動画はブラウザ内で処理します/);
  assert.doesNotMatch(config.description,/G2|G3|RC PREPARATION|not released/);
  assert.doesNotMatch(config.descriptionJa,/G2|G3|Draft|未合格/);
  assert.match(rc,/v0\.9\.0 merged to main, app NOT RELEASED/);
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
test('published Builder runtime is pinned but Reverse Clip app remains RC',()=>{
  assert.equal(lock.kind,'github-release-st-mt');
  assert.equal(lock.status,'release-approved');
  assert.equal(lock.builderVersion,'1.10.6');
  const notices=read('THIRD_PARTY_NOTICES.md');
  assert.ok(notices.includes(lock.builderCommit),'Third-party notices must match the compiled Builder commit');
  assert.ok(notices.includes('Builder version: **'+lock.builderVersion+'**'),'Third-party notices must show the current Builder version');
  assert.ok(notices.includes(lock.builderTag),'Third-party notices must identify the released Builder profile');
  assert.ok(notices.includes(lock.correspondingSourceAsset),'Corresponding source must be discoverable');
  assert.ok(notices.includes(lock.supplementalNoticeAsset),'GPL addendum must be discoverable');
  assert.ok(notices.includes(lock.wasmLicense),'Third-party notices must state the current WASM license');
  assert.match(notices,/single-thread \(ST\).*multi-thread \(MT\/pthreads\)/s);
  assert.doesNotMatch(notices,/Builder 1\.10\.4|11715866319/);
  assert.ok(lock.variants['single-thread'].assets['ffmpeg.wasm']);
  assert.ok(lock.variants['multi-thread'].assets['ffmpeg.wasm']);
  assert.match(rc,/publicly obtainable matching GPL source/);
  assert.equal(lock.correspondingSourceSha256,'9ceb47a5f46fb3484f8b1f6a8fa37e6d0dc4144aa09d78939ac9d23e8ab5ce92');
  assert.equal(lock.supplementalNoticeSha256,'e011d66e3451dbf5ffa5f67f26636749664a69d285a3cfc665a71e36635e15f3');
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

test('actual JA/EN desktop and mobile screenshots match the reviewed CI manifest',()=>{
  const evidence=JSON.parse(read('docs/release/RC_SCREENSHOT_ASSET_MANIFEST.json'));
  assert.equal(evidence.artifact_run_id,38944766865);
  assert.equal(evidence.evidence.runtime,'single-thread Chrome (not Android/iPhone QA)');
  const cases=[
    ['reverse-clip-desktop-ja.png','assets/screenshot.png',1360,900,'README.ja.md'],
    ['reverse-clip-desktop-en.png','assets/screenshot-en.png',1360,900,'README.md'],
    ['reverse-clip-mobile-ja.png','assets/screenshot-mobile.png',390,844,'README.ja.md'],
    ['reverse-clip-mobile-en.png','assets/screenshot-mobile-en.png',390,844,'README.md']
  ];
  const records=new Map(evidence.evidence.screenshots.map(x=>[x.file,x]));
  assert.equal(records.size,4);
  for(const [original,target,width,height,readme] of cases){
    const record=records.get(original);
    assert.ok(record,original);
    const bytes=readFileSync(new URL('../../'+target,import.meta.url));
    assert.ok(bytes.subarray(0,8).equals(Buffer.from('89504e470d0a1a0a','hex')));
    assert.equal(bytes.readUInt32BE(16),width,target);
    assert.equal(bytes.readUInt32BE(20),height,target);
    assert.equal(bytes.length,record.bytes,target);
    assert.equal(createHash('sha256').update(bytes).digest('hex'),record.sha256,target);
    assert.ok(read(readme).includes('('+target+')'),readme+' missing '+target);
  }
  // Verified viewport screenshots are not falsely presented as phone hardware QA.
  assert.match(read('README.md'),/not physical Android device certification/);
  assert.match(read('README.ja.md'),/Android実機による動作確認を表す画像ではありません/);
  assert.match(rc,/A-13 screenshots PASS/);
  assert.equal(lock.status,'release-approved');
});
