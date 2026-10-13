# Reverse Clip / 動画逆再生

**Development status: v0.1.6 ST/MT experimental builds (cancel/retry hardened; Android/Windows-first; stable release pending).** Reverse up to 10 seconds of silent video; 10-second Android operation remains unverified. Android users confirmed 1s and 5s exports, including 5s at long-edge 720px in 12.7s (user report). iPhone testing is deferred.

[日本語 README](README.ja.md) · [Product specification](APP_SPEC.md) · [Development plan](DEVELOPMENT_PLAN.md) · [Feasibility record](docs/feasibility/G1.md)

## Goal

Select a short portion of a video and export a reversed or forward-then-reverse H.264 MP4 **without uploading the video**. Initial limits planned for v1.0.0: standard up to 720p / 10 seconds, high quality up to 1080p / 5 seconds, pending real-device proof.

## What this version does

- Runs a browser-local **feasibility diagnostic**: open/capture a video, preview it, select an interval, inspect duration/dimensions, estimate an uncompressed frame-buffer lower bound, probe seeking and baseline Worker/WASM availability, and download a diagnostic JSON report (explicit action only).
- With a playable video selected, **Check browser capabilities** runs the seek test automatically too. Earlier `seek: null` reports indicate the seek check was not run, not a failed seek.
- Includes reproducible **native FFmpeg algorithm tests** for frame-accurate middle-clip reversal and ping-pong without a duplicated turnaround frame.
- Preserves the `htmlapps-template` single-HTML, offline-first, CSP, bilingual, Windows build and GitHub Actions conventions.

**Experimentally available:** a 0.5–10s reversed H.264 MP4 without audio; long edge 360px and 720px at 15fps (no upscaling). **Not available:** ping-pong, reverse audio, longer clip stitching, reliably supported HEVC/MOV, and verified phone performance. G1 remains open.

## Development

Build on Windows: `build-standalone.bat` (PowerShell; follows the upstream template). Expected readable build: `dist/index.html`; self-extract variant: `dist/index.self-extract.html`; root copy: `reverse-clip.html`.

Run the algorithm baseline with Node.js 20+ and native FFmpeg installed:

```shell
node --test tests/feasibility/native-reverse.test.mjs
```

This optional native test is not required by the standalone app. Android real-device export has been user-confirmed, but repeat-run memory tests, longer clips, standard 720p/1080p output and direct `file://` remain pending. The original cross-platform G1 is not complete; iPhone Safari testing is explicitly deferred.

## Privacy

The diagnostic browser page uses an object URL to preview the selected local video and does not upload it. `connect-src 'none'` blocks runtime network connections. Diagnostic JSON records browser capability and media characteristics, **not media contents or filename**, and is saved only when you select Download.

## Browser support

Chrome/Edge: priority desktop targets. Android Chrome: real-phone user reports confirm short 1s and 5s exports for the tested samples, but other codecs/devices and repeated runs remain unverified. **iOS Safari: not tested and deferred; no compatibility claim.** Metadata and codec support vary by browser/device.

## License

App and native test source: MIT. Embedded experimental FFmpeg/x264 WASM: GPL-2.0-or-later, separate license obligations. See `THIRD_PARTY_NOTICES.md` and pinned hashes in `reverse-runtime.lock.json`. This is not a final GPL source-compliance or public-release approval.

## Experimental WASM build provenance

Earlier versions imported an **experimental, expiring** Builder Actions artifact at **build time only**, initially pinned to commit `f91efb4` and SHA-256 for the core JavaScript, WASM and BrowserFFmpeg loader. Check `reverse-runtime.lock.json`. The generated HTML includes all bytes and makes no runtime API/CDN calls. This is **not** a stable release artifact: GitHub Actions artifacts expire, so the build download will eventually stop working. **Before v1.0**, merge/review the Builder profile and replace the Actions artifact with a permanent, version-tagged GPL-compliant Builder Release with corresponding sources.

Normal build on Windows: set `GITHUB_TOKEN` or `GH_TOKEN` with permission to read the public Builder artifact, then run `build-standalone.bat`. Once verified runtime files are cached in `.cache/reverse-runtime`, further local builds can run offline. The GitHub Actions build sets its own scoped token; users of the generated single HTML do **not** need any token.

### Experiment steps

1. Choose an MP4/MOV and let the browser display metadata and a preview.
2. Choose 0.5–5 seconds, output long edge 360px or 720px; mode is reverse-only.
3. Press **Create reversed MP4** and optionally cancel during conversion. If an error appears, expand the technical details.
4. Play the *generated* output, check frame order and orientation, edit the MP4 filename, and press **Save MP4**.
5. Use the separate diagnostic button if requested. The JSON optionally includes an output-success/error summary, but never raw video data or the input filename.

Because this is a feasibility experiment, no unconditional iPhone/Android support claim is made.

### Android file-picker reading workaround (v0.1.2)

Some Android photo or cloud providers return a `File` that can be previewed but fails when FFmpeg's Worker reads it through `FileReaderSync`/`WORKERFS`. For **mobile-selected input files up to 64 MiB**, this version attempts to read the content immediately on the main thread, builds a temporary in-memory Blob, and loads it into the FFmpeg virtual filesystem through `MEMFS`; this path **does not invoke `FileReaderSync`** for the original provider file. The bytes never leave the browser. The extra copy uses more memory and is deliberately limited. Large files retain WORKERFS, with a clear error if this platform cannot read them. Desktop files retain WORKERFS and can retry through the bounded-memory path after a recognized read failure. If even the initial browser read is denied, download/save the video to local device storage before selecting it again.

