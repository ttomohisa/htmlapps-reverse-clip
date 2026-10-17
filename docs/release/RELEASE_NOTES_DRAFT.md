# Reverse Clip v0.9.0 — Release Notes (DRAFT ONLY)

**NOT FOR PUBLICATION.** RC preparation, NOT a signed-off release candidate; G2/G3 OPEN.

Reverse Clip creates locally processed reversed or forward-back (Ping-pong) H.264 MP4 clips. Output is 15fps and silent by default; supported source audio can use reverse AAC. Source files are not uploaded.

Desktop Chrome ST/isolated MT CI validated marked H.264 frame order, AAC mono/stereo, VFR/sparse, 30/60fps input to 15fps output, H.264 MOV with 90/180/270° display-matrix orientation, invalid/corrupt input fail-closed, and local ST `file://` readable/self-extract HTML. On 2026-10-17, the owner confirmed **all four requested basic checks on the latest v0.9 ST Android Chrome PR Preview**: Reverse/save/replay, Ping-pong/save/replay, cancel/retry and audible reversed audio. These are owner-reported results, not independently logged device/media evidence; **The owner later confirmed all four requested checks on the temporary MT Android Chrome QA site as well**, replying 「MTも4つOK」. Both ST and MT reports are user-reported smoke results, not independent device/media logs. See [ST owner smoke](ANDROID_ST_RC_OWNER_SMOKE.md) and [MT owner smoke](ANDROID_MT_RC_OWNER_SMOKE.md).

Limits: HEVC/HDR color fidelity not guaranteed; unsupported synthetic HEVC 8/10-bit rejected in the tested desktop Chrome. Multiple source audio tracks cannot be selected. Android input providers may trigger <=64MiB whole-source fallback copy, conflicting with original G2. Higher quality and long export remain experimental. Download initiation does not prove OS save completion. iPhone deferred.

The existing Builder-wide `v1.10.6` GitHub Release does not contain this profile. The exact audited ST/MT/source files were independently staged as a **temporary review candidate** in [CI #39004330416](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/actions/runs/39004330416). A distinct profile-scoped `video-reverse-v1.10.6` GitHub Release is only **proposed**; no tag or Release has been created. The importer has a future fail-closed path for source/binary hashes and a validated cache, but the runtime lock still points at expiring Actions artifacts.

The original pinned Builder ST/MT ZIPs include GPL/x264 licenses and correct `video-reverse` BUILDINFO, but their generic notices omit the dedicated profile name. A [GPL license addendum](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/blob/feat/video-reverse-poc/docs/VIDEO_REVERSE_LICENSE_ADDENDUM.md) was separately audited and staged with unchanged core/source binaries in [CI #39006344474](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/actions/runs/39006344474). The future importer requires SHA-256-pinned public addendum, corresponding source and binary ZIP. Permanent GPL publication and final sign-off remain outstanding.

See [RC_CHECKLIST.md](RC_CHECKLIST.md). No tag, release, merge or Browser Kitty integration until final MT distribution verification, source-complete immutable GPL Builder distribution, supported-platform scope and Gate G2/G3 acceptance are resolved.


**2026-10-17 review:** For the proposed initial Windows Chrome/Android Chrome short H.264 scope, remove unconditional iPhone/HD 3×/precise RAM requirements from P0; do not weaken valid output, local processing, critical error handling, core Android smoke or license requirements. Do not advertise HD/HEVC/HDR as fully supported.
