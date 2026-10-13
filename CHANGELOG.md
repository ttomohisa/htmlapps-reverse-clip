# Changelog

## [0.4.0] - 2026-10-13 (experimental silent ping-pong implementation)

- Stage a real `pingpong` video mode (forward H.264 chunks followed by reverse return), next to existing reverse mode. The dedicated Builder `video-reverse` profile now supports a bounded `--direction forward` chunk, using the same x264 encoder and scale/fps settings, and extends the public-libav MP4 remux join to at most **16** chunks.
- The frame-exact composition for N selected source frames is **0..N-1, N-2..1** (2N-2 frames). Skip the turning frame on the return, and the starting frame at the end so repeated playback has no doubled loop-boundary frame. Do not skip arbitrary H.264 packets. No audio yet.
- A pure shared timeline planner balances chunks to avoid a 1-frame reverse tail, preserves 0.5–10s trim and HD pilot <=5s, counts all output frames before saving, and rejects missing or excess encoded packets in the Builder.
- Modes are exclusive; changing mode clears stale output and updates the suggested suffix between `-reverse.mp4` and `-pingpong.mp4` without overwriting a user-edited filename. UI previews only the completed MP4 and shows expected duration.
- The ping-pong control is **fail-closed** until both real ST/MT binary SHA-256 values are pinned. The experimental Builder build at commit `076fe727...`, CI run `38345618409` produced distinct verified new cores; their hash-locked bytes are integrated, with real Chrome ST/MT ping-pong playback and frame-order regression. This is temporary Actions storage until a permanent source-complete GPL release is authorized.
- v0.4.0 remains a development milestone: Android physical MT, VFR/rotation, full-size 720p/1080p and an immutable corresponding-source GPL release require further acceptance. Do not update Browser Kitty.


## [0.3.0] - 2026-10-13 (Trim & Reverse development)
- Add two native, touch/keyboard-accessible trim handles directly below the source video, synchronized with numeric start/end fields and an illustrated selected interval. Keep user-typed invalid numeric ranges invalid rather than silently shortening them. Moving a handle enforces 0.5s minimum and current output quality limits.
- Add "Play selected section" of the **original** source; playback stops at the end boundary. Actual reversed MP4 remains previewed only after conversion and may be saved with a user-edited filename.
- Replace favicon and header icon with the user-supplied 64x64 green/white SVG (verified SHA-256), change JA language button label from 日本語 to JA, change local badge to 完全ローカル処理, replace technical branding subtitle with an app-purpose description, remove obsolete feasibility footer suffix, and show ST/MT only under Build information.
- Prevent background scrolling on the Help dialog via fixed-body scroll lock; preserve scrolling inside the dialog and restore body position on Close/Escape/backdrop.
- Add real Chrome ST/MT test cases for middle/tail selections, downloaded MP4 frame order, handle keyboard interaction, source play range, content/icon/lang labels, modal background lock and responsive viewports.
- The actual Android device, full 720p10s / 1080p5s, ping-pong, audio and stable source-complete GPL distribution remain separate acceptance gates. Do not open a Browser Kitty integration PR yet.


### v0.2.0 — 2026-10-13 App Foundation follow-up (safe import and recovery)
- Validate only the first 32 bytes of an MP4/MOV's ISO-BMFF/QuickTime atom structure before handing it to browser playback. Reject obvious renamed text/RIFF/EBML without reading or copying a 1GiB video; full codec compatibility still depends on native browser/FFmpeg decoding.
- Bound stuck photo-provider reads or stalled media metadata to 30 seconds, show a localized recovery message, revoke stale Blob URLs, and reject any late async result from the old source.
- Generate a safe default MP4 filename from the selected source; include v0.2.0 source phase/error code (not media name/data) in the opt-in diagnostic JSON.
- Extend real Chrome ST/MT tests for corrupt container headers, invalid codec-like media, stalled and stale provider reads, source switching and automatic save names. Add targeted Node unit tests.
- Add an explicit "Cancel loading" action while a source is being inspected; it invalidates the file generation immediately instead of forcing users to wait for the 30-second timeout. Pending browser/provider reads may finish internally but can no longer change the app.
- Reject multi-video drag/drop instead of silently taking the first file. Remove the inert focus stop on the drop area; the actual choose/record buttons remain keyboard accessible.
- Exercise ST/MT UI at 320/360/390/1024px in the real-browser smoke suite to catch horizontal overflow.
- Physical Android device intake/error and repeated MT performance acceptance remain **PENDING**. Browser Kitty PR #41 remains closed unmerged.


