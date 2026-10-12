# Changelog

## [0.1.5] - 2026-10-12 (two real ST/MT WASM distributions)
- Request dual ST/MT pthread builds in the dedicated Reverse Clip Builder profile.
- Generate ST + MT readable and self-extract single HTML, with separately pinned JS/WASM hashes.
- Publish GitHub Pages root (ST) and /mt/ (MT). A fixed, MIT-licensed, SHA-256-verified same-origin COI Service Worker is deployed **only** under Pages /mt/.
- MT conversion requires crossOriginIsolated plus SharedArrayBuffer; missing isolation disables the MT conversion UI with a clear Japanese/English explanation.
- Prepare Browser Kitty to use MT with route-scoped COOP/COEP/CORP; no global cross-origin isolation and no silent ST fallback.
- No claims of MT speedup or stable release until actual runtime/phone/hosting checks and permanent source-complete GPL runtime distribution.


## [0.1.4] - 2026-10-12 (experimental ten-second reverse)
- Extend the experimental range to 0.5–10 seconds at 15fps, with at most five 2-second segments for a full ten-second selection.
- Require an exact expected encoded-frame count for every WASM segment and for the joined MP4. Reject incomplete/extra-frame output, rather than silently accepting a loose duration.
- Show a distinct warning for selections over five seconds; preserve the Android photo-provider MEMFS workaround, separate quality presets and cancellation.
- Pin dedicated Builder commit b67b1e2 and its SHA-256-verified expiring Actions binary; no runtime fetch.
- Keep iPhone deferred and the original G1 not passed. Android 10s reliability and 720p/1080p-class export remain future tests.

## [0.1.3] - 2026-10-11 (experimental chunk reversal)
- Added 0.5–5-second video-only MP4 reversal via 1–3 sequential chunks on 2-second frame boundaries, each up to 2 seconds.
- Added public-libav MP4 joining in reverse chronological order, with timestamp and codec-parameter checks; no partial outputs are downloadable.
- Disclose 15fps frame snapping. Quality presets specify long edge 360/720px (not full native 360p/720p).
- Added conversion stage labels, cancel and output timing checks.
- Upgraded pinned Builder WASM to commit 47448852; source-complete permanent release and mobile performance tests remain pending.
- Gate G1 remains INVESTIGATE.

## [0.1.2] - 2026-10-11 (Android file read recovery)

- Avoid Android photo-provider `FileReaderSync.readAsArrayBuffer` failures during WORKERFS reads: immediately copy selected mobile videos **up to 64 MiB** into a new local in-memory Blob, then stage via FFmpeg MEMFS (no FileReaderSync).
- Retain memory-efficient WORKERFS on desktop and larger input; retry once using bounded MEMFS if its original file reader reports a known permission/readability error and the source is under 64 MiB.
- Show a useful explanation when an external photo/cloud provider cannot be read or when a large file cannot safely use the memory fallback.
- Keep video data entirely in-browser, preserve cancellation/stale-source guards, and record the input transport in the optional diagnostic JSON (not media bytes or source filename).
- Real Android/iOS MP4 output and the long-video memory limits remain unverified; Gate G1 stays INVESTIGATE.

## [0.1.1] - 2026-10-11 (experimental reverse-WASM preview)

- Added pinned Builder FFmpeg WASM import with SHA-256 verification and offline-capable single HTML.
- Added short silent MP4 reversal, result preview, filename editing, cancellation and diagnostic result summary.
- Reverse output is limited to 0.5–2 seconds and 360p/720p at 15 fps; mobile support remains unverified.
- Uses a temporary Actions artifact; must transition to permanent source-complete release before stable publication.
- Gate G1 remains INVESTIGATE.

## [0.1.0] - 2026-10-11 (feasibility)

- Started Browser Kitty Reverse Clip from the current standalone template.
- Added native frame-order tests, diagnostic browser probes, responsive bilingual UI, and explicit G1 gate.
