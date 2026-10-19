import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync, writeFileSync, copyFileSync, mkdirSync, mkdtempSync, rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join, resolve} from 'node:path';
import {spawnSync} from 'node:child_process';

const source=resolve('scripts/prepare-video-reverse-runtime.ps1');
const current=JSON.parse(readFileSync('reverse-runtime.lock.json','utf8'));
const sha='a'.repeat(64);
function releaseCandidate(kind,status){
  return {
    ...current,
    kind, status,
    builderTag:'video-reverse-v1.10.6',
    correspondingSourceAsset:'ffmpeg-wasm-sources-v1.10.6.tar.gz',
    correspondingSourceSha256:sha,
    supplementalNoticeAsset:'VIDEO_REVERSE_LICENSE_ADDENDUM.md',
    supplementalNoticeSha256:sha,
    variants:{
      'single-thread':{
        ...current.variants['single-thread'],
        releaseAsset:'ffmpeg-wasm-video-reverse-single-thread-v1.10.6.zip',
        releaseArchiveSha256:sha,
      },
      'multi-thread':{
        ...current.variants['multi-thread'],
        releaseAsset:'ffmpeg-wasm-video-reverse-multi-thread-v1.10.6.zip',
        releaseArchiveSha256:sha,
      },
    },
  };
}
function assertRejectedBeforeNetwork(lock,message){
  const dir=mkdtempSync(join(tmpdir(),'rc-proposed-lock-'));
  try{
    const scripts=join(dir,'scripts');
    mkdirSync(scripts);
    copyFileSync(source,join(scripts,'prepare-video-reverse-runtime.ps1'));
    writeFileSync(join(dir,'reverse-runtime.lock.json'),JSON.stringify(lock),'utf8');
    // The import script must reject these states *before* any external fetch.
    const proc=spawnSync('pwsh',[
      '-NoProfile','-NonInteractive','-File',
      join(scripts,'prepare-video-reverse-runtime.ps1'),
      '-Variant','single-thread'
    ],{encoding:'utf8',timeout:15000,env:{...process.env,GITHUB_TOKEN:'',GH_TOKEN:''}});
    assert.equal(proc.error,undefined,proc.error?.message);
    assert.notEqual(proc.status,0,'Review-only lock unexpectedly imported');
    const output=proc.stdout+'\n'+proc.stderr;
    assert.match(output,message);
    assert.doesNotMatch(output,/\[Reverse WASM\] Downloading|Verifying corresponding source/);
  } finally {
    rmSync(dir,{recursive:true,force:true});
  }
}
test('staged non-activatable kind is rejected by actual PowerShell importer',()=>{
  assert.equal(current.status,'release-approved');
  assertRejectedBeforeNetwork(
    releaseCandidate('review-only-proposed-github-release-st-mt','review-only-not-published'),
    /Unsupported reverse runtime source kind/
  );
});
test('published-shaped kind still rejects review-only status before any network',()=>{
  assertRejectedBeforeNetwork(
    releaseCandidate('github-release-st-mt','review-only-not-published'),
    /Public Builder Release import requires explicit release-approved status/
  );
});
test('approved status with invalid GPL sidecar hash rejects before network',()=>{
  const candidate=releaseCandidate('github-release-st-mt','release-approved');
  candidate.supplementalNoticeSha256='invalid';
  assertRejectedBeforeNetwork(candidate,
    /Invalid pinned Builder Release version, profile tag, hashes, GPL notice or source metadata/
  );
});
