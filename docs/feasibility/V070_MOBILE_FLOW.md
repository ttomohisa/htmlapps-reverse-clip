# v0.7.0 Mobile UX / Save Flow — implementation and acceptance

**State (2026-10-15): UI preparation on Reverse Clip v0.6.0 Draft PR #2.
Gate G2 remains OPEN. No v0.7.0 version bump, tag or release has occurred.**
iPhone Safari is explicitly deferred. Windows Chrome/Edge and physical
Android Chrome are the current target devices.

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
   action changes the view only: changing a setting/source or
   cancelling a later job invalidates old MP4/result state.

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
| Fresh source, no MP4 | Video current; Edit/Result disabled; empty state shows picker | Implemented, browser regression pending |
| Source metadata ready | Edit automatically selected, source playable, settings enabled | Implemented, browser regression pending |
| Source replaced/cancelled/unreadable | Video current, old Result disabled; stale async loads cannot resurface | Existing generation guard; browser regression pending |
| Valid 0.5–10s MP4 | Result current only after fully validated output; Save downloads actual H.264 | Existing ST/MT smoke + new mobile checks pending |
| Back to Edit without changes | Existing MP4 retained; navigating to Result works | Implemented, browser regression pending |
| Edit trim/quality/mode/audio after output | Old MP4 and Save cleared, Result disabled | Existing state invalidation; browser regression pending |
| Abort/error or failed frame count | Stays on Edit and shows error details, never an incomplete MP4 | Existing guard; browser regression pending |
| Result metadata | Actual MP4 dimensions, FPS, duration, output size; filename editable | Implemented, browser regression pending |
| 320/360/390px and long JA filename | No horizontal scrolling, controls 44px+, sticky steps visible without bottom overlays | Automated regression pending; physical phone pending |
| JA/EN toggling | Current phase and selected output preserved, navigation/metadata translated | Automated regression pending |
| ST and true COI MT | Both generate/download real MP4; source file never uploaded | Real browser suite pending |
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
