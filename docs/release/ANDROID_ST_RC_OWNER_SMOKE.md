# Reverse Clip v0.9.0 — Android ST RC owner smoke report (2026-10-17)

**Recorded:** 2026-10-17, after the owner was asked in the Browser Kitty development chat to test four specific workflows. **Evidence type: user-reported results; no remotely captured logs, media or device diagnostics.** This is not a laboratory benchmark or an independent physical-device certification.

## Build actually requested

- App: Reverse Clip v0.9.0, Android Chrome, **ST (single-thread) Cloudflare PR #2 Preview**.
- Test URL provided: https://r1414006067-pr-2-bk-previews.ttomohisa.workers.dev
- Latest app preview at the time: PR #2 head `b91c49bcb10f8c3f852845c474072cadd25ec5d3` ([preview CI #38946332100](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38946332100), successful). This identifies the requested deployment; the user did **not** independently provide a build hash or diagnostic JSON.
- The owner replied **「4つともOK」** to all four checklist items below. This is valid owner-supplied *smoke feedback* for the requested ST Preview; it is not an independent capture of settings, playback files or timestamps.

## Exactly what was asked and confirmed

| Check | Instruction sent before the owner tested | Result |
| --- | --- | --- |
| Reverse | Use a short (~5-second) H.264 MP4 segment, make a reverse MP4, save and play it on Android; long edge at most 720 px | **USER-REPORTED PASS — ST** |
| Ping-pong | Make a ~2-second forward/back clip, save/replay and check that direction turns correctly | **USER-REPORTED PASS — ST** |
| Cancel/retry | Interrupt an export, then start again successfully | **USER-REPORTED PASS — ST** |
| Reversed audio | Reverse an audio-bearing source and listen for intelligible reverse audio without an obvious failure | **USER-REPORTED PASS — ST** |

The response was a collective approval of those four prompts. **Do not infer** the exact actual selection length or input/output resolution, the original video codec beyond the requested test constraints, verified AAC stream structure/precise synchronization, whether a stale result was inspected, the file provider and filename, a saved MP4 hash, the phone model, the Android or Chrome version, processing time, or peak RAM.

## Coverage and remaining release work

- **Covered at the smoke-feedback level:** one Android Chrome **ST Preview** user journey involving reverse, ping-pong, retry and audible audio. No new regression was reported in these workflows.
- **Not covered:** latest **MT (multi-thread/cross-origin isolated)** app running on a real Android phone; hosting/runtime changes for the final MT distribution; extra input providers/large files; explicit output file metadata and device/browser model details; rigorous unsupported-input and cancellation-stale-MP4 device audit. Desktop CI separately covers ST and MT media integrity.
- **Unchanged gate decision:** original Gate G2 **NOT PASSED** (historical criteria differ); Gate G3 **NOT PASSED**. Review-only Builder Actions WASM remains `temporary-not-release`; durable, corresponding-source-complete GPL binary/source publication and owner sign-off are not complete. No release, merge, tag or Browser Kitty import is approved by this smoke feedback.

The revised [P0/P1/P2 acceptance scope](REVISED_ACCEPTANCE_SCOPE.md) is still a review proposal. The next meaningful phone check should focus on the **actual production-intended isolated MT build**, rather than repeating all four tests unnecessarily on the existing ST preview.
