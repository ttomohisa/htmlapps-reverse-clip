# Third-party notices — Reverse Clip v0.9.0 release candidate

**Status: review-only, not a published app or approved GPL release.**

Reverse Clip's original application source is licensed under the repository's MIT license. Its bundled **video-reverse** WebAssembly runtime links **FFmpeg n9.0.1 and x264**, and is separately identified in its binary metadata as **GPL-2.0-or-later**, not MIT. Both the single-thread (ST) and multi-thread (MT/pthreads) variants use the same license classification. The application license does not replace FFmpeg/x264 license requirements. Review of the combined distribution's applicable license obligations remains pending.

## Current compiled runtime provenance

The current experimental runtime is specified by `reverse-runtime.lock.json`:

- Builder repository: `ttomohisa/htmlapps-ffmpeg-wasm-builder`.
- Exact compiled Builder commit: `8e60da7cf9de644ce3f6cce9c007b17e6a385c53`.
- Builder version: **1.10.6**; profile: `video-reverse`.
- FFmpeg revision: **n9.0.1**, commit `bf1b838f2ab88b4f8fd83443325c782ea0e0f7fa`.
- x264 revision: commit `31e19f92f00c7003fa115047ce50978bc98c3a0d`.
- Emscripten toolchain: **6.0.6**, source commit `ce75e06884093bcefb86a6b8fd56a5d62a4cc245`.
- Development-only compiled WASM Actions artifact: **11914029733**, from workflow run **38603383794**. This original artifact is scheduled to expire **2026-10-21T17:11:44Z**. It is **not** a permanent distribution location.

Exact variant-specific `ffmpeg.js` and `ffmpeg.wasm` SHA-256 values, and the shared `browser-ffmpeg.js` loader digest, are recorded in `reverse-runtime.lock.json`. Builds reject mismatches. The ST output supports standalone local use; the MT variant requires cross-origin isolation and SharedArrayBuffer.

The current build-time expiry fallback reuses only the independently SHA-256-audited, **review-only** Builder package **12145680508** (scheduled expiry **2026-11-17T17:48:11Z**). It preserves the same binaries and source; it does **not** change their license, mark them release-approved, or provide lasting public availability.

## Corresponding source and notices — publication remains pending

A matching source-complete **review candidate** has been technically audited. It includes FFmpeg, x264, Emscripten source, Builder build scripts and profile-specific runtime code. The source and binary archive checksums match the audited record, but independent corresponding-source/licensing review and durable public source availability have not yet been approved.

The original 1.10.6 binary ZIP files contain FFmpeg/x264/Emscripten license texts and `BUILDINFO.txt` showing the GPL/x264 linkage. Their embedded general `THIRD_PARTY_NOTICES.md` omits the new `video-reverse` profile name; the separately SHA-256-pinned [video-reverse GPL/x264 license addendum](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/blob/feat/video-reverse-poc/docs/VIDEO_REVERSE_LICENSE_ADDENDUM.md) explicitly discloses that limitation. It does not alter the already-audited binary bytes.

The existing Builder-wide `v1.10.6` Release **does not** contain the `video-reverse` assets. A separate `video-reverse-v1.10.6` profile Release is **proposed but not published or approved**; its proposed tag differs from the original binary's embedded `Release tag: v1.10.6` label. Any eventual release must make that discrepancy explicit and provide the appropriate source and notices. See the Builder [publication handoff](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/blob/feat/video-reverse-poc/docs/VIDEO_REVERSE_PUBLICATION_HANDOFF.md).

## GitHub Pages MT isolation helper

The GitHub Pages `/mt/` deployment conditionally loads `coi-serviceworker` **v0.1.7**, by Guido Zuidhof and contributors (MIT). Its exact commit and SHA-256 are pinned in `coi-serviceworker.lock.json`, with its notice in `licenses/coi-serviceworker-MIT.txt`. This helper is **not embedded** in the ST or MT single-HTML artifacts; it is a hosted Pages isolation fallback and is not a media upload or telemetry component.

This document describes the experimental code and known licensing status. It is not legal approval or permission to publish a public Release, tag, or production Browser Kitty integration.
