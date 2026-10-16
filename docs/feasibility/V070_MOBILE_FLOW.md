# v0.7.0 Mobile UX / Save Flow — implementation and acceptance

**State (2026-10-15): UI preparation on Reverse Clip v0.6.0 Draft PR #2.
Gate G2 remains OPEN. No v0.7.0 version bump, tag or release has occurred.**
iPhone Safari is explicitly deferred. Windows Chrome/Edge and physical
Android Chrome are the current target devices.

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
remains an **earlier pinned snapshot**; this development-branch
follow-up is **not** present in those published-test bytes. It must
not be claimed as Android hardware validated before a deliberately
re-pinned deployment and physical review. G2 is still OPEN.

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

The real-device Android UI/safe-area/keyboard, actual audio listening,
source-provider memory fallback and all outstanding G2 items remain
**PENDING**. iPhone verification is postponed. v0.6.0 stays the
version; this is not v0.7.0 milestone approval.

A separate [Pages test-only PR #5](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/5)
pins the exact green build for Android UX review without merging
this unfinished app development PR. A Pages PR check does not
establish live mobile behavior until the owner merges it and the
`verify-live-mt` deployment job passes.

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
| Typing trim start/end before blur | Old MP4 and Save cleared immediately on input, even before change/blur | Actual ST/MT Chrome PASS #38830240345 |
| Mobile actions at 320/360/390px | Picker, capture, navigation and conversion tap areas at least 44px tall | Actual Chrome PASS #38830712274 |
| Edit trim/quality/mode/audio after output | Old MP4 and Save cleared, Result disabled | Browser PASS |
| Abort/error or failed frame count | Stays on Edit and shows error details, never an incomplete MP4 | ST/MT regression PASS; independent Android still pending |
| Result metadata | Actual MP4 dimensions, FPS, duration, output size; filename editable | Browser PASS |
| 320/360/390px and long JA filename | No horizontal scrolling, controls 44px+, sticky steps visible without bottom overlays | Automated PASS; physical phone pending |
| JA/EN toggling | Current phase and selected output preserved, navigation/metadata translated | Browser PASS |
| ST and true COI MT | Both generate/download real MP4; source file never uploaded | Browser/CI PASS; phone pending |
| Foldable diagnostics (initially closed) | Native disclosure retains tests/log export; error button opens diagnostics | Browser and Node PASS; Android pending |
| Physical Android, keyboard, picker, OS save location | Source and Save workflows remain accessible, safe-area behavior correct | **Pending real device** |
| Real high-resolution repeated exports/audio/whole-copy | All G2 performance/privacy/cancel/audio conditions satisfied | **Pending G2**, independent of UX |

The automated tests run in `tests/feasibility/v030-ui.test.mjs` and
`tests/feasibility/browser-video-smoke.py` on ST + isolated MT using
actual H.264 output. They do not claim a physical Android acceptance.
The last known [live Pages MT #38667384368](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38667384368)
validates the **previous** UI/1.10.6 experimental binaries; the
updated navigation lives **only in unmerged Draft PR #2** until a
deliberate subsequent Pages test update.

## G2 and release constraints

A user confirmed the formerly failing 1.03fps H.264 video now
works on PC and Android with Builder 1.10.6, but this does not close
the broader 720p10s/1080p5s mode matrix, real camera provider
memory/copy exception, audio listening, cancel/retry, or final GPL
source-complete permanent Builder Release. iPhone remains deferred.
Do not mark v0.6.0 complete or call this v0.7.0 released without
separate explicit Gate G2 review.

App branch: `feat/reverse-wasm-preview`, [Draft PR #2](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/2)
(base `feat/reverse-clip-feasibility-v0.1`).
Builder branch: `feat/video-reverse-poc`, [Draft PR #16](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/pull/16).
No merge, tag, Release or Browser Kitty portal change is implied.
