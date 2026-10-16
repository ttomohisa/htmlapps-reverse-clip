# Reverse Clip v0.9.0 — actual screenshot evidence

**Recorded 2026-10-17; CI-built development Draft PR #2, NOT RELEASED.**
[GitHub Actions #38939628625](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38939628625)
**ALL SUCCESS** including real ST/isolated MT H.264/AAC media tests.

Four actual browser images are in artifact
`reverse-clip-v090-real-ui-e8a8ce59664ff25bfc37112e60eac6730d614b04`,
artifact ID **12062302953**, expires **2026-11-15T17:29:47Z**.
Do not mistake this temporary CI artifact for durable README screenshots.

| Generated file | Resolution | SHA-256 |
| --- | --- | --- |
| `reverse-clip-desktop-ja.png` | 1360×900 | `6cfd0fb9fa836d10d76828ce832e26d2a475d414fd83a061587b83006aa1a95f` |
| `reverse-clip-desktop-en.png` | 1360×900 | `5120f7c71dc8be9ed2dba704463d85e3c2d3b149d4c0f678d885e87691d33546` |
| `reverse-clip-mobile-ja.png` | 390×844 | `3324d87cbd4665d3407be1a4eed462ee78e209176115854a5cea582e4f50787c` |
| `reverse-clip-mobile-en.png` | 390×844 | `d5ba342a16b1112b28b67ea291d8d3321c92d01190421308b537c144ed73ad67` |

These screenshots are from real Chrome rendering of the verified
MP4 Result step, generated from a synthetic 30fps H.264 fixture
and reverse-exported to a 15-frame/1s H.264 MP4. There is no
customer video or personal data. The shooting code is
`tests/feasibility/browser-video-smoke.py` with
`RC_CAPTURE_SCREENSHOTS=1`; normal source and output semantics
are unchanged. Manifest SHA-256 values above were transcribed from the downloaded\nverified screenshot archive's manifest. The actual screenshots were inspected locally:
Japanese glyphs rendered correctly, result headings/video were
inside the viewport and saving was available.

**Editorial review (2026-10-17):** This first artifact uses FFmpeg's
color-bar-style `testsrc2` calibration video and is **not suitable as a
README hero screenshot**, even though its H.264 output and UI are genuine.
Do not promote the four PNGs above as final marketing screenshots.
The test harness now generates a separate locally rendered, 2-second
motion sample (384×216, 30fps), reverses it in the actual app, verifies
the saved 30-frame H.264 MP4 with ffprobe, and then captures the four
language/viewport views. That new CI artifact must be downloaded and
reviewed before selecting and committing images under `assets/`.
Real device checks remain separate.
No screenshot is falsely claimed to be from Android hardware.

**Outstanding:** physical Android current v0.9 UX and audible AAC,
original G2 historical gate, permanent source-complete GPL Builder
publication, G3 approval. No release actions have been performed.
