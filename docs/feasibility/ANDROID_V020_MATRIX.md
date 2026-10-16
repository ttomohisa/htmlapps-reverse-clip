# Reverse Clip v0.2.0 — Android physical-device acceptance matrix

**Status (2026-10-16): historical v0.2 matrix mostly unaccepted; targeted v0.6 low-FPS and v0.7-preparation basic workflow were USER-REPORTED PASS on real Android.** v0.2.0 App Foundation exists in [Draft PR #2](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/2). Neither passing a Linux Chrome emulator nor using an Android user-agent counts as physical Android proof.

Use the current PR preview's **ST page** and **MT page** (configured with cross-origin isolation). These are temporary PR previews; do not confuse them with unmerged public GitHub Pages. The Builder's current assets are a temporary Actions artifact. Do not merge PRs or import into Browser Kitty solely because this matrix exists.

## 2026-10-16 Android workflow — user-reported basic UX PASS

Following the owner merge of [Pages PR #5](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/5),
[public deployment #38834461219](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38834461219) passed live
isolated MT Chrome MP4 tests. When asked to exercise the Android
Video → Edit → Result → MP4 download journey, the owner confirmed
**"androidもOK"**. This is **physical-device user-reported basic
workflow PASS** for the pinned Pages candidate, not a formal pass
for every historical v0.2 case A20-01…A20-12 or the G2 memory,
source-provider, high-resolution, cancellation and audio matrix.
Device/browser version, selected footage, output profile, repeat
count, RAM and file provider were not independently recorded.

The follow-up Oct 16 Draft app UI changes are absent from the
Pages-pinned snapshot. Android iPhone/HEVC claims remain unverified;
iPhone hardware acceptance is deferred.

## 2026-10-15 real Android result — specific v0.6 regression only

Following the merged [experimental Pages PR #4](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/4)
and [deployed isolated MT Chrome test #38667384368](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38667384368),
the owner reported that the same original H.264 High,
1920×1080, 37.806089s, ~1.03fps presentation MP4 that previously
failed on MT now **succeeds on PC and Android**. Record this as
**USER-REPORTED PASS for that video and bug**, not as a blanket pass
for the earlier A20-01 through A20-12 input-state tests, Photos/file
providers, large files, or the broader Gate G2 720p/1080p/audio
matrix. Device/Android/browser versions, separate repetition timings
and transport diagnostics were not supplied. The original
64MiB provider fallback still makes a full memory copy.
iPhone tests remain deferred.

## Test procedure

Record physical device model, Android version, browser name/version, source codec/container, width/height/fps/file bytes, route (ST/MT), selection, output geometry, runtime seconds, observed result, memory/tab reload behavior, and the diagnostic JSON SHA-256 or issue reference. Avoid uploading personal recordings publicly.

| ID | Android real-device test | Expected | Status |
|---|---|---|---|
| A20-01 | Select a local Android camera H.264 MP4 | `ready`, original video plays, duration/width/height and file size shown | PENDING |
| A20-02 | Choose the same MP4 again, then choose a different MP4 | Old result/save UI cleared; new source alone is `ready`; no stale frame | PENDING |
| A20-03 | Change the source while conversion initializes or runs | Previous MP4 cannot be downloaded; subsequent short conversion works | PENDING |
| A20-04 | Select a renamed text/WEBM `.mp4` from Android file manager | Recognizable JA/EN error; no preview, conversion or save | PENDING |
| A20-05 | Select a 0-byte `.mp4` or damaged `.mov` | Invalid input/error state; can choose another valid video | PENDING |
| A20-06 | Pick an MP4 from Photos and from Android Files / cloud-backed provider | Under-64MiB staged Blob works or localized actionable error; no upload | PENDING |
| A20-07 | Reload the page after error; switch JA/EN during error and after valid import | Error remains understandable; old media state not resurrected | PENDING |
| A20-08 | Full output path, ST: 1–5s long-edge360/720px | Silent reversed MP4 plays and saves, no repeated boundary frames | PENDING new v0.2 build |
| A20-09 | Repeat A20-08 on a cross-origin-isolated MT Preview, three times | All outputs play/save, no unexpectedly reloaded tabs or unstable memory | PENDING |
| A20-10 | Stress with a large original file (up to 1GiB; short trim only) | No full-file copy, no tab crash; clear error when provider access fails | PENDING |
| A20-11 | Start a slow Photos/cloud video selection and select "読み込みを中止" | Cancel button hides; old content never returns; new source can be selected | PENDING |
| A20-12 | Drop multiple videos on the app (supported desktop/Android setups) | Reject all with a clear one-file-only message, no stale MP4 output | PENDING / platform dependent |

Existing older-user-reported ST results: 1s and 5s reverse succeeded, including 5s at **long-edge720px / 12.7s**. These reports do **not** validate the new v0.2 build, MT performance, full 1280×720 5s, 720p 10s, 1080p, iPhone Safari or audio.

## Record of an actual run (fill after testing)

| Timestamp (JST) | Device / Android / Chrome | Source format and WxH | ST or MT / duration / quality | Conversion seconds | Saved result / memory behavior | Evidence |
|---|---|---|---|---|---|---|
| — | — | — | — | — | PENDING | — |

**Release policy:** keep this matrix honest; do not mark `PASS` based on synthetic browser tests. iPhone physical testing is deferred by the owner, and Browser Kitty integration remains explicitly postponed until the app is complete.

## 2026-10-14 — v0.6 mobile Worker input-probe acceptance (all phone results PENDING)

**Desktop automation verified:** [App CI #38493664787](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38493664787)
PASS for synthetic Android user agent original WorkerFS (150 frames,
10.000s MP4) and simulated provider rejection + MEMFS fallback
(15 frames, 1.000s MP4), with downloaded transport diagnostics,
no error/remote requests. Actual device and cloud-provider behavior
remain PENDING.

The Android <=64MiB eager whole-file memory copy has been replaced
by a bounded preliminary **head/tail 32-byte FileReaderSync Worker**
probe. Its success selects original File/WORKERFS without eager
copy; failure retains the old <=64MiB MEMFS fallback. This may reduce
allocations on normal local files, but **does not prove** compatibility
with photo-picker providers which revoke file access after preview.
The strict no-full-source-copy G2 condition is still OPEN.

Physical Android cases still required (ST and isolated MT separately):
- Choose a normal locally saved camera MP4 <=64MiB, record diagnostics
  `source.transport=workerfs`, preview, and real 5s Reverse/Ping-pong export.
- Choose an MP4 from Google Photos/Files/cloud provider <=64MiB;
  verify metadata, preview, real conversion, transport from diagnostic
  `memory` or `memory-fallback`, and usable error/recovery if unavailable.
- For files >64MiB to 1GiB, verify no full `file.arrayBuffer()` copy and
  readable WORKERFS; fail visibly rather than cloning large media.
- Cancel while probe/provider read is pending, switch sources, retry,
  background/resume tab and confirm no old file appears.
- Repeat high-resolution 720p10s / 1080p5s with audio and log time,
  crash/tab restart, OS/browser/device, and actual RAM source.

Desktop Chrome with a simulated Android UA is a regression test only,
not actual Android picker/file-provider acceptance.
