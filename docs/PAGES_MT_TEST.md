# Reverse Clip — experimental GitHub Pages ST/MT test deployment

**Purpose:** Enable physical Android MT testing without merging the unfinished
Reverse Clip v0.6.0 and Builder development PRs. This is a publicly reachable
**development test page, not a stable or licensed-release approval**.

## Merge only the dedicated Pages PR

This limited PR modifies the main-branch GitHub Pages deployment workflow and
adds a published-site verifier; it **does not merge** Reverse Clip PR #1/#2,
FFmpeg Builder PR #16, or Browser Kitty. It does not change the main app's
source, change runtime dependencies or create a tag/Release.

- **Verified source app head:** `e5f66428c501090513b6fa0da925b1d1bffbbfb8`
  (from the app's Draft PR #2; the PR remains unmerged).
- **Verified app CI:** [#38688780206](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38688780206).
  Real ST/MT Chrome video, AAC, service-worker isolation, offline and frame-order
  regressions are part of that source CI. The deployment itself does not rebuild.
- **Pinned artifact:** `11950309753`,
  `standalone-html-e5f66428c501090513b6fa0da925b1d1bffbbfb8`,
  expires **2026-10-29 05:48:56 UTC**. The Pages workflow downloads this
  exact artifact and checks three pinned SHA-256 fingerprints, failing closed.
  The generated HTML embeds the runtime; no browser-side CDN is required.

| GitHub Pages route | Exact file | Execution |
| --- | --- | --- |
| `https://ttomohisa.github.io/htmlapps-reverse-clip/` | `pages-dist/index.html` | Single-thread (ST), no isolation headers |
| `https://ttomohisa.github.io/htmlapps-reverse-clip/mt/` | `pages-dist/mt/index.html` | Real multi-thread (MT), isolated by same-origin pinned `coi-serviceworker.js` |

GitHub Pages cannot be relied upon to set route-specific COOP/COEP HTTP
response headers. The MT Pages wrapper instead registers a pinned
same-origin COI Service Worker scoped to `/htmlapps-reverse-clip/mt/`.
**The very first visit can automatically reload** to activate isolation.
When the worker is unavailable (such as restricted/private browsing), MT
must report unavailable instead of silently falling back to ST.

## 2026-10-15 — Mobile UX candidate for testing (version remains v0.6.0)

The owner already confirmed that the previously failing H.264 High,
37.806s, ~1.03fps Presentation Video Maker output **succeeds on
PC and Android** using the Builder 1.10.6 MT Pages snapshot. The
fix is retained unchanged in this HTML refresh.

The new pinned snapshot is an **unmerged Draft PR #2 user-interface
candidate**; it does not merge the incomplete app or Builder into
the main branch, change the WASM binary, or increment the application
version to v0.7.0. On phone-sized screens (<=600px), the app exposes:

- **Video:** choose/capture a video; Edit is unlocked only after
  playable metadata. Source filename/duration remain accessible.
- **Edit:** trim the source, adjust reverse/ping-pong, output quality
  and optional supported audio; cancel/retry; inspect any errors.
- **Result:** unlocked only after a genuine verified MP4 is ready;
  show video, actual output resolution/FPS, duration/size, editable
  filename, and a Download action. Changing an edit or input discards
  the prior result. A download action reports that the browser has
  started downloading, *not* that the OS has saved the file.
- **Optional diagnostics and development details:** kept accessible
  in native collapsible sections. An export failure displays a direct
  path to the diagnostic JSON download. No technical section
  blocks ordinary save workflow by default.

Desktop >600px retains the existing continuous layout. No fixed
bottom overlay obstructs downloads. JA/EN copy is supported. No
media byte is uploaded or stored in localStorage/IndexedDB/Cache.

**CI source verification:** [Reverse Clip #38688780206](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38688780206)
is green for the Windows-built ST and MT standalone HTML,
mobile JavaScript regressions and actual Chrome offline/MP4/AAC,
cancellation, WebCodecs sparse low-FPS cases, service-worker
isolation and 320/360/390px responsive checks. A separate
local Chrome smoke verified Video/Edit/Result, real MP4 download,
return to Edit, and opening the collapsed diagnostics. **These
are automated desktop/browser results, not physical Android UX
acceptance.**

After the owner's merge of **only this Pages UI refresh PR** and a
successful published-site Chrome smoke, please test the mobile
workflow with any already-working short video. Confirm the
Video/Edit/Result navigation, MP4 playback/download, source change,
and on-screen diagnostics behavior. There is no need to repeat
the previously accepted low-FPS source investigation unless the
UI refresh causes a new failure.

**Still open:** Gate G2 device memory and no-full-source-copy
requirements, audio seam listening, high-res real-camera matrix,
cancel/retry physical phone observations, permanent GPL
corresponding-source distribution. iPhone remains deferred. Neither
this experimental test page nor its source review candidate is a
stable or legal/GPL-approved public product release.

## 2026-10-15 experimental sparse-video patch test

This version-refresh changes only the pinned Pages **test** binaries
to Builder **1.10.6** (source commit
`8e60da7cf9de644ce3f6cce9c007b17e6a385c53`) and adds richer
published-site MT verification. It does NOT merge the unfinished
Reverse Clip or Builder development PRs.

The owner reported ST succeeding but MT failing with `30 expected /
24 actual` frames on a 37.806s H.264 High presentation video. A
synthetic 39-frame / 37.806089s equivalent reproduced a related
older-WASM 28-vs-9 return-chunk failure. The 1.10.6 source normalizes
VFR to 15fps **before** selecting a bounded frame-grid interval and
adds best-effort MT pthread teardown per chunk. Strict segment frame
counts remain mandatory.

Before physical-device retesting, require real Chrome `/mt/`
validation of both **2s Ping-pong / 58 output frames** and
**10s Ping-pong / 298 output frames** using the 39-sample input. The
script must confirm actual downloaded H.264 MP4, full FFmpeg decode,
crossOriginIsolated / SharedArrayBuffer and no unexpected network
request. The old published snapshot was only 1s-verified.

**GPL matching source:** independently checked Builder 1.10.6
source-and-binary candidate from
[review-only CI #38617100332](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/actions/runs/38617100332)
(artifact `11920042823`, expires 2026-10-21). It contains the
matching FFmpeg/x264/Emscripten sources, the new pthread cleanup,
both ST/MT binaries and notices. This is not a permanent immutable
public Release or final legal approval, and does not prove Android
RAM stability.

This is still an experimental test snapshot: the actual original
media and physical Android must be retested. iPhone is deferred.
No change is made to Browser Kitty.

## User action

1. Review and merge **only the dedicated mobile-UI Pages refresh PR** after its PR checks are green.
2. Watch its GitHub Actions `Deploy Reverse Clip experimental ST/MT to GitHub Pages`.
   If the workflow summary says GitHub Pages is not enabled, open
   **Repository Settings → Pages → Build and deployment → Source: GitHub Actions**,
   then rerun that workflow. No other branch has to be merged.
3. After deployment and live MT Chrome verification are green,
   open the `/mt/` URL on Android Chrome. Choose a previously working
   video and try the **Video → Edit → Result → Save MP4** flow once.
   Confirm that settings remain easy to reach, the MP4 plays/downloads,
   and the save hint does not pretend to know the phone's destination.
4. If something fails, use **Error details → Download a diagnostic
   report**; otherwise simply report that the mobile steps and download
   were usable. High-resolution repeated tests and audio listening
   remain separate G2 acceptance work.

## Limits and retention

- This PR publishes an **immutable experiment snapshot**. Further commits to
  unfinished PR #2 do not silently alter the Pages test. To update it, review
  a newly built and verified Pages CI artifact and update this workflow's pin
  in another PR. This protects reproducibility and GitHub Actions minutes.
- The source CI artifact expires on October 29; a **new** deployment attempt
  after that date fails closed unless intentionally repinned. A successful
  existing Pages deployment remains served until replaced/deleted.
- The embedded experimental FFmpeg/x264 WASM has a GPL license. A reviewed,
  immutable public binary-plus-corresponding-source release remains an
  outstanding product-release obligation. Existing source and matching
  review archive evidence are documented in the Builder Draft PR #16.
  Do not advertise this Pages experiment as a finished release.
- GitHub Pages availability, published-site success and the exact live URL
  cannot be asserted before the owner merges the dedicated workflow PR
  and its `deploy` / `verify-live-mt` jobs pass.
- No user data leaves the browser during media conversion. `connect-src
  'none'` remains in both prebuilt ST/MT HTML outputs; user media is
  not sent to the Pages server.
- iPhone physical testing remains deferred. Browser Kitty integration
  remains out of scope.
