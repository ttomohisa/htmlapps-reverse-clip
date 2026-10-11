/**
 * Native FFmpeg algorithm baseline for Reverse Clip (v0.1.0).
 * This DOES NOT validate the Browser Kitty WASM runtime or any phone.
 * Requires ffmpeg and ffprobe on PATH, Node 20+; no npm dependencies.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import path from 'node:path';
import { execFileSync } from 'node:child_process';

function run(args, binary = 'ffmpeg') {
  return execFileSync(binary, args, { stdio: ['ignore', 'pipe', 'pipe'], maxBuffer: 2 ** 26 });
}
function frameIds(mp4) {
  const data = run(['-hide_banner', '-loglevel', 'error', '-i', mp4,
    '-vf', 'scale=1:1:flags=neighbor,format=rgb24', '-vsync', '0',
    '-f', 'rawvideo', '-pix_fmt', 'rgb24', 'pipe:1']);
  const ids = [];
  for (let at = 0; at < data.length; at += 3) ids.push(Math.round((data[at] - 10) / 5));
  return ids;
}
const root = mkdtempSync(path.join(tmpdir(), 'bk-reverse-native-'));
try {
  const frames = path.join(root, 'frames');
  mkdirSync(frames);
  for (let i = 0; i < 40; i++) {
    const pixels = Buffer.alloc(160 * 90 * 3);
    for (let p = 0; p < pixels.length; p += 3) pixels[p] = 10 + 5 * i;
    writeFileSync(path.join(frames, String(i).padStart(3,'0') + '.ppm'),
      Buffer.concat([Buffer.from('P6\n160 90\n255\n'), pixels]));
  }
  const input = path.join(root, 'source.mp4');
  run(['-hide_banner','-loglevel','error','-framerate','10', '-i',path.join(frames,'%03d.ppm'),
    '-c:v','libx264','-preset','ultrafast','-crf','0','-pix_fmt','yuv420p',input]);

  test('middle clip reversed frame for frame (A-01/A-03 native baseline)', () => {
    const output = path.join(root, 'reverse.mp4');
    run(['-hide_banner','-loglevel','error','-i',input,
      '-vf','trim=start=0.5:end=2.5,setpts=PTS-STARTPTS,reverse,setpts=PTS-STARTPTS,format=yuv420p',
      '-fps_mode','cfr','-r','10','-c:v','libx264','-preset','ultrafast','-crf','0','-an',output]);
    assert.deepEqual(frameIds(output), Array.from({length:20},(_,i)=>24-i));
  });

  test('pingpong no duplicated turnaround (A-02 native baseline)', () => {
    const output=path.join(root,'pingpong.mp4');
    const graph='[0:v]trim=start=0.5:end=2.5,setpts=PTS-STARTPTS,split=2[f][r];'+
      '[r]reverse,trim=start=0.1,setpts=PTS-STARTPTS[b];'+
      '[f][b]concat=n=2:v=1:a=0,format=yuv420p[out]';
    run(['-hide_banner','-loglevel','error','-i',input,'-filter_complex',graph,'-map','[out]',
      '-fps_mode','cfr','-r','10','-c:v','libx264','-preset','ultrafast','-crf','0','-an',output]);
    assert.deepEqual(frameIds(output), [
      ...Array.from({length:20},(_,i)=>5+i),
      ...Array.from({length:19},(_,i)=>23-i)
    ]);
  });
} finally {
  // Test callbacks are synchronous; remove temporary fixtures on process exit.
  process.once('exit',()=>rmSync(root,{recursive:true,force:true}));
}

