# Reverse Clip — Offline & Standalone Verification

**Current status (2026-10-16):** v0.9.0 RC PREPARATION, **Gate G2 / Gate G3 still NOT PASSED**. Prior real Chrome `file://` ST readable+self-extract MP4 smoke PASS ([CI #38864099711](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38864099711)); this does not establish Windows Edge, Android physical acceptance or iPhone Safari. MT requires COOP/COEP from a web server and must not be advertised as direct file://. Refer to [current RC checklist](docs/release/RC_CHECKLIST.md) for release signoff. Older version references below are historical regression instructions, not current status.

## Build & compare output

1. Run `build-standalone.bat` with a source checkout. The app downloads the fixed ST/MT assets and matching source from the [public Builder video-reverse Release](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/tag/video-reverse-v1.10.6) on the first build. A GitHub token is no longer needed for the FFmpeg WASM runtime; browser users never needed one.
2. Confirm the template builds `dist/index.html`, `dist/index.self-extract.html` and `reverse-clip.html`. These are separate variants of the same local application, not external-runtime shells.
3. Confirm `connect-src 'none'`, `worker-src ... blob:`, and `script-src ... 'wasm-unsafe-eval'` in the effective CSP of both standalone files. Verify no external JS/WASM URLs remain.
4. On Windows Chrome/Edge, open **each** HTML directly through `file://`. Observe the self-extract loader complete without CSP errors, then turn off network and reload. This local URL check is required; tests that use `page.set_content` do **not** replace it.
5. Use `tests/feasibility/browser-video-smoke.py` for an optional reproducible Chromium test. It creates an artificial 50-frame source and checks 75 reverse frames across all segment boundaries, both HTML variants, MP4 save and no external network requests. See `tests/feasibility/README.md`.

## Device tests (record results in docs/feasibility/G1.md)

1. iPhone Safari and Android Chrome: select a real H.264 MP4; preview, adjust start/end to **0–1s**, output **long edge 360px**, create and save MP4. Confirm the downloaded file plays correctly.
2. Repeat **0–5s** with long edge 360px; then separately try long edge 720px and record seconds, file size, successful playback, source codec and failure messages. Test 2 consecutive runs and cancellation/retry.
3. Use a video from the device's photo gallery and one from Downloads. On Android, a picker source may allow browser preview but block Worker-side `FileReaderSync`. Confirm the pre-copy/MEMFS fallback for source files ≤64 MiB, and actionable error text for denied or larger files.
4. Include an iPhone HEVC MOV with orientation metadata. If unsupported, record that explicitly rather than claiming MOV works.
5. Check landscape and portrait outputs, start/end frame order, correct 15fps timing, UI at 320–390px, and long filenames in both Japanese and English.
6. Replace the source while processing; confirm the previous worker stops and stale results never appear. Cancel during chunk reversal and during joining; ensure partial MP4 cannot be saved.
7. Inspect Network for CDN, analytics, upload or other external dependencies; source video bytes should stay on-device.

## Release blockers

The Builder WASM currently comes from an **expiring GitHub Actions artifact**, pinned in `reverse-runtime.lock.json`. Before a stable release, replace it with a permanent versioned artifact carrying the required FFmpeg/x264/Emscripten corresponding source and GPL notices. Full G1/G2 acceptance and actual mobile testing remain necessary.

## v0.1.4 ten-second checks (Android / Windows focus)

1. Test 0–5s again to ensure the previously working Android path remains intact.
2. Test 0–10s first with long edge360px, then optionally long edge720px. The app displays an experimental warning beyond five seconds; there is no automatic downgrade. Record conversion time and failures, but **do not infer mobile performance from desktop simulation**.
3. Test start=0.1s, end=9.87s; the expected video is 146 frames at 15fps / ~9.733s after frame-grid snapping. Test 0–9.9s (149 frames) and 0–0.5s (8 frames). Unexpected frame counts must fail closed rather than leave a savable output.
4. Repeat the same 10-second conversion twice, compare output hashes where possible, cancel during the second/third segment and during join, and ensure no previous/stale/partial result is downloadable.
5. Test replacement of input during a slow 10-second conversion, Android photo-provider source and browser Downloads source, direct `file://` on Windows, long filenames, offline access and English/Japanese UI.
6. **iPhone Safari / HEVC MOV testing is deferred by user instruction (2026-10-12)**; do not claim it passed or request it as part of the current Android-first milestone.

A separate `tests/feasibility/browser-video-smoke.py` optional suite runs real WASM on both generated HTML variants using desktop Chromium. It does not validate physical Android devices or direct file://.

## ST / MT distribution acceptance (v0.1.5)

- The normal Windows standalone build must produce four HTML files: `dist/index.html`, `dist/index.mt.html`, and both respective self-extract outputs. Root ST and MT copies must match each output byte-for-byte.
- ST standalone must operate directly from `file://` (when allowed by the local browser); MT may only run on a server that supplies COOP/COEP and exposes SharedArrayBuffer. Missing MT isolation must disable conversion with a clear message; **do not silently execute ST while labeling MT**.
- `pages-dist/index.html` is ST; `pages-dist/mt/index.html` is MT with a **pinned, same-origin COI SW**. Neither standalone HTML variant embeds a Pages worker reference.
- GitHub Pages ST and MT must both pass real MP4 conversion, cancellation, saved output, per-threading SHA-256 and no runtime external media/network requests. Pages MT may reload once to install its SW.
- Browser Kitty must import the actual MT Pages HTML and apply COOP/COEP/CORP only on `/apps/reverse-clip.html`. The required headers must be observed on the live HTTP response; runtime must show `crossOriginIsolated` and `SharedArrayBuffer` available. The portal homepage and other apps must be unchanged.
- A successful build does not prove MT is faster on Android, nor make iPhone supported. Stable release is blocked on corresponding GPL source and immutable Builder assets.
