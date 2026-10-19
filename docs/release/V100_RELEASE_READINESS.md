# Reverse Clip — v1.0.0 release readiness

**As of 2026-10-19:** Reverse Clip v0.9.0 RC is integrated into `main` (merge `70cc23bf526f38f416b465943b031f4cb167bb7c`). The app has **no v0.9.0/v1.0.0 GitHub Release**, and **G3 is not yet accepted**. The dedicated Builder [`video-reverse-v1.10.6`](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/tag/video-reverse-v1.10.6) dependency and its matching GPL source are already public.

**Ordering:** finish v1.0.0 and its app distribution **before touching the Browser Kitty main repository**. This file does not authorize a v1.0.0 tag or app Release. The owner performs merges.

## Initial supported scope (the previously agreed practical RC scope)

- Windows Chrome and Android Chrome: short H.264 MP4 clips (roughly 0.5–5 seconds, 360/720px-oriented usage), reverse and forward/back ping-pong, optional reversed AAC for recognized inputs.
- ST standalone readable/self-extract HTML (`file://`), and MT only where cross-origin isolation is available. Do not claim local `file://` MT support.
- Input files remain on-device; built HTML has `connect-src 'none'`. The Android provider fallback copies a source to memory only conditionally for inputs at or below 64 MiB.
- iPhone Safari, HEVC/HDR correctness, selectable multiple audio tracks, 1080p/long-running/high-memory stability and all device/providers are **not** claimed supported. Preserve honest UI limitations.
- The historical stricter G2 (iPhone + Android 3× full-HD and unconditional no-copy) remains **NOT PASSED**, not retroactively reclassified. Use [revised scope](REVISED_ACCEPTANCE_SCOPE.md) only for the proposed initial stable release, and explicitly decide app G3 against that scope.

## Evidence already obtained — do not rerun without a relevant source change

| Item | Evidence |
| --- | --- |
| Public Builder ST/MT, matching source and GPL notice | [Builder release](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/tag/video-reverse-v1.10.6), audited SHA-256 |
| ST/MT standalone builds, H.264 reverse/ping-pong and AAC real Chrome | [CI #39180735282](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/39180735282) |
| Hosted MT isolation and real MP4 browser test | [CI #39180735321](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/39180735321) |
| Final v0.9 stack-to-main reconciliation browser CI | [CI #39182186680](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/39182186680) |
| Last v0.9 PR Preview | [CI #39182186687](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/39182186687) |
| Merged `main` ST/MT Pages build + deployment | [CI #39182815120](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/39182815120) |
| Android ST and separate MT basic 4-action tests | Owner-reported PASS 2026-10-17, see [RC checklist](RC_CHECKLIST.md); not independent hardware logs |
| JA/EN desktop and mobile-viewport screenshots | Existing PNGs and SHA-256 asset manifest, [RC screenshot evidence](RC_SCREENSHOT_ASSET_MANIFEST.json) |

## Only remaining release actions

1. **Finish release-facing copy and artifacts.** Remove stale `Draft`, unmerged PR, expired artifact, pending public GPL source claims from present-tense UI/README/notes. Keep historical test reports clearly dated. Check screenshot, favicon, EN/JA, small-screen layout and unsupported-format disclosures.
2. **Final v1.0.0 candidate.** After the release scope and G3 decision, update `app.config.json`, the HTML's displayed version, READMEs, changelog, offline/readable and self-extract filenames. Run the existing repository/CI build from the exact tag candidate, then verify four ST/MT HTML distribution files, SHA-256 manifest, no runtime network, safe error/empty/result/cancel states and isolated MT production deployment. No new exhaustive performance matrix or additional GPL legal audit.
3. **Publish the app release.** Once G3 and the versioned artifacts are reviewed, the owner merges the release PR. Create the v1.0.0 app tag/GitHub Release (not the Builder tag) with its downloadable standalone files, release notes and a visible pointer to the matching GPL Builder source. Check public URLs. Only **then** consider Browser Kitty integration in a separate task.

**Do not advance the app version to 1.0.0 merely because the GitHub PRs were merged.** An explicit G3 decision based on the agreed limited scope is still necessary. A successful Builder WASM Release is not the app Release.
