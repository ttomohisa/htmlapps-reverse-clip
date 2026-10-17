import test from 'node:test';
import assert from 'node:assert/strict';
import {spawnSync} from 'node:child_process';
import {readFileSync,writeFileSync,copyFileSync,existsSync,mkdirSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve} from 'node:path';
import {createHash} from 'node:crypto';

const existing=JSON.parse(readFileSync('reverse-runtime.lock.json','utf8'));
const imported=resolve('scripts/prepare-video-reverse-runtime.ps1');
const h=p=>createHash('sha256').update(readFileSync(p)).digest('hex');
const tag='video-reverse-v1.10.6';

function pwsh(script,...args){
  const p=spawnSync('pwsh',['-NoProfile','-NonInteractive','-File',script,...args],
    {encoding:'utf8',timeout:30000,env:{...process.env, GITHUB_TOKEN:'', GH_TOKEN:''}});
  assert.equal(p.error,undefined,p.error?.message);
  return p;
}
function assertSuccess(p,context){
  assert.equal(p.status,0,context+'\n'+p.stdout+'\n'+p.stderr);
}
function populateVariant(dir,variant){
  const cache=resolve('.cache/reverse-runtime',variant);
  for(const name of ['ffmpeg.js','ffmpeg.wasm','browser-ffmpeg.js','manifest.json'])
    assert.ok(existsSync(join(cache,name)),cache+' missing '+name);
  const staged=join(dir,'staged-'+variant);
  mkdirSync(join(staged,'LICENSES'),{recursive:true});
  for(const name of ['ffmpeg.js','ffmpeg.wasm','browser-ffmpeg.js','manifest.json'])
    copyFileSync(join(cache,name),join(staged,name));
  // Synthetic license text is used only for the importer transport test.
  // It is NOT a publication archive, GPL compliance proof or reviewed source.
  writeFileSync(join(staged,'LICENSES','FFmpeg-COPYING.GPLv2'),'synthetic GPL fixture');
  writeFileSync(join(staged,'LICENSES','x264-COPYING'),'synthetic x264 fixture');
  writeFileSync(join(staged,'LICENSES','Emscripten-LICENSE'),'synthetic Emscripten fixture');
  writeFileSync(join(staged,'THIRD_PARTY_NOTICES.md'),'synthetic test notice');
  writeFileSync(join(staged,'BUILDINFO.txt'),'synthetic test buildinfo');
  const zipScript=join(dir,'zip-fixture.ps1');
  const zip=join(dir,`ffmpeg-wasm-video-reverse-${variant}-v1.10.6.zip`);
  assertSuccess(pwsh(zipScript,'-InputPath',staged,'-OutputPath',zip),'fixture ZIP generation');
  return {zip,sha:h(zip),variant};
}

