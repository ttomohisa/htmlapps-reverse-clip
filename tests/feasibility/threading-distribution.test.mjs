import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import crypto from 'node:crypto';
import zlib from 'node:zlib';
const read = p=>fs.readFileSync(p,'utf8');
const lock=JSON.parse(read('reverse-runtime.lock.json'));
function extractJson(html,name) {
  const marker='const '+name+' = ';
  const pos=html.indexOf(marker);
  assert.ok(pos>=0,name+' must be embedded');
  assert.equal(html.indexOf(marker,pos+marker.length),-1,name+' duplicated');
  const start=html.indexOf('{',pos+marker.length);
  let inString=false,escape=false,depth=0;
  for(let i=start;i<html.length;i++){
    const c=html[i];
    if(inString){
      if(escape)escape=false;
      else if(c==='\\')escape=true;
      else if(c==='"')inString=false;
      continue;
    }
    if(c==='"'){inString=true;continue;}
    if(c==='{')depth++;
    else if(c==='}'&&--depth===0)return JSON.parse(html.slice(start,i+1));
  }
  throw new Error('Unterminated '+name);
}
function hash(buf){return crypto.createHash('sha256').update(buf).digest('hex');}
for(const [threading,path] of [['single-thread','dist/index.html'],['multi-thread','dist/index.mt.html']]){
  test('actual '+threading+' HTML contains only a verified dedicated WASM',()=>{
    const html=read(path);
    assert.ok(html.includes('const RUNTIME_VARIANT = "'+threading+'";'));
    const manifest=extractJson(html,'BUILD_MANIFEST');
    assert.equal(manifest.runtime.threading,threading);
    assert.equal(manifest.runtime.profile,'video-reverse');
    const enabled=Array.isArray(lock.features)&&lock.features.includes('pingpong');
    assert.equal(manifest.runtime.pingpongEnabled,enabled);
    const audioEnabled=Array.isArray(lock.features)&&lock.features.includes('audio-mux');
    assert.equal(manifest.runtime.audioMuxEnabled,audioEnabled);
    assert.ok(html.includes('const AUDIO_MUX_ENABLED = '+String(audioEnabled)+';'));
    assert.ok(html.includes('const PINGPONG_ENABLED = '+String(enabled)+';'));
    assert.equal(manifest.runtime.requiresCrossOriginIsolation,threading==='multi-thread');
    const embedded=extractJson(html,'assetBundle');
    const assets=embedded.dependencies['reverse-wasm'].assets;
    const p=lock.variants[threading];
    for(const [name,key] of [['ffmpeg.js','coreJs'],['ffmpeg.wasm','coreWasm'],['browser-ffmpeg.js','runtimeJs']]){
      const asset=assets[key];
      assert.ok(asset?.base64);
      assert.ok(asset.storedBytes>0&&asset.originalBytes>0);
      const stored=Buffer.from(asset.base64,'base64');
      assert.equal(stored.length,asset.storedBytes);
      const actual=asset.compression==='gzip'?zlib.gunzipSync(stored):stored;
      assert.equal(actual.length,asset.originalBytes);
      assert.equal(hash(actual),name==='browser-ffmpeg.js'?lock.browserRuntimeSha256:p.assets[name]);
    }
    assert.ok(html.includes("connect-src 'none'"));
    assert.ok(html.includes("worker-src 'self' blob:"));
    assert.ok(!html.includes('coi-serviceworker.js'));
    assert.ok(!html.includes('__RUNTIME_VARIANT__'));
  });
}
test('both variants require the same Builder commit but distinct binaries',()=>{
  assert.equal(lock.schemaVersion,2);
  assert.equal(lock.profile,'video-reverse');
  assert.match(lock.builderCommit,/^[a-f0-9]{40}$/);
  assert.notEqual(lock.variants['single-thread'].assets['ffmpeg.wasm'],
    lock.variants['multi-thread'].assets['ffmpeg.wasm']);
});

test('future immutable Builder Release import is fail-closed and current lock stays experimental',()=>{
  const importer=read('scripts/prepare-video-reverse-runtime.ps1');
  assert.equal(lock.kind,'experimental-dual-github-actions-artifact');
  assert.ok(importer.includes("'github-release-st-mt'"));
  for(const token of [
    'releaseArchiveSha256','correspondingSourceSha256',
    'Get-Hash $zip','Assert-Manifest $manifest',
    "Assert-File 'browser-ffmpeg.js' $variantDir",
    'LICENSES/FFmpeg-COPYING.GPLv2',
    'LICENSES/x264-COPYING',
    'LICENSES/Emscripten-LICENSE'
  ]) assert.ok(importer.includes(token),'Release import guard missing '+token);
  assert.ok(importer.includes('if (-not $isRelease) {'));
  assert.ok(importer.includes('Builder Release archive SHA-256 mismatch.'));
  // A distinct video-reverse-v1.10.6 release must not collide with the
  // existing Builder-wide v1.10.6 Release. Do not update today's temp lock.
  assert.ok(importer.includes('video-reverse-v$version'));
  assert.ok(importer.includes('Verified-SourceRelease'));
  assert.ok(importer.includes('Get-Hash $releaseSourceProof'));
  assert.ok(importer.includes('Invoke-WebRequest -Uri "$releaseBase/$sourceAsset"'));
  assert.ok(importer.includes('Corresponding GPL source archive SHA-256 mismatch.'));
  assert.equal(lock.status,'temporary-not-release');
});
