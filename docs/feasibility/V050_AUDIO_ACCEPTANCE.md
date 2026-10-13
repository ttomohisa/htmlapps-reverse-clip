# Reverse Clip v0.5.0 — Audio acceptance record

**Status (2026-10-13): Desktop Chrome ST/MT A/V automation PASS; physical Android, audible seam review, release G1/G2/G3 and permanent GPL distribution still PENDING.**

## Reproducible evidence

- [App standalone + real-browser CI #38358181120](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38358181120) — **success** on app commit `202d0ddb2830408f60bdad0028b098428944512c`. Actual ST and cross-origin-isolated MT: MP4 downloads, ffprobe streams/durations, decoded PCM and waveform direction, L/R frequency, cancellation and existing no-audio regression.
- [Builder ST/MT source/audio remux CI #38357268611](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/actions/runs/38357268611) — **success** on Builder commit `d1feee021aae6feb53eab1084664123f602c2085`. The binary lock pins separately hashed ST and MT JS/WASM assets; `audio-mux` is enabled only for that inspected build.
- Automated tests: `tests/feasibility/audio-browser-smoke.py`, `tests/feasibility/audio-mode.test.mjs`, `tests/feasibility/pingpong-browser-smoke.py`, `tests/feasibility/file-standalone-browser-smoke.py`, `tests/feasibility/dual-thread-browser-smoke.py`.

## Verified desktop CI behavior

| Scenario | Evidence / expected result | ST Chrome | MT Chrome |
|---|---|---|---|
| 1s mono reverse | H.264+AAC, 15 frames; 300/990Hz source tones reverse in decoded PCM | PASS | PASS |
| 1s mono ping-pong | 28 frames, 1.867s H.264+AAC; source sound goes forward then returns | PASS | PASS |
| 0.5s reverse | 8 frames, 0.533s; real audio present | PASS | PASS |
| 0.5s ping-pong | 14 frames, 0.933s; real audio present | PASS | PASS |
| 5s stereo reverse | 75 frames, 5.000s; left 440Hz / right 660Hz remain distinct after AAC encode | PASS | PASS |
| 10s stereo ping-pong | 298 frames, 19.867s; left/right remain distinct; actual AAC MP4 saved and decoded | PASS | PASS |
| MP4 without audio | Audio selection unavailable; silent H.264 export remains usable | PASS | PASS |
| Existing video-only modes | Reverse 10s, ping-pong 10s, VFR/black/portrait footage, cancellation | PASS | PASS |
| Single HTML direct `file://` | ST and self-extract silent reverse works without HTTP | PASS | N/A; MT requires cross-origin isolation |

A test fixture uses two consecutive mono tones (300Hz then 990Hz) and a separate stereo fixture with independent left 440Hz / right 660Hz audio. The tests inspect **actual downloaded MP4s** using FFmpeg/ffprobe and decode audio to PCM; a compiler-only/synthetic timeline assertion does not count as an A/V pass.

### Corrected long-output regression

The dedicated WASM runner had incorrectly reused the **120-frame limit for one reversed segment** when validating a complete video+AAC MP4. A legitimate 10s ping-pong result has 298 frames and was rejected. Builder commit `d1feee021aae6feb53eab1084664123f602c2085` retains the 120-frame *chunk* cap, permits up to 960 frames at the *joined-output* validator, and still requires an exact expected frame count. The final application CI above passes this regression with actual stereo AAC output.

## Pending acceptance (do not mark PASS based on Chrome CI)

- [ ] Physical Android Chrome ST and MT: source selection, audio permission, saving/listening, several repeated 5–10s operations, tab resets or memory pressure; record device/OS/browser versions and timings
- [ ] Human listening and quantitative checks for turn-point/loop-seam clicks, loudness jumps, and any unintended trailing/leading silence across real camera footage
- [ ] Test real camera VFR with audio, display-matrix rotation, HEVC/HDR MOV, and 44.1kHz or other source sample rates
- [ ] Full production-quality and peak-memory goals, including long-edge standard 720p10s and full HD 1080p5s (current 1280×720 1s pilot does not satisfy them)
- [ ] Permanent, versioned, publicly obtainable FFmpeg/x264/Emscripten **GPL corresponding-source** and license-notice bundle; existing Builder Actions artifact `11794061552` **expires 2026-10-20**
- [ ] G1/G2/G3 review and product release readiness; iPhone device testing remains deferred

**Shipping policy:** v0.5 proves desktop ST/MT audio pipeline functionality, not stable cross-device compatibility. Default audio choice remains **No audio**, even when a supported audio track is found. Reverse Clip PR [#2](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/2) and Builder PR [#16](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/pull/16) remain Draft and unmerged. **No Browser Kitty integration before the app is finished**; Browser Kitty PR #41 remains closed without merge.
