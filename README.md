# Reverse Clip / 動画逆再生

**Development status: v0.1.3 experimental chunked WASM export (Gate G1: NOT PASSED).** Reverse up to 2 seconds of video, no audio. Mobile performance and original-capture codecs remain unverified.

[日本語 README](README.ja.md) · [Product specification](APP_SPEC.md) · [Development plan](DEVELOPMENT_PLAN.md) · [Feasibility record](docs/feasibility/G1.md)

## Goal

Select a short portion of a video and export a reversed or forward-then-reverse H.264 MP4 **without uploading the video**. Initial limits planned for v1.0.0: standard up to 720p / 10 seconds, high quality up to 1080p / 5 seconds, pending real-device proof.

## What this version does

- Runs a browser-local **feasibility diagnostic**: open/capture a video, preview it, select an interval, inspect duration/dimensions, estimate an uncompressed frame-buffer lower bound, probe seeking and baseline Worker/WASM availability, and download a diagnostic JSON report (explicit action only).
- With a playable video selected, **Check browser capabilities** runs the seek test automatically too. Earlier `seek: null` reports indicate the seek check was not run, not a failed seek.
- Includes reproducible **native FFmpeg algorithm tests** for frame-accurate middle-clip reversal and ping-pong without a duplicated turnaround frame.
- Preserves the `htmlapps-template` single-HTML, offline-first, CSP, bilingual, Windows build and GitHub Actions conventions.

**Experimentally available:** a single 0.5–5s reversed H.264 MP4 without audio; long edge 360px and 720px at 15fps (no upscaling). **Not available:** ping-pong, reverse audio, longer clip stitching, reliably supported HEVC/MOV, and verified phone performance. G1 remains open.

## Development

Build on Windows: `build-standalone.bat` (PowerShell; follows the upstream template). Expected readable build: `dist/index.html`; self-extract variant: `dist/index.self-extract.html`; root copy: `reverse-clip.html`.

Run the algorithm baseline with Node.js 20+ and native FFmpeg installed:

```shell
node --test tests/feasibility/native-reverse.test.mjs
```

This optional native test is not required by the standalone app. G1 requires real iPhone Safari and Android Chrome conversion, H.264 MP4 playback/save, resource-performance evidence and direct `file://` tests; passing the desktop smoke alone is insufficient.

## Privacy

The diagnostic browser page uses an object URL to preview the selected local video and does not upload it. `connect-src 'none'` blocks runtime network connections. Diagnostic JSON records browser capability and media characteristics, **not media contents or filename**, and is saved only when you select Download.

## Browser support

Chrome/Edge: target for initial desktop tests. iOS Safari / Android Chrome: test targets; **not yet verified**. Metadata and codec support depend on the browser/device.

## License

App and native test source: MIT. Embedded experimental FFmpeg/x264 WASM: GPL-2.0-or-later, separate license obligations. See `THIRD_PARTY_NOTICES.md` and pinned hashes in `reverse-runtime.lock.json`. This is not a final GPL source-compliance or public-release approval.

## Experimental WASM build provenance

v0.1.1 imports an **experimental, expiring** Builder Actions artifact at **build time only**, pinned to commit `f91efb4` and SHA-256 for the core JavaScript, WASM and BrowserFFmpeg loader. Check `reverse-runtime.lock.json`. The generated HTML includes all bytes and makes no runtime API/CDN calls. This is **not** a stable release artifact: GitHub Actions artifacts expire, so the build download will eventually stop working. **Before v1.0**, merge/review the Builder profile and replace the Actions artifact with a permanent, version-tagged GPL-compliant Builder Release with corresponding sources.

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

The fixed UI has **not** yet been proven on the reporting Android handset. G1 remains pending.

### v0.1.3 — experimental segment joining

A 0.5–5-second selection is snapped to the nearest 15fps frame boundary (up to about 0.033s shift, disclosed in the UI), then divided into 1–3 bounded segments with 2-second-aligned boundaries, each no longer than 2 seconds. The app reverses chunks from **latest to earliest**, before a dedicated public-libav remuxer validates H.264 stream consistency and rebases timestamps to produce one MP4. Source audio is not included and ping-pong is unavailable. Cancellation never enables saving a partial MP4.

The quality presets now explicitly mean **long edge 360px or 720px**; they do not promise conventional 720p dimensions. A 5-second marker-video proof passed 50/50 frame-order checks in desktop Chromium. Actual 5-second Android/iPhone throughput and memory behavior remain unverified. The temporary Builder artifact is pinned to commit `47448852` / ID `11698036987` and must be replaced by a permanent, source-complete GPL release before stable publication.