## [0.2.0] - 2026-10-13 (App Foundation / development milestone)
- Advance beyond the v0.1.x technical-spike series to the v0.2.0 app-foundation milestone. This is a working development build, **not** a completed G1/G2/G3 or stable public release.
- Introduce an explicit generation-aware source state machine: `empty / inspecting / ready / error`; preserve validation and decoder errors across JA/EN switching, including empty videos.
- Keep source replacement and rejected input fail-closed: clear previous results, disable stale edit/save controls, and reject late async input reads. Continue using object URLs for source preview without uploading media.
- Preserve the proven ST/MT separate FFmpeg assets, local-first single HTML, `file://` ST build and 10s video-only reverse experiments; newer features remain experimental.
- Expand Chrome ST/MT regression to cover invalid type, zero-byte MP4, unplayable MP4, language switching after an error, and recovery when a valid video is selected again.
- **Pending v0.2.0 completion evidence:** Android physical-device intake/replacement/error-path tests. Do not claim this milestone fully accepted until those checks are recorded.
- Browser Kitty PR #41 remains closed unmerged. No further portal PR until Reverse Clip is finished.


## [0.1.7] - 2026-10-13 (experimental HD 720p-class output)
- Keep the existing long-edge 360px / 720px presets and add a **separate** long-edge 1280px pilot for true 1280×720 landscape or 720×1280 portrait source without upscaling.
- Hard-cap the HD 720p-class pilot at 5 seconds, preserve up-to-2-second FFmpeg chunks and the existing 96 MiB estimated frame-buffer limit. No automatic shortening or quality downgrade.
- Disclose device-memory/performance uncertainty in both JA/EN. Real-device Android ST/MT 720p output is **not** claimed until tested.
- Expand Chrome ST/MT smoke with native 1280×720 H.264 source, 1-second real HD MP4 download and ffprobe dimension/codec/frame checks.
- Browser Kitty remains deferred; do not merge or release.


## [0.1.6] - 2026-10-13 (cancel/retry & source-switch hardening)
- Prevent a WASM runner that finishes initializing *after* a cancellation or file change from being published or executed. Dispose each conversion's own runner even when stale, without touching a newer conversion.
- Make output-video metadata loading abortable; cancellation immediately cleans up preview listeners/timers rather than waiting for a timeout.
- Restore availability of the Convert button through the existing range/input/isolation guards, not just an old range-valid flag.
- Expand actual ST/MT Chrome smoke to cancel during delayed WASM initialization, change input mid-load and then successfully export H.264 MP4 again.
- Bring the existing frame-indexed 10-second/fractional-boundary regression into the hosted ST/MT Chrome CI, with repeat-run output validation, MP4 frame-order checks and simulated mobile file transport.
- Keep the experimental input/output/10s limits and temporary pinned GPL Builder artifacts unchanged; this is not a claim of Android device MT or release readiness.
- Stage a future immutable Builder Release asset importer that validates the exact ZIP digest, ST/MT core hashes and included GPL/BUILDINFO notices; current runtime lock still selects the temporary Actions artifact.
- Per owner direction, **Browser Kitty integration is postponed until Reverse Clip is complete**; mistakenly opened Browser Kitty Draft PR #41 was closed unmerged. Do not open a replacement now.


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
