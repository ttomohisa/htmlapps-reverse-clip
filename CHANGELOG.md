# Changelog

## [0.6.0] — Adaptive quality guard / memory and reliability (development, 2026-10-13)
- **2026-10-14 user-reported MT frame-loss regression (OPEN):** physical Android/PC MT returned `Stage: video-segments` and `Reverse frame count mismatch: expected=30 actual=24` for a 37.89s/396kbps MP4 while ST succeeded. The fail-closed integrity check stays enforced. Introduce an actual ST/isolated MT H.264 29.97fps/VFR reproduction test and expand structured diagnostics (chunk index, start, runtime, expected/actual frames), automatically opening error detail on failure. Do not claim a fix until real MT/browser reruns succeed for the affected source.

- **2026-10-14 (Android source memory path):** Add generation-aware, cancellable, <=2.5s FileReaderSync Worker probe of only the first/last 32 source bytes before preview of eligible <=64MiB mobile files. Use zero-eager-copy original File/WORKERFS when readable; keep the original bounded full-file MEMFS fallback on failed/unsupported Worker reads, plus the existing conversion-time provider retry. Abort/terminate probe and revoke URL on source switch, failure or timeout. **Full-copy-free G2 is still not satisfied** for fallbacks; physical Android testing is pending.
- Test real MP4 exports under a desktop Android-like UA for both unmodified WORKERFS and deliberately forced Worker-probe failure/MEMFS fallback. Add Node success/failure/abort/probe cleanup coverage. Maintain ST/MT standalone and silent/AAC regressions.

