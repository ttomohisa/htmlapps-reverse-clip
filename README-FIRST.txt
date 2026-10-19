Reverse Clip v1.0.0 — ST/MT SINGLE-HTML RELEASE.
App Release: https://github.com/ttomohisa/htmlapps-reverse-clip/releases/tag/v1.0.0
Initial supported scope: short H.264 MP4 on Windows / Android Chrome.
The historic broader G2 matrix remains NOT PASSED.

What is available:
- Short H.264 MP4 reverse and forward/back (ping-pong), default silent;
  optional reversed AAC for compatible inputs.
- SHA-256-locked public Builder ST/MT FFmpeg WASM v1.10.6, with matching
  GPL corresponding source and x264 notices:
  https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/tag/video-reverse-v1.10.6
- Windows/desktop Chrome ST/MT and isolated hosted MT automated smoke passed.
- User-reported basic Android Chrome ST and MT tests passed 2026-10-17.

What is not claimed:
- iPhone/HEVC/HDR compatibility, comprehensive Android hardware performance
  or exact device memory limits. Higher resolutions/long clips are experimental.
- Passing the historical full-HD/iPhone repeated-stress G2 matrix.
- Browser Kitty integration in this app Release (separate follow-up task).

Next milestone: docs/release/V100_RELEASE_READINESS.md.
Detailed historical test evidence: docs/release/RC_CHECKLIST.md.
Standalone offline/build guidance: VERIFY_OFFLINE.md.
