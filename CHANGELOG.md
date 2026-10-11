# Changelog

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
