# Reverse Clip v0.9.0 — Android MT RC owner smoke report (2026-10-17)

**Status: USER-REPORTED PASS for four requested Android MT workflows. This is not a release approval.** The user replied **「MTも4つOK」** after receiving a direct link to the temporary MT QA application and instructions to repeat the previously passed ST checks. No user video files, screenshots, hashes, diagnostics, timing or hardware metadata were sent to ChatGPT.

## Actual environment requested

- App: Reverse Clip v0.9.0 development Draft PR #2, **multi-threaded** (MT) preview.
- Test link that the user was given: https://rc-reverse-clip-mt-qa.ttomohisa.workers.dev/mt/
- Hosting: temporary, separately named Workers.dev QA site; **SHA-256-pinned same-origin COI Service Worker** applied only to `/mt/`. This is **not** the regular Cloudflare ST PR Preview or a permanent Builder Release.
- Tested application branch snapshot at the time of the request: `d2314720b0f6c9dddd2f192b76a919d979e9e328`. Both the [MT deploy/test workflow #38955447221](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38955447221) and [standalone Chrome CI #38955448388](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38955448388) completed successfully on this commit. The user's reply does not independently identify a served commit hash.
- Date: 2026-10-17 JST. Android Chrome physical device as requested; exact model, Android version and browser version were **not provided**.

## What the user confirmed

Before testing, the user was asked to open the MT QA URL in Android Chrome (not ST Preview) and check the four specific operations used for the prior ST smoke. The reply was: **「MTも4つOK」** ("all four on MT are OK too").

| Requested Android MT action | Evidence category | Result |
| --- | --- | --- |
| Short H.264 MP4 Reverse → save → replay | Owner response to requested scenario | **USER-REPORTED PASS — MT** |
| Short H.264 MP4 Ping-pong → save → replay and confirm direction changes | Owner response to requested scenario | **USER-REPORTED PASS — MT** |
| Cancel conversion → retry successfully | Owner response to requested scenario | **USER-REPORTED PASS — MT** |
| Reverse supported source audio and listen for obvious failure/noise/silence | Owner response to requested scenario | **USER-REPORTED PASS — MT** |

The user confirmed the requested four operations collectively. **Do not invent** the precise selected duration, source codec/profile, actual file provider, AAC sample details or independent audio synchronization measurement, saved output bytes and hashes, system download destination, failure-free memory/CPU metrics, COI/SAB diagnostic traces from the phone, or device/browser version.

## Other independent evidence and remaining gates

- Actual desktop Chrome against the **deployed MT QA host** established the same-origin Service Worker isolation, `SharedArrayBuffer`, correct ST unisolated root, and genuine 1-second H.264 reverse MP4 export/save with ffprobe verification. See [MT_QA_BROWSER_EVIDENCE.md](MT_QA_BROWSER_EVIDENCE.md) and workflow #38955447221.
- Earlier separate Android **ST** smoke received the user's reply **「4つともOK」**. See [ANDROID_ST_RC_OWNER_SMOKE.md](ANDROID_ST_RC_OWNER_SMOKE.md). Therefore **both ST and MT basic four-action Android smoke checklists have user-reported passes**. These are not independent media-file certifications.
- **Original Gate G2 historical NOT PASSED** (older, broader quality / device / zero-copy criteria). Revised P0 Android main-flow **smoke-feedback portion** has been fulfilled, subject to documentation limitations and no new regressions when the release distribution changes. **Gate G3 NOT PASSED**.
- FFmpeg/x264/Emscripten corresponding-source-complete **permanent/public GPL binary+source distribution** and sign-off are outstanding. The current runtime lock still says `temporary-not-release`; the review candidate Actions artifact expires 2026-10-21. Exact final distributed MT deployment and subsequent source/asset changes must be verified before a release claim.
- No PR merges, releases, tags or Browser Kitty main-site changes were authorized by this QA report. The temporary MT QA site should be removed once no longer needed.

**Next release work:** finish the Builder corresponding-source distribution and review, then revalidate the exact final deployed ST/MT bytes and release scope, without repeating prior 4-action device smoke unnecessarily unless the runtime or hosting behavior changes.
