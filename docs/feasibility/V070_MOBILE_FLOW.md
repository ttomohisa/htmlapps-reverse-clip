# v0.7.0 Mobile UX / Save Flow — implementation and acceptance

**State (2026-10-16): v0.7.0 development is now active on Draft PR #2
by owner-directed exception; Gate G2 remains OPEN / NOT PASSED. The
earlier v0.6.0 Pages candidate (PR #5) has owner-reported Android basic
workflow PASS, but was not this new v0.7.0 build. No tag or release.**
iPhone Safari is explicitly deferred. Windows Chrome/Edge and physical
Android Chrome are the current target devices.

## 2026-10-16 — keep conversion and Cancel visible on mobile

While the WASM conversion is active, the Video workflow navigation
button is disabled. The user stays in Edit, where the actual progress,
processing stage and Cancel action are visible. Attempts to invoke
Video navigation programmatically are guarded too. On successful
completion, failure, or explicit cancellation the Video navigation
is available again; output remains restricted to a verified MP4 and
there is no hidden background job from ordinary mobile navigation.

The mobile heading is kept visible after automatic step transitions.
The first Chrome regression caught the heading offscreen because the
template's global `html { scroll-behavior: smooth }` made the
`scrollIntoView({behavior:'auto'})` call **animate**, so the next
browser assertion ran while the document was still at its prior
scroll position. The fix temporarily overrides the root's scroll
behavior to `auto` for this explicit step-navigation scroll only,
focuses and scrolls the **heading itself** below the sticky app header,
and immediately restores the previous inline style. Manual nav
button taps still retain focus. This does not globally remove smooth
scrolling or change the media runtime.

**Verified:** [App CI #38845668240](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38845668240)
**ALL SUCCESS** on the final code commit `2c25329226f1f6092b69aa880a7a87406f3a0c20`:
Windows build/Node checks, actual ST and isolated MT Chrome
H.264/AAC/Ping-pong, 10s frame order, conversion+Cancel navigation
locking/unlocking, and focused headings visible at 320px width/568px
height. [PR preview #38845668281](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38845668281)
also passed. The optional full-resolution MT endurance job was not
run (SKIPPED). Physical Android/iPhone G2 proof remains separate.

## 2026-10-16 — unsaved MP4 protection and accessible mobile transitions

The v0.7 Draft PR now protects a verified MP4 when the user selects
another source **before initiating any browser download**. A localized
native confirmation dialog asks whether to discard it. Cancelling
retains the same source, output Blob URL and editable filename; approving
discards the old output, revokes resources and opens the new source.
An accidentally rejected multi-file drop also leaves an undownloaded
MP4 intact. This is not evidence that a previous download was actually
saved by the operating system.

On phone-sized screens, automatic Video→Edit and Edit→Result transitions,
manual back-to-edit actions, and failed source recovery focus the visible
workflow heading instead of an element hidden by the new step.
Manually selecting one of the navigation buttons keeps that button
focused. Cancelling conversion restores focus to an available action.
The workflow still retains no user video across reloads.

Real ST/isolated MT H.264/AAC and mobile browser regression tests cover
the confirmation cancel/approve paths, multi-drop, verified MP4 retention
or invalidation and focus movement. [App CI #38843512812](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38843512812)
**ALL SUCCESS** (build, Node and genuine ST/MT Chrome); the associated
[PR preview #38843512820](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38843512820)
also succeeded.
No FFmpeg/WASM encoding, source-provider memory fallback, CSP, or
high-resolution experimental caps were changed. Android physical QA
and G2 remain separate, unfinished acceptance work.

## 2026-10-16 — owner-directed v0.7.0 development start (G2 stays open)

The user requested moving into v0.7.0 development while G2 remains
unaccepted. The existing three-step mobile flow and its refinements
are now the active v0.7 work. This is **not a G2 pass or a stable
release**. The Android success was on the separately pinned v0.6.0
Pages test snapshot, not the newer Draft v0.7.0 code.

The Android full HD/repeat and source-provider/keyboard matrix, real
audio quality and memory issues remain pending, as documented in
`docs/feasibility/G2.md`. iPhone is deferred. No main/app/Builder
merges, tag, release or Browser Kitty integration have occurred.

## 2026-10-16 — physical Android mobile workflow: OWNER-REPORTED PASS

- The owner merged [test-only GitHub Pages PR #5](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/5).
  [Published-site deployment/verification #38834461219](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38834461219)
  **SUCCESS** for prepare, deploy and live isolated MT Chrome video export.
- After being asked to check the Android **Video → Edit → Result → MP4
  download** journey on the published [MT test page](https://ttomohisa.github.io/htmlapps-reverse-clip/mt/),
  the owner reported **"androidもOK"**. Record this as a **user-reported
  basic physical Android UX PASS** for the publicly deployed, SHA-pinned
  candidate derived from app commit `e5f66428c501090513b6fa0da925b1d1bffbbfb8`.
  The message did not give device/browser details or measurements.
- The owner did not separately report a tested source provider, output
  resolution, repeated high-resolution run count, timing, memory, audio
  mode/seam listening, cancelled jobs, or the OS download destination.
  Those remain unaccepted. Do not infer general G2 or G3 acceptance.
- The app Draft branch's later Oct 16 enhancements (pausing playback
  after leaving Result, invalidation on numeric `input`, extra 44px
  targets) **were not in that pinned Pages test snapshot**. They passed
  their own automated Chrome ST/MT regressions, not this Android run.
- Draft app PR #1/#2 and Builder PR #16 remain unmerged. G2 is
  still OPEN, and v0.7.0 is now a development milestone only,
  not final UI/G2 acceptance. iPhone is deferred.

## 2026-10-16 regression and tap-target hardening

[App CI #38830240345](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38830240345)
**all jobs SUCCESS** after two narrowly scoped mobile fixes: changing
Video/Edit/Result away from Result now pauses even an AAC-capable output
video without discarding the verified MP4; editing a numeric trim field
invalidates previous output immediately on `input` (not just blur).
A first CI attempt failed solely because the new invalidation test erased
the Android-transport diagnostic state before its existing assertion;
the test order was corrected, and the full corrected ST/MT real-Chrome
suite passed. No WASM binaries, codecs, frame plans, output quality,
version or release status changed.

Mobile action buttons (file choice/capture, conversion/cancel, save,
diagnostics) now use at least **44px** height at <=600px. The
320/360/390px regression explicitly measures the source pickers and
conversion control in addition to the three navigation buttons. This
styling refinement passed [App CI #38830712274](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38830712274)
(all jobs SUCCESS: Windows build, Node assertions, actual ST and isolated
MT Chrome MP4/AAC, low-FPS/VFR, offline and mobile layout regressions).
The opt-in HD MT endurance job was not run as part of normal CI.

[Pages-only test PR #5](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/5)
has now **merged and deployed successfully**. It deliberately pins the
earlier validated snapshot; this development-branch follow-up is
**not included in the public Pages bytes** and is not covered by
the owner's Android report. G2 is still OPEN.

## 2026-10-15 automated UX acceptance — Chrome/browser PASS

[App CI #38688780206](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38688780206)
**SUCCESS**: Windows PowerShell build, Node UI/state tests and
real ST/isolated MT H.264 MP4/AAC/browser regressions all passed.
This includes Android-UA file transport (simulated, not a real phone),
long Japanese filenames, widths 320/360/390px without horizontal
scrolling, accessible navigation buttons, returning to Edit, stale
results disabled, repeated 10-second output, full MP4 decode,
client-only data paths and language switching. A separately run
local headless Chrome test generated/saved an actual H.264 MP4,
opened the native diagnostic disclosure on demand, verified it is
initially collapsed, and checked the resulting metadata and
download hint.

A subsequent UI refinement now keeps normal users focused on the
Video/Edit/Result steps. The previous **Browser checks** and
**Development status** sections are **not removed**: each has a
native `<details>` disclosure, collapsed by default, with a 48px+
tap summary and full JA/EN labels. A conversion failure exposes a
direct **Download diagnostic report** path that expands/focuses the
diagnostic section. Browser download status says download started,
not OS save completed. Internal result/diagnostic data still remain
in memory and are not uploaded.

The basic Android mobile flow has owner-reported PASS on the earlier
pinned Pages version. Device-specific keyboard/safe-area, real audio
listening, provider fallback and all outstanding G2 items remain
**PENDING**. iPhone testing is postponed. The app Draft version
is now **v0.7.0 development**, not a release or G2 approval.

The separate [Pages test-only PR #5](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/5)
has now merged; live isolated MT Chrome checks passed in
[deploy #38834461219](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38834461219), and the owner subsequently
reported the Android basic workflow works. App Draft PR #2
remains unmerged.

## What is implemented

On narrow screens (CSS width **<=600px**) the app offers three native
button steps: **Video → Edit → Result**. All video processing, MP4
file bytes, thumbnails and input ownership continue to use the current
v0.6 state machine: the navigator is a presentation layer and **does
not copy or persist media**, silently change output quality or use
external network resources.

1. **Video:** choose an MP4/MOV or open the browser/device capture
   picker; report empty/loading/cancel/error/ready. A selected source
   is summarized safely as text with filename and duration and offers
   a visible **Edit selected section** action.
2. **Edit:** source playback and 0.1s trim handles; numeric range;
   Reverse/Ping-pong, quality and optional source-audio settings;
   browser-validity notice, conversion and cancel action. The source
   step remains available to replace a file.
3. **Result:** enabled only after the exact job generated a verified
   MP4 Blob and the browser loaded its metadata and duration. Show
   resulting video, true output width/height and FPS, duration/size,
   editable filename and explicit MP4 download. A **Back to Edit**
   action pauses output playback (also when the MP4 has AAC) and changes
   the view without discarding the verified Blob. Returning to Result
   requires no re-encode. Changing a setting/source or cancelling a
   later job invalidates old MP4/result state.

Desktop (>600px) keeps the existing continuous page. On mobile the
three-step navigator uses a sticky region just below the existing
sticky header with **44px+** tap targets and **no persistent bottom
bar**. Navigation is *not* an ARIA tablist: native buttons have
`aria-current="step"`, `disabled` for inaccessible steps, a
descriptive nav label and a small live step announcement. All
labels have JA/EN translations. No state persists across page reloads.

**Save truthfulness:** a click starts a browser `<a download>`
request; the app cannot guarantee final OS download completion or
photo-library location. The UI now says **download started** and
suggests checking browser downloads, not **saved successfully**.
The result MP4 remains available to retry download while unchanged.

## Browser and device acceptance

| Case | Expected behavior | Status |
| --- | --- | --- |
| Fresh source, no MP4 | Video current; Edit/Result disabled; empty state shows picker | Automated Chrome PASS; physical Android pending |
| Source metadata ready | Edit automatically selected, source playable, settings enabled | Automated Chrome PASS; physical Android pending |
| Source replaced/cancelled/unreadable | Video current, old Result disabled; stale async loads cannot resurface | Automated ST/MT Chrome PASS; provider-specific Android pending |
| Valid 0.5–10s MP4 | Result current only after fully validated output; Save downloads actual H.264 | Actual ST/MT Chrome MP4 PASS |
| Back to Edit without changes | Output playback pauses while hidden; existing MP4 retained, navigating to Result works without re-encoding | Actual ST/MT Chrome PASS #38830240345 |
| Conversion in progress on mobile | Video step unavailable, progress and Cancel stay accessible in Edit; Cancel/finish re-enables navigation | Actual ST/MT Chrome PASS #38845668240 |
| Focused heading after automatic step change | Heading remains below sticky header without an inherited smooth-scroll race, including 320×568 viewport | Actual ST/MT Chrome PASS #38845668240 |
| Typing trim start/end before blur | Old MP4 and Save cleared immediately on input, even before change/blur | Actual ST/MT Chrome PASS #38830240345 |
| Mobile actions at 320/360/390px | Picker, capture, navigation and conversion tap areas at least 44px tall | Actual Chrome PASS #38830712274 |
| Edit trim/quality/mode/audio after output | Old MP4 and Save cleared, Result disabled | Browser PASS |
| Abort/error or failed frame count | Stays on Edit and shows error details, never an incomplete MP4 | ST/MT regression PASS; independent Android still pending |
| Result metadata | Actual MP4 dimensions, FPS, duration, output size; filename editable | Browser PASS |
| 320/360/390px and long JA filename | No horizontal scrolling, controls 44px+, sticky steps visible without bottom overlays | Automated PASS; physical phone pending |
| JA/EN toggling | Current phase and selected output preserved, navigation/metadata translated | Browser PASS |
| ST and true COI MT | Both generate/download real MP4; source file never uploaded | Browser/CI PASS; phone pending |
| Foldable diagnostics (initially closed) | Native disclosure retains tests/log export; error button opens diagnostics | Browser and Node PASS; Android pending |
| Published Pages MT Android basic Video/Edit/Result/Download flow | User can complete the basic journey on a real Android device | **OWNER-REPORTED PASS 2026-10-16**; exact device/browser, keyboard/safe area and final save destination not separately documented |
| Physical Android keyboard, Photos/cloud picker, OS save location | Source and Save workflows remain accessible, safe-area behavior correct | **Pending detailed real-device checks** |
| Real high-resolution repeated exports/audio/whole-copy | All G2 performance/privacy/cancel/audio conditions satisfied | **Pending G2**, independent of UX |

The automated tests run in `tests/feasibility/v030-ui.test.mjs` and
`tests/feasibility/browser-video-smoke.py` on ST + isolated MT using
actual H.264 output. They do not claim a physical Android acceptance.
The updated mobile-navigation Pages candidate passed live isolated MT
Chrome in [deploy #38834461219](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38834461219) and has an
owner-reported basic Android UX success. It is the pinned Oct 15
snapshot, **not** the later Oct 16 Draft PR #2 refinements.

## G2 and release constraints

A user confirmed the formerly failing 1.03fps H.264 video now
works on PC and Android with Builder 1.10.6, but this does not close
the broader 720p10s/1080p5s mode matrix, real camera provider
memory/copy exception, audio listening, cancel/retry, or final GPL
source-complete permanent Builder Release. iPhone remains deferred.
Do not mark v0.6.0/G2 accepted or call v0.7.0 released. The owner
explicitly authorized **v0.7 development** despite open G2; formal
acceptance and stable release are separate decisions.

App branch: `feat/reverse-wasm-preview`, [Draft PR #2](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/2)
(base `feat/reverse-clip-feasibility-v0.1`).
Builder branch: `feat/video-reverse-poc`, [Draft PR #16](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/pull/16).
No merge, tag, Release or Browser Kitty portal change is implied.
