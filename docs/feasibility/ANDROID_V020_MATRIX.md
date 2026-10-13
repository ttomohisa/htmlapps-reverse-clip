# Reverse Clip v0.2.0 — Android physical-device acceptance matrix

**Status: PENDING REAL-DEVICE VALIDATION.** v0.2.0 App Foundation exists in [Draft PR #2](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/2). Neither passing a Linux Chrome emulator nor using an Android user-agent counts as physical Android proof.

Use the current PR preview's **ST page** and **MT page** (configured with cross-origin isolation). These are temporary PR previews; do not confuse them with unmerged public GitHub Pages. The Builder's current assets are a temporary Actions artifact. Do not merge PRs or import into Browser Kitty solely because this matrix exists.

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

Existing older-user-reported ST results: 1s and 5s reverse succeeded, including 5s at **long-edge720px / 12.7s**. These reports do **not** validate the new v0.2 build, MT performance, full 1280×720 5s, 720p 10s, 1080p, iPhone Safari or audio.

## Record of an actual run (fill after testing)

| Timestamp (JST) | Device / Android / Chrome | Source format and WxH | ST or MT / duration / quality | Conversion seconds | Saved result / memory behavior | Evidence |
|---|---|---|---|---|---|---|
| — | — | — | — | — | PENDING | — |

**Release policy:** keep this matrix honest; do not mark `PASS` based on synthetic browser tests. iPhone physical testing is deferred by the owner, and Browser Kitty integration remains explicitly postponed until the app is complete.
