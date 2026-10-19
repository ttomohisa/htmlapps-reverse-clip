# Reverse Clip v0.4.0 — Ping-pong acceptance evidence

**Status: Desktop Chrome ST/MT automated quality checks passed; Android hardware and stable-release gates PENDING.**

Evidence as of 2026-10-13 (JST):

- [Reverse Clip ST/MT full app CI run 38347758127](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38347758127) — **all jobs success**, app head `3db5a269adc3d7757ea7e8ce41fd2f5898f23ffa`
- [WASM Builder ST/MT build and browser smoke run 38346351559](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/actions/runs/38346351559) — **success**, Builder commit `fa52f86b27675f5c7b6c7fba52a73d38ac766687`
- Source: `tests/feasibility/pingpong-browser-smoke.py`, `tests/feasibility/pingpong-plan.test.mjs`, `tests/feasibility/browser-video-smoke.py`

## What was exercised

| Case | Input and expected output | ST Chrome | MT isolated Chrome |
|---|---|---|---|
| 1-second midpoint | 15 input frames → **28** output; `0..14,13..1` in correct order | PASS | PASS |
| Minimum section | 0.5s → **14** output frames, no duplicate turning frame | PASS | PASS |
| 31-frame boundary | 31 original frames → **60** output, no one-frame reverse chunk | PASS | PASS |
| 10-second selection | 150 selected frames → **298** output across forward/return chunks | PASS | PASS |
| True VFR container | 34 frames with irregular input PTS deltas → 28 output, forward/return direction, no unexpected blank/seam | PASS | PASS |
| Black source | Intentional black H.264 input → 28 black output frames; no unexpected rejection | PASS | PASS |
| Portrait | 90×160 H.264 input → 90×160 output, 28 frames | PASS | PASS |
| Cancel/retry | No incomplete previous output made available after cancel | PASS | PASS |
| Zero external media traffic | Source locally loaded and MP4 saved using browser download | PASS | PASS |
| Original Reverse regression | 10s, 150-frame reverse and repeated export | PASS | PASS |

The tests call the **real embedded FFmpeg WASM**, save actual MP4 through Chromium, then verify H.264, absent audio, frame count, duration and (for marker fixtures) decoded frame order with ffprobe/ffmpeg. Desktop simulated Android User-Agent tests are **not hardware verification**.

### Temporal boundary policy

For N chosen frames `0..N−1` at 15fps, Ping-pong emits exactly **`0..N−1, N−2..1`**, totaling **2N−2 frames**. The first frame is encountered again only when the clip itself loops. This avoids consecutive duplicate encoded frames at the turn and loop seam for a CFR marker source. VFR-to-15fps resampling may naturally repeat source imagery, and should not be incorrectly diagnosed as a stitching error.

### Required before real-device or stable release acceptance

- [ ] Physically test on Android Chrome ST and MT (model, Android/browser versions, 1/5/10s, source type, memory/tab restarts, cancellation and repeated runs)
- [ ] Verify 720p-class full selection and the planned standard 720p10s / high 1080p5s limits on appropriate real-device hardware
- [ ] Verify real camera rotation/display-matrix samples, HDR/HEVC MOV and VFR with audio tracks
- [ ] Complete v0.5.0 audio-mode functionality or explicitly revise approved product scope
- [ ] Replace **expiring** Builder Actions artifact `11789347043` (expires **2026-10-20**) with a reviewed immutable public tag, matching GPL/FFmpeg/x264/Emscripten corresponding sources and notices
- [ ] Record G1/G2 and release-candidate gate decisions; do not infer passing hardware from CI
- [ ] Do not import into Browser Kitty until the application is complete. Browser Kitty PR #41 remains closed unmerged.

**PR policy:** Reverse Clip [Draft PR #2](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/2) stacks on [Draft PR #1](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/1), Builder [Draft PR #16](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/pull/16) remains unmerged. Only the owner merges.
