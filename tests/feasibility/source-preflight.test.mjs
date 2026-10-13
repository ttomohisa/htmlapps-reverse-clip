import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';

const html=readFileSync(new URL('../../src/index.template.html',import.meta.url),'utf8');
function pureFunction(startToken,endToken,name){
  const start=html.indexOf(startToken),end=html.indexOf(endToken,start);
  assert.ok(start>=0 && end>start,'Missing pure function '+name);
  return runInNewContext(html.slice(start,end)+'\n'+name,{Uint8Array},{timeout:1000});
}
const plausibleVideoContainer=pureFunction('function plausibleVideoContainer(','async function inspectSourceBlob(','plausibleVideoContainer');
const suggestOutputFilename=pureFunction('function suggestOutputFilename(','function normalizeMP4Filename(','suggestOutputFilename');
const header=(atom,size=24)=>{
  const bytes=new Uint8Array(32);
  bytes[0]=Math.floor(size / 16777216);
  bytes[1]=(size>>>16)&255;
  bytes[2]=(size>>>8)&255;
  bytes[3]=size&255;
  [...atom].forEach((c,i)=>bytes[4+i]=c.charCodeAt(0));
  return bytes;
};
test('MP4 ftyp atom and legacy QuickTime atoms pass a minimal header preflight',()=>{
  assert.equal(plausibleVideoContainer(header('ftyp')),true);
  for(const atom of ['moov','mdat','wide','free','skip'])
    assert.equal(plausibleVideoContainer(header(atom)),true,atom);
});
test('renamed text, WebM/EBML, RIFF and malformed MP4 headers fail',()=>{
  const fake=new Uint8Array(Buffer.from('not a real mp4 container'));
  assert.equal(plausibleVideoContainer(fake),false);
  assert.equal(plausibleVideoContainer(new Uint8Array([0x1a,0x45,0xdf,0xa3,0,0,0,0])),false);
  assert.equal(plausibleVideoContainer(new Uint8Array(Buffer.from('RIFF0000WEBM'))),false);
  assert.equal(plausibleVideoContainer(new Uint8Array(0)),false);
  assert.equal(plausibleVideoContainer(header('ftyp',8)),false);
  assert.equal(plausibleVideoContainer(header('ftyp',4)),false);
  assert.equal(plausibleVideoContainer(header('FAKE',32)),false);
});
test('derived filenames preserve the input stem, extension and safe path handling',()=>{
  assert.equal(suggestOutputFilename('movie.mp4'),'movie-reverse');
  assert.equal(suggestOutputFilename('family.MOV'),'family-reverse');
  assert.equal(suggestOutputFilename('clip.m4v'),'clip-reverse');
  assert.equal(suggestOutputFilename('CON.mp4'),'CON-file-reverse');
  assert.equal(suggestOutputFilename('.mp4'),'reverse-clip-reverse');
  assert.equal(suggestOutputFilename('a/b.mp4'),'a-b-reverse');
  assert.equal(suggestOutputFilename('a'.repeat(300)+'.mp4').length,120);
});
test('source timeout, stale file guards and no whole-file sniff copy are present',()=>{
  assert.ok(html.includes('SOURCE_LOAD_TIMEOUT_MS = 30000'));
  assert.ok(html.includes("failSource('sourceTimedOut', generation)"));
  assert.ok(html.includes("await blob.slice(0, 32).arrayBuffer()"));
  assert.ok(html.includes("state.sourcePhase !== 'inspecting'"));
  assert.ok(html.includes("sourceIsCurrent(file, generation)"));
  assert.ok(html.includes("setSourcePhase('error', generation, errorKey)"));
  assert.ok(html.includes("'reverseSourceUnreadable'"));
  assert.ok(html.includes("'invalidContainer'"));
});
