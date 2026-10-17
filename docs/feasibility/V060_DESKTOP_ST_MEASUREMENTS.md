# Reverse Clip v0.6.0 — desktop ST full-resolution measurement (2026-10-13)

**Result: 11/11 full-resolution H.264 exports succeeded on one Linux desktop ST environment. This is NOT Gate G2 approval, NOT MT full-resolution proof, and NOT Android/iPhone acceptance.**

## Reproducibility and scope

- Tested the actual pinned single-thread standalone HTML from application Draft PR #2, commit [`b26ebc8b77e407a7a267b11bcd74666912b2e471`](https://github.com/ttomohisa/htmlapps-reverse-clip/commit/b26ebc8b77e407a7a267b11bcd74666912b2e471), [verified CI #38374824807](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38374824807), Actions artifact **`11801040425`** (SHA-pinned embedded Builder ST runtime as recorded in `reverse-runtime.lock.json`).
- Device: Linux x86_64 execution container, Debian 13, headless Chromium **144.0.7559.96**, Python **3.13.5** / Playwright, FFmpeg/ffprobe **7.1.5**, psutil **7.2.2**.
- Source fixtures generated locally: **testsrc2** H.264 15fps yuv420p, 1280×720 10s / 1920×1080 5s, optionally 48kHz AAC stereo derived from a 440Hz sine. This is **not** phone-captured footage, VFR/HEVC/MOV, genuine independent left/right tones, or meaningful human listening material.
- **Environment difference:** Chromium in this execution environment returns `ERR_BLOCKED_BY_ADMINISTRATOR` for both loopback HTTP and `file://` navigation. Consequently, the test used Playwright `page.set_content` to instantiate the **unaltered, generated single HTML bytes** in its initial `about:blank` document. It verified ST `crossOriginIsolated=false` and produced real H.264/AAC MP4; it did **not** reverify actual local file navigation or cross-origin-isolated MT. Prior CI provides separate normal HTTP + `file://` ST and low-resolution MT regressions.
- For each downloaded MP4, `ffprobe` checked output codec, geometry, encoded frame count and container duration; **native FFmpeg decoded the entire output video**. Additional 96×54 grayscale per-frame comparisons checked source identity at **every output position** (against both immediate source-frame neighbors) for one representative case per resolution/direction/audio class. No duplicate/missing/wrong-order frames were detected in those comparisons.
- Each reported processing duration measures from the UI's Create click to visible completed result, not fixture generation or output validation. The approximate browser-related subprocess RSS is sampled at 250ms intervals and summed; it **may double-count shared pages** and is not Android RAM peak or a guaranteed single-tab memory bound.
- The browser reported **no uncaught page errors and no unexpected network requests** in these cases.

## Actual outputs — all PASS

| Quality | Mode | Audio | Run | Processing (s) | Decoded frames / MP4 duration | Process-tree sampled peak (MiB) |
| --- | --- | --- | --- | ---: | --- | ---: |
| 1280×720 / 10s input | Reverse | No | 1 | **9.71** | 150 / 10.000s | 752.6 |
| 1280×720 / 10s input | Ping-pong | No | 1 | **18.14** | 298 / 19.867s | 748.2 |
| 1280×720 / 10s input | Ping-pong | No | 2 | **20.24** | 298 / 19.867s | 747.6 |
| 1280×720 / 10s input | Ping-pong | No | 3 | **20.71** | 298 / 19.867s | 727.1 |
| 1920×1080 / 5s input | Reverse | No | 1 | **10.29** | 75 / 5.000s | 865.5 |
| 1920×1080 / 5s input | Ping-pong | No | 1 | **20.43** | 148 / 9.867s | 843.8 |
| 1920×1080 / 5s input | Ping-pong | No | 2 | **20.57** | 148 / 9.867s | 838.1 |
| 1920×1080 / 5s input | Ping-pong | No | 3 | **20.16** | 148 / 9.867s | 808.4 |
| 1280×720 / 10s input | Ping-pong | AAC | 1 | **21.00** | 298 / 19.867s | 786.0 |
| 1920×1080 / 5s input | Ping-pong | AAC | 1 | **20.69** | 148 / 9.867s | 891.4 |
| 1280×720 / 10s input | Ping-pong | AAC | Retry after active-segment cancel | **21.80** | 298 / 19.867s | 842.6 |

The two high-resolution AAC outputs were probed independently: both MP4 streams reported matching **video and AAC audio durations** of **19.866667s** (720p) and **9.866667s** (1080p), respectively, sample rate 48kHz with two output channels. This does not prove click-free acoustic turn/loop seams or independent stereo preservation on real source footage.

### Cancellation/retry proof

On the 720p10s AAC Ping-pong test, the test clicked Create twice, observed active processing of **forward segment 1/10 at 87%**, cancelled and confirmed the result area and Save control were hidden. A subsequent real export **succeeded and decoded** (298 frames, 19.866667s H.264/AAC). There were no uncaught page errors or unintended remote network requests. Cancellation at initial WASM initialization, segment join, final AAC mux, page backgrounding, Android picker and persistent memory pressure are not established by this one test.

### Frame order proof

The source `testsrc2` varies between adjacent 15fps frames. A grayscale representation of **every** decoded output frame (96×54) was compared with the expected input frame and its immediate neighbors. The expected frame had lower mean squared error than both neighbors in:

- 720p10s Reverse video-only (150/150 positions),
- 720p10s Ping-pong including AAC (298/298 positions),
- 1080p5s Reverse video-only (75/75 positions),
- 1080p5s Ping-pong including AAC (148/148 positions).

The comparisons found **zero wrong neighboring-frame matches**, including the chunk and return boundaries. This strengthens frame order evidence but does not cover footage with equal consecutive frames, real VFR, camera rotation or other codecs.

## Next Gate G2 work

1. Full-resolution **MT** runs under genuine COOP/COEP and three repeat Reverse/Ping-pong operations for both resolutions; ordinary Chrome ST already has the desktop successes above.
2. Representative **physical Android** H.264/AAC filming, repeat, hardware RAM, system tab pressure and audible seam/sync testing; **iPhone testing remains deferred by owner request**.
3. Reliable input-provider handling and the specification's no-whole-original-copy condition for inputs ≤1GiB; the existing Android ≤64MiB in-memory fallback conflicts with a literal reading and needs either engineering resolution or owner-approved exception.
4. Measure 4K/HEVC/VFR/rotated HDR inputs separately, without claiming they were covered by these fixtures.
5. Replace the expiring Builder Actions artifact with permanent, license-complete and corresponding-source GPL versioned assets.

**Decision: Desktop ST full-resolution synthetic proof recorded; G2 remains INVESTIGATE.** Keep app PR #2 and Builder PR #16 Draft, do not merge, tag or integrate Browser Kitty.