- **2026-10-14 isolated MT full-resolution:** [App CI #38464029860](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38464029860) PASSED cross-origin-isolated MT 720p10s Ping-pong with AAC (298 frames/19.867s, 11.20s processing) and 1080p5s silent Reverse (75 frames/5.000s, 5.87s processing). Real MP4s were saved, decoded and validated frame-by-frame. One run of each scenario only. Summed Chrome-related RSS (~3,203 / 2,846 MiB) may double-count shared pages and does NOT represent Android RAM. Full evidence: `docs/feasibility/V060_DESKTOP_MT_MEASUREMENTS.md`.
- Expensive MT HD job now requires explicit `workflow_dispatch` input `run_hd_mt=true` instead of running on every pull-request push. Routine ST/MT regression remains.
- Opt-in desktop performance harness can also collect Linux process-tree PSS/USS where supported; these are not device/tab RAM measurements. Release finished MP4 Uint8Array once its preview Blob takes ownership, shortening redundant buffering during metadata waits. Actual peak reduction needs separate proof.

- Tested the pinned real ST standalone in Linux Chromium at full 1280×720/10s and 1920×1080/5s: **11 real downloaded/decoded MP4 successes**, including three consecutive silent Ping-pong conversions per quality, two high-resolution AAC exports and 720p in-progress cancellation followed by successful retry. Frame identity and stream duration verified; precise observations and limitations in `docs/feasibility/V060_DESKTOP_ST_MEASUREMENTS.md`. This is not real-device/MT G2 approval.
- Strengthened the opt-in high-resolution stress harness to validate **every decoded frame against its expected original source position**, check optional AAC duration and cancel after real conversion progress rather than only at startup. Default CI still syntax-checks this potentially expensive test without running it.

- Introduce separate 720p-class (short edge <=720px / long edge <=1280px, 0.5–10s) and 1080p-class (short edge <=1080px / long edge <=1920px, 0.5–5s) experimental output settings, retaining compact 360/720px long-edge presets and no upscaling.
- Plan each Reverse/Ping-pong segment with an estimated YUV420 frame-buffer target <=48MiB instead of always up to 2 seconds. 1920x1080 at 15fps uses up to 16 frames per segment; 1280x720 uses up to 30. Frame-boundary and expected-frame-count safeguards stay enabled.
- Do not silently shorten user ranges or lower quality. On source replacement, cancellation or pagehide, discard old URLs/Worker; preempt separate audio-inspector WASM before exporting, restart after when necessary; reject repeated Create clicks and clean failed result previews.
- Synthetic timeline planning checks added. Real 720p10s/1080p5s files, repeated conversions on physical phones, actual memory peaks, human listening and GPL source-complete permanent distribution remain **PENDING**. See docs/feasibility/G2.md. No v0.6 acceptance claim, merge or Browser Kitty integration.


### v0.5.0 — Verified ST/MT AAC MP4 regression (2026-10-13)
- App [CI 38358181120](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38358181120) **passed** real ST/MT reverse audio and ping-pong MP4 exports: mono 0.5s/1s, independent stereo L/R 440/660Hz reverse at 5s, 10s stereo ping-pong 298 frames/19.867s, and silent input fallback. AAC was decoded to PCM and stream count/duration checked with FFmpeg/ffprobe.
- Builder [CI 38357268611](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/actions/runs/38357268611) passed ST/MT after fixing an accidental 120-frame-per-segment validation limit applied to full 298-frame A/V MP4 output. Individual chunk guard stays 120 frames; joined-output guard stays 960 with exact expected count.
- Audio defaults to No audio; the optional reverse-audio choice activates only after local supported source audio is verified. Runtime ST/MT hashes remain pinned to the temporary Actions artifact expiring October 20, 2026.
- Physical Android audio quality and repeated memory use, true HD target durations, 44.1kHz sources and camera display-rotation, and permanent corresponding-source GPL Release are still pending. No portal integration or merges.


### v0.5.0 — Audio A/V proof path and acceptance tests
- Implement source-scoped lightweight FFmpeg audio stream inspection (generation-aware, cancelable, no whole-file copy). Select audio only if a supported AAC/MP3/Opus/FLAC mono/stereo stream is positively identified.
- When the future pinned ST/MT core advertises `audio-mux`, render the original selected audio range in reverse or as a forward/return ping-pong track, then remux only the AAC into the already finished exact-frame H.264 MP4. All failures discard the pending result; existing no-audio exports stay unchanged.
- Add full real-Chrome ST/MT regression that, when gated on, decodes the AAC MP4 and checks actual reversed 300Hz/990Hz source tones, waveform direction in ping-pong, approximate 150ms audio/video duration alignment, and silent-source/cancel rejection. When gated off, it asserts users cannot select unverified audio.
- **Do not enable audio-mux solely on source code or compilation evidence.** Await Builder's actual A/V smoke, pin reviewed ST/MT SHA-256, run the app's real A/V CI, then review audio quality and mobile limitations.


## [0.5.0] - 2026-10-13 (Audio modes — implementation in progress)
- Start the real AAC audio pipeline in the dedicated FFmpeg WASM Builder while preserving the working video-only Reverse and Ping-pong modes.
- Add a bilingual audio choice UI (default no audio), state generation resets, capability checks and a strict fail-closed output gate. **The audio option stays disabled** until actual ST+MT A/V multiplexing, stream inspection and playback pass; availability of an AAC encoder alone is not sufficient.
- Record audio support explicitly in the embedded runtime manifest, without changing the pinned v0.4 video-only binary. Never claim old reverse-only assets contain AAC or a synced mux.
- In Builder Draft PR #16, develop a bounded AAC source-audio encoder with selectable forward/reverse filters, requiring a genuine audio stream; actual A/V mux, click-free joins, physical Android acceptance, permanent GPL Release and audio waveform verification remain future acceptance conditions.


## [0.4.0] - 2026-10-13 (experimental silent ping-pong implementation)

- Stage a real `pingpong` video mode (forward H.264 chunks followed by reverse return), next to existing reverse mode. The dedicated Builder `video-reverse` profile now supports a bounded `--direction forward` chunk, using the same x264 encoder and scale/fps settings, and extends the public-libav MP4 remux join to at most **16** chunks.
- The frame-exact composition for N selected source frames is **0..N-1, N-2..1** (2N-2 frames). Skip the turning frame on the return, and the starting frame at the end so repeated playback has no doubled loop-boundary frame. Do not skip arbitrary H.264 packets. No audio yet.
- A pure shared timeline planner balances chunks to avoid a 1-frame reverse tail, preserves 0.5–10s trim and HD pilot <=5s, counts all output frames before saving, and rejects missing or excess encoded packets in the Builder.
- Modes are exclusive; changing mode clears stale output and updates the suggested suffix between `-reverse.mp4` and `-pingpong.mp4` without overwriting a user-edited filename. UI previews only the completed MP4 and shows expected duration.
- The Ping-pong control remains **fail-closed** unless real Builder ST/MT binaries are SHA-256 pinned. Those checks now pass: Builder commit `fa52f86b27675f5c7b6c7fba52a73d38ac766687`, passing ST/MT smoke run [38346351559](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/actions/runs/38346351559), and corresponding embedded asset hashes in `reverse-runtime.lock.json`. This is a **temporary Actions artifact expiring October 20, 2026**, not a stable GPL corresponding-source release.
- Real ST/MT Chrome acceptance passed [app run 38347038030](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38347038030): 15→28, 31→60, 150→298 frames, saved and decoded H.264 MP4, exact turning-frame and source-boundary order, mode changes, cancel/retry.
- Additional [app run 38347758127](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38347758127) passed ST/MT: minimum 0.5s→14 frames, *genuinely* VFR video, intentional black footage, and native portrait 90×160 output, all via actual MP4 export/decode. No external video transfer.
- v0.4.0 remains a development milestone: real Android MT, camera rotation metadata, full-size 720p10s/1080p5s and immutable corresponding-source GPL release require further acceptance. Do not update Browser Kitty.


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
