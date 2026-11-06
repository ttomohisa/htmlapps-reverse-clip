# Reverse Clip v1.1.0 verification

Implementation is on a feature branch; this is not a release or physical-device certification.

## Verified locally

- PowerShell syntax/encoding preflight and full `scripts/check-repository.ps1`: PASS. PowerShell 7.5.4 on Linux, `tar.exe` mapped to system tar, pinned ST/MT runtime archives verified by the existing importer. PowerShell telemetry disabled before startup using `POWERSHELL_TELEMETRY_OPTOUT=1`; update checks disabled for local tool execution.
- Node `--test tests/feasibility/*.test.mjs tests/*.test.cjs`: 88 tests, all PASS after generated outputs/caches exist.
- `editor-browser-smoke.py`: ST and isolated MT PASS. Real 30fps H.264 reverse (60 frames) and ping-pong (118 frames), AAC/video duration agreement, decoded frame-content comparison, low-resolution 15fps silent draft, full rendering after draft, edited/sanitized filenames, stationary zoom scale, current-position marking, loop preview, cancellation, source replacement and thumbnail failure recovery.
- Native sharing cancellation/error/filename handling: PASS with an explicit mocked OS share boundary. Real OS delivery is not claimed.
- JA/EN layouts at 320, 390 and 1360px: no horizontal overflow. Actual editor screenshots refreshed in both languages at desktop and phone viewports. Thumbnail failure intentionally leaves an empty strip instead of stale imagery from a different timescale.
- `file-standalone-browser-smoke.py`: readable ST and self-extracting ST both opened via `file://`, rendered/saved real H.264 MP4 without HTTP(S) requests.
- `pingpong-browser-smoke.py`: ST/MT PASS, including 10s output, VFR, portrait, intentional black frames, repeated export and cancellation.
- `audio-browser-smoke.py`: ST/MT PASS, including mono/stereo, silent sources, minimum duration, 10s ping-pong, reversed PCM and video/audio duration validation.
- `mt-real-source-regression.py`: five ST/MT sparse-WebCodecs-timeline cases PASS, including 1080-source 10s reverse and ping-pong.
- `browser-video-smoke.py`: PASS, including 10s repeat, fractional boundaries, short/invalid sources, H.264 MOV, 90/180/270-degree rotation, fail-closed HEVC observations, simulated Android/provider fallback, layout/network/JS checks. The local libx265 fixture needed explicit SPS color tags; fixture generation now sets encoder and container color fields rather than silently accepting untagged HDR media.
- Application runtime HTTP(S) traffic and page errors: none observed in the above browser tests. CSP retains `connect-src 'none'`.

Chromium Headless Shell 143 was used locally. This environment's system Chromium could not launch due to a socket restriction. Windows/stock Chrome behavior is also covered by the repository's PR CI, separately from these local observations.

## Review and remaining manual scope

A separate reviewer inspected source cancellation, thumbnails, output policy, sharing and mobile flow. Its stale-thumbnail finding was reproduced with a failing browser regression, fixed, and the full ST/MT editor suite passed afterward.

Physical Android/iPhone, the OS share sheet with real destination apps, subjective audio listening and sustained high-resolution device memory are unverified. 30fps remains experimental at <=720px long-edge presets and <=5 source seconds; 15fps remains the default. Existing HEVC/HDR/iPhone limitations remain.

No Browser Kitty main-site change, merge, tag or GitHub Release publication is included.