test('offline mocked Release importer verifies BOTH ST/MT source, GPL notice, ZIP and cache',()=>{
  // Test only after the standard Windows build has resolved pinned ST/MT
  // runtime bytes. No GitHub Release exists; all network calls are mocked.
  const tmp=mkdtempSync(join(tmpdir(),'rc-public-release-mock-'));
  try{
    const app=join(tmp,'app'),scripts=join(app,'scripts'),assets=join(tmp,'assets');
    mkdirSync(scripts,{recursive:true});mkdirSync(assets);
    copyFileSync(imported,join(scripts,'prepare-video-reverse-runtime.ps1'));
    writeFileSync(join(tmp,'zip-fixture.ps1'),`param([string]$InputPath,[string]$OutputPath)
$ErrorActionPreference = 'Stop'
Compress-Archive -Path (Join-Path $InputPath '*') -DestinationPath $OutputPath -CompressionLevel Fastest -Force
`);
    const sourceName='ffmpeg-wasm-sources-v1.10.6.tar.gz';
    const noticeName='VIDEO_REVERSE_LICENSE_ADDENDUM.md';
    writeFileSync(join(assets,sourceName),'synthetic corresponding-source transport fixture (NOT a true source tarball)');
    writeFileSync(join(assets,noticeName),'video-reverse x264 GPL-2.0-or-later synthetic notice transport fixture');
    const variants={};
    for(const variant of ['single-thread','multi-thread']){
      const {zip,sha}=populateVariant(tmp,variant);
      const name=`ffmpeg-wasm-video-reverse-${variant}-v1.10.6.zip`;
      copyFileSync(zip,join(assets,name));
      variants[variant]={
        ...existing.variants[variant],
        releaseAsset:name,
        releaseArchiveSha256:sha
      };
    }
    const release={
      ...existing,
      kind:'github-release-st-mt',
      status:'release-approved',
      builderTag:tag,
      correspondingSourceAsset:sourceName,
      correspondingSourceSha256:h(join(assets,sourceName)),
      supplementalNoticeAsset:noticeName,
      supplementalNoticeSha256:h(join(assets,noticeName)),
      variants,
    };
    delete release.workflowRunId;
    delete release.artifactId;
    writeFileSync(join(app,'reverse-runtime.lock.json'),JSON.stringify(release),'utf8');
    const wrapper=join(tmp,'import-with-mocked-public-release.ps1');
    writeFileSync(wrapper,`param([string]$ScriptPath,[string]$Variant)
$ErrorActionPreference = 'Stop'
function Invoke-WebRequest {
  param([string]$Uri,[switch]$UseBasicParsing,[string]$OutFile)
  if ($env:RC_TEST_NO_WEB -eq '1') { throw 'Unexpected external download: cached release was not honored' }
  $prefix = 'https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/download/video-reverse-v1.10.6/'
  if (-not $Uri.StartsWith($prefix,[StringComparison]::Ordinal)) {
    throw "Unexpected external URL $Uri"
  }
  $file = $Uri.Substring($prefix.Length)
  if ($file -notin @('ffmpeg-wasm-sources-v1.10.6.tar.gz','VIDEO_REVERSE_LICENSE_ADDENDUM.md',
    'ffmpeg-wasm-video-reverse-single-thread-v1.10.6.zip',
    'ffmpeg-wasm-video-reverse-multi-thread-v1.10.6.zip')) {
    throw "Unexpected Release asset: $file"
  }
  Copy-Item -LiteralPath (Join-Path $env:RC_TEST_ASSETS $file) -Destination $OutFile -Force
}
. $ScriptPath -Variant $Variant
`);
    const mockEnv=assets;
    for(const variant of ['single-thread','multi-thread']){
      const p=spawnSync('pwsh',['-NoProfile','-NonInteractive','-File',wrapper,
          '-ScriptPath',join(scripts,'prepare-video-reverse-runtime.ps1'),
          '-Variant',variant],{
          encoding:'utf8',timeout:30000,
          env:{...process.env,GITHUB_TOKEN:'',GH_TOKEN:'',RC_TEST_ASSETS:mockEnv}
        });
      assertSuccess(p,'simulated public Release import '+variant);
      const cache=join(app,'.cache','reverse-runtime',variant);
      const proof=JSON.parse(readFileSync(join(cache,'verified-release-archive.json'),'utf8'));
      assert.equal(proof.tag,tag);
      assert.equal(proof.sha256,variants[variant].releaseArchiveSha256);
      assert.equal(proof.sourceSha256,release.correspondingSourceSha256);
      assert.equal(proof.noticeSha256,release.supplementalNoticeSha256);
      for(const name of ['ffmpeg.js','ffmpeg.wasm','browser-ffmpeg.js'])
        assert.equal(h(join(cache,name)), name==='browser-ffmpeg.js'?
          release.browserRuntimeSha256:existing.variants[variant].assets[name]);
    }
    // A validated cache must be reusable with NO network request.
    const p=spawnSync('pwsh',['-NoProfile','-NonInteractive','-File',wrapper,
        '-ScriptPath',join(scripts,'prepare-video-reverse-runtime.ps1'),
        '-Variant','single-thread'],{
        encoding:'utf8',timeout:20000,
        env:{...process.env,GITHUB_TOKEN:'',GH_TOKEN:'',RC_TEST_ASSETS:mockEnv,
          RC_TEST_NO_WEB:'1'}
      });
    assertSuccess(p,'offline verified-cache reuse');
    assert.match(p.stdout,/Using verified cached single-thread runtime/);
  }finally{
    rmSync(tmp,{recursive:true,force:true});
  }
});
