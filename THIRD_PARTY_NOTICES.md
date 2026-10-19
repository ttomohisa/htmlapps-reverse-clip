# Third-party notices — Reverse Clip v0.9.0 release candidate

**Status: Reverse Clip v0.9.0 is an unreleased RC integrated into `main`. Its dedicated FFmpeg WASM dependency is now published.**

Reverse Clip's original application source is licensed under the repository's MIT license. Its bundled **video-reverse** WebAssembly runtime links **FFmpeg n9.0.1 and x264**, and is separately identified in its binary metadata as **GPL-2.0-or-later**, not MIT. Both the single-thread (ST) and multi-thread (MT/pthreads) variants use the same license classification. The application license does not replace FFmpeg/x264 license requirements. The owner authorized the dedicated Builder profile distribution; the app's separate G3 release acceptance remains pending.

## Current compiled runtime provenance

The published, SHA-256-pinned runtime is specified by `reverse-runtime.lock.json`:

- Builder repository: `ttomohisa/htmlapps-ffmpeg-wasm-builder`.
- Exact compiled Builder commit: `8e60da7cf9de644ce3f6cce9c007b17e6a385c53`.
- Builder version: **1.10.6**; profile: `video-reverse`.
- FFmpeg revision: **n9.0.1**, commit `bf1b838f2ab88b4f8fd83443325c782ea0e0f7fa`.
- x264 revision: commit `31e19f92f00c7003fa115047ce50978bc98c3a0d`.
- Emscripten toolchain: **6.0.6**, source commit `ce75e06884093bcefb86a6b8fd56a5d62a4cc245`.
- Public dedicated Builder profile Release: [video-reverse-v1.10.6](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/tag/video-reverse-v1.10.6).
- Public matching source file: [ffmpeg-wasm-sources-v1.10.6.tar.gz](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/download/video-reverse-v1.10.6/ffmpeg-wasm-sources-v1.10.6.tar.gz); hash `9ceb47a5f46fb3484f8b1f6a8fa37e6d0dc4144aa09d78939ac9d23e8ab5ce92`.

Exact variant-specific `ffmpeg.js` and `ffmpeg.wasm` SHA-256 values, and the shared `browser-ffmpeg.js` loader digest, are recorded in `reverse-runtime.lock.json`. Builds reject mismatches. The ST output supports standalone local use; the MT variant requires cross-origin isolation and SharedArrayBuffer.

The old development-only Actions artifact and archived review fallback were used during implementation. The active runtime lock now downloads only SHA-256-pinned public Release assets and corresponding source; the fallback remains historical code, not the active path.

## Corresponding source and notices — public Builder profile distribution

The published [matching source archive](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/tag/video-reverse-v1.10.6) includes FFmpeg, x264 and Emscripten source, Builder build scripts and profile-specific runtime code. Original source and binary archive hashes were independently checked before publication, and public download hashes were checked after publication.

The original 1.10.6 binary ZIP files contain FFmpeg/x264/Emscripten license texts and `BUILDINFO.txt` showing the GPL/x264 linkage. Their embedded general `THIRD_PARTY_NOTICES.md` omits the new `video-reverse` profile name; the separately SHA-256-pinned [video-reverse GPL/x264 license addendum](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/blob/feat/video-reverse-poc/docs/VIDEO_REVERSE_LICENSE_ADDENDUM.md) explicitly discloses that limitation. It does not alter the already-audited binary bytes.

The existing Builder-wide `v1.10.6` Release **does not** contain the `video-reverse` assets. The separate [video-reverse-v1.10.6](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/tag/video-reverse-v1.10.6) profile Release **was published on 2026-10-19**; its profile-specific tag differs from the original binary's embedded `Release tag: v1.10.6` label. The published Release notes explain that original build metadata and provide source and notices. See the Builder [publication handoff](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/blob/feat/video-reverse-poc/docs/VIDEO_REVERSE_PUBLICATION_HANDOFF.md).

## GitHub Pages MT isolation helper

The GitHub Pages `/mt/` deployment conditionally loads `coi-serviceworker` **v0.1.7**, by Guido Zuidhof and contributors (MIT). Its exact commit and SHA-256 are pinned in `coi-serviceworker.lock.json`, with its notice in `licenses/coi-serviceworker-MIT.txt`. This helper is **not embedded** in the ST or MT single-HTML artifacts; it is a hosted Pages isolation fallback and is not a media upload or telemetry component.

This document records the published dependency's provenance. Reverse Clip itself remains a Draft RC and has not been publicly released or integrated into Browser Kitty.
