Reverse Clip v0.9.0 — RC PREPARATION ONLY (DRAFT, NOT RELEASED).
Gate G2 and Gate G3 are NOT PASSED. See docs/release/RC_CHECKLIST.md.
Desktop ST and isolated MT real H264/AAC Chrome tests:
https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38864099711
Physical Android 720p10s/1080p5s repeated device/RAM/audio acceptance missing.
iPhone Safari hardware acceptance deferred. No tag, merge or release.
Builder video-reverse-v1.10.6 ST/MT and matching GPL source are now publicly
released: https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/tag/video-reverse-v1.10.6
reverse-runtime.lock.json pins public Release ZIPs, source and GPL notice by SHA-256.
The Reverse Clip APP remains Draft; G3 not yet passed.
Release notes are in docs/release/RELEASE_NOTES_DRAFT.md (DRAFT ONLY).

HISTORICAL v0.5.0 AAC CHECKPOINT:

Desktop Chrome real ST and pthread MT MP4 export with AAC has now PASSED:
0.5s + 1s mono, 5s stereo Reverse, 10s stereo Ping-pong (298 frames/19.867s).
ST/MT actual downloaded MP4, decoded PCM and independent L/R pitches tested.
Evidence: https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38358181120
AUDIO DEFAULT: No audio. Optional reverse audio is available only when FFmpeg
recognizes a supported mono/stereo input and the verified audio-mux core is present.
Silence-only input must not expose audio controls. Offline ST video-only is tested.
Builder ST/MT hash-locked commit: d1feee021aae6feb53eab1084664123f602c2085
HISTORICAL: old Builder Actions artifact 11794061552 expired 2026-10-20; current temporary locked artifact details are above. Do not use the old artifact for v0.9.
No permanent source-complete GPL release; physical Android memory/listening,
44.1kHz, camera rotate/HDR, long 720p/1080p stress, and gate reviews PENDING.
Never merge or import into Browser Kitty before completed product acceptance.