The local-file workaround was followed by successful Android real-device export reports, including a 5s clip. G1 remains pending for broader performance, codec, and original cross-platform coverage.

### v0.1.3 — experimental segment joining

A 0.5–5-second selection is snapped to the nearest 15fps frame boundary (up to about 0.033s shift, disclosed in the UI), then divided into 1–3 bounded segments with 2-second-aligned boundaries, each no longer than 2 seconds. The app reverses chunks from **latest to earliest**, before a dedicated public-libav remuxer validates H.264 stream consistency and rebases timestamps to produce one MP4. Source audio is not included and ping-pong is unavailable. Cancellation never enables saving a partial MP4.

The quality presets now explicitly mean **long edge 360px or 720px**; they do not promise conventional 720p dimensions. A 5-second marker-video proof passed 50/50 frame-order checks in desktop Chromium. One Android 5s/long-edge720px conversion completed in a reported 12.7s; repeat-run memory and codec coverage are still unverified. iPhone verification is deferred. The temporary Builder artifact is pinned to commit `47448852` / ID `11698036987` and must be replaced by a permanent, source-complete GPL release before stable publication.

### Scope decision — 2026-10-12

**Android Chrome and Windows Chrome/Edge are the current development/verification priorities.** The user explicitly deferred iPhone Safari and iPhone HEVC MOV work. iOS is **unverified**, not unsupported by design and not a blocker to continued experimental Android-first development. Do not represent it as supported or treat the original cross-platform G1 as passed. Full release scope and acceptance criteria remain subject to explicit review; the temporary Builder Actions artifact and source/license obligations must be resolved before stable publication.

### v0.1.4 — 10-second experimental mode

The current pinned binary is Builder commit `b67b1e2f19eef802791ca733884709155f10dfb5`, Actions run `38175167646`, artifact `11715866319`. Hashes for both JS and WASM live in `reverse-runtime.lock.json`. This build adds **`--frames` for each segment** and **`--expected-frames` when joining**. The actual H.264 packets are counted with public libavformat, rejecting a failed length/rounding match. The app continues to render at fixed 15fps using a maximum of 2 seconds per segment and **long edge 360px or 720px**, not standard 1280×720 output.

Independent Linux Chromium experiments (not real Android) converted 10s / 100-marked-frame input to **150 correctly reversed frames, 10.000s**, byte-for-byte repeatably, plus non-frame-aligned ranges. A simulated Android Chrome UA converted 720×1280 portrait H.264 into 404×720, 150 frames / 10.000s, on two consecutive runs with byte-identical MP4 files and a successful cancellation cleanup. **Desktop timings are not mobile benchmarks.**

A 10-second selection shows an explicit experimental warning. On a phone start with long edge 360px; no automatic quality downgrade occurs. The Android 5s/long-edge720px user result was 12.7s, but **10s on Android is not yet tested**. iPhone remains deferred. Memory limits, VFR and rotated HEVC MOV remain unverified. No stable release is authorized.

## v0.1.5 — ST / MT distribution (2026-10-12)

The same Reverse Clip app is built with **two actual FFmpeg WebAssembly binaries** from one pinned Builder source: **ST (single thread)** and **MT (pthreads)**. These are not the same binary with a UI switch. Following the proven `htmlapps-ffmpeg-filter-builder` layout:

- **GitHub Pages root:** portable ST at `/`, `https://ttomohisa.github.io/htmlapps-reverse-clip/`.
- **GitHub Pages MT:** `/mt/`, `https://ttomohisa.github.io/htmlapps-reverse-clip/mt/`, with an MIT-licensed SHA-pinned same-origin cross-origin-isolation Service Worker that may reload on first visit.
- **Browser Kitty intended import:** MT only, at `/apps/reverse-clip.html`, served with route-scoped COOP `same-origin`, COEP `require-corp`, CORP `same-origin`. The Cloudflare origin provides isolation; the Pages bootstrap remains inactive.
- **Standalone HTML:** separate ST `dist/index.html` and MT `dist/index.mt.html`, plus separate self-extract versions. ST can open through `file://`; MT requires HTTP(S) hosting and cross-origin isolation.

The MT app checks `crossOriginIsolated` and `SharedArrayBuffer` and **does not silently run the ST core while claiming MT**. Pages ST is the explicit fallback. Neither version uploads selected video or retrieves runtime code on use. The runtime is embedded at build time from pinned, independently SHA-256 verified JS and WASM, after successful Builder Docker/browser smoke. See [threading distribution](docs/THREADING_DISTRIBUTION.md).

**Important:** Existing Android 1s/5s/10s performance results apply to the original ST runtime. MT performance on actual phones has **not yet been measured or promised**. The temporary Builder Actions artifact must be replaced by a permanent GPL source-complete release before stable publication. A successful build/PR alone does not publish these new Pages routes.

## v0.1.6 — cancellation and source-switch safety (2026-10-13)

WASM initialization can finish after a user cancels a conversion or chooses a different video. That late runner is now disposed by its original conversion, never attached to a newer job or allowed to publish an obsolete MP4. The result-preview metadata wait is abortable too. The ST/MT Chrome smoke test now checks cancellation during delayed initialization, file replacement during initialization and a subsequent real MP4 export.

The product is **still experimental**. These automated desktop tests do not establish Android MT performance, full 10-second stability or a stable GPL-corresponding-source release. **Browser Kitty integration is deferred until Reverse Clip is finished**; Browser Kitty PR #41 was closed unmerged and no new portal PR should be opened during ongoing development.
