# Reverse Clip / 動画逆再生

**Development status: v0.1.0 feasibility spike (Gate G1: NOT PASSED).** This is a diagnostic build, not a video-reversing editor yet.

[日本語 README](README.ja.md) · [Product specification](APP_SPEC.md) · [Development plan](DEVELOPMENT_PLAN.md) · [Feasibility record](docs/feasibility/G1.md)

## Goal

Select a short portion of a video and export a reversed or forward-then-reverse H.264 MP4 **without uploading the video**. Initial limits planned for v1.0.0: standard up to 720p / 10 seconds, high quality up to 1080p / 5 seconds, pending real-device proof.

## What this version does

- Runs a browser-local **feasibility diagnostic**: open/capture a video, preview it, select an interval, inspect duration/dimensions, estimate an uncompressed frame-buffer lower bound, probe seeking and baseline Worker/WASM availability, and download a diagnostic JSON report (explicit action only).
- Includes reproducible **native FFmpeg algorithm tests** for frame-accurate middle-clip reversal and ping-pong without a duplicated turnaround frame.
- Preserves the `htmlapps-template` single-HTML, offline-first, CSP, bilingual, Windows build and GitHub Actions conventions.

**Not yet available:** actual video reversal, audio reversal, MP4 export, a pinned FFmpeg WASM asset, or verified mobile stability. A successful native FFmpeg test is **not** G1 approval.

## Development

Build on Windows: `build-standalone.bat` (PowerShell; follows the upstream template). Expected readable build: `dist/index.html`; self-extract variant: `dist/index.self-extract.html`; root copy: `reverse-clip.html`.

Run the algorithm baseline with Node.js 20+ and native FFmpeg installed:

```shell
node --test tests/feasibility/native-reverse.test.mjs
```

This optional test does **not** require FFmpeg for the standalone HTML build. G1 cannot pass until the dedicated Builder WASM, iPhone Safari, Android Chrome, direct `file://` test, and real video save/replay results have been recorded.

## Privacy

The diagnostic browser page uses an object URL to preview the selected local video and does not upload it. `connect-src 'none'` blocks runtime network connections. Diagnostic JSON records browser capability and media characteristics, **not media contents or filename**, and is saved only when you select Download.

## Browser support

Chrome/Edge: target for initial desktop tests. iOS Safari / Android Chrome: test targets; **not yet verified**. Metadata and codec support depend on the browser/device.

## License

App and native test source: MIT. Third-party codec runtime has **not** yet been added. When FFmpeg/x264 WASM is adopted, its exact licenses, corresponding source, version and SHA-256 must be recorded before shipping.
