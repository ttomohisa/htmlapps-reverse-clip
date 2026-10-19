# Reverse Clip / 動画逆再生

[![GitHub Pages](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/workflows/deploy-pages.yml/badge.svg)](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/workflows/deploy-pages.yml)
[![Single HTML](https://img.shields.io/badge/distribution-single%20HTML-16624f)](https://ttomohisa.github.io/htmlapps-reverse-clip/)
[![App: MIT](https://img.shields.io/badge/app%20license-MIT-blue)](LICENSE)
[![FFmpeg: GPL](https://img.shields.io/badge/FFmpeg%20WASM-GPL--2.0--or--later-blue)](THIRD_PARTY_NOTICES.md)

[日本語版 README](README.ja.md)

Reverse a short video, or make it play forward and then backward (ping-pong), and save the result as an MP4. Everything runs in your browser without uploading the selected video. No account or installation is needed.

## Live demo

### [Open Reverse Clip on GitHub Pages](https://ttomohisa.github.io/htmlapps-reverse-clip/)

The root page runs the **single-thread (ST)** version. An [isolated multi-thread (MT) page](https://ttomohisa.github.io/htmlapps-reverse-clip/mt/) is also available for supported browsers. The web page is downloaded normally, but the video you select is processed on your device.

[![Reverse Clip showing a generated MP4 in desktop Chrome](assets/screenshot-en.png)](https://ttomohisa.github.io/htmlapps-reverse-clip/)

Desktop Chrome screenshot of an actual locally generated and verified MP4. This screenshot is **not physical Android device certification**. The app is currently an unreleased v0.9.0 release candidate.

## Features

- **Reverse a selected section** — Choose the start and end points and create a backward-playing H.264 MP4.
- **Create a ping-pong clip** — Play the section forward and then backward in one MP4, excluding repeated frames at the turning point.
- **Include reverse audio when supported** — Silent output is the default; supported source tracks can use reversed AAC audio.
- **Preview before saving** — Review the generated video, edit the output filename and download the MP4.
- **Work on phones and PCs** — Japanese/English UI, a mobile Video → Edit → Result flow, and controls for cancellation and retry.
- **Keep source files local** — The FFmpeg WebAssembly runtime and supporting files are embedded in the standalone HTML, without runtime CDN or media upload requests.

## Quick start

### Use it on the web

Open the [GitHub Pages demo](https://ttomohisa.github.io/htmlapps-reverse-clip/) in a compatible browser, then select a video. No sign-in or installation is required.

### Use a standalone HTML file offline

The readable **ST** build works directly via `file://` after it has been generated. The repository does not currently publish a versioned Reverse Clip app download; v1.0.0 is still being prepared.

1. Download or clone this repository on Windows.
2. Run `build-standalone.bat` to generate the self-contained HTML files.
3. Copy `dist/index.html` or `dist/index.self-extract.html` to the desired location.
4. Open the file in Chrome without an internet connection.

The initial build needs an internet connection to fetch the fixed-version dependencies, including the [public video-reverse FFmpeg WASM Release](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/tag/video-reverse-v1.10.6). The generated ST HTML runs without downloading these dependencies again. The **MT** build needs cross-origin isolation and is not intended for direct `file://` use.

## How to use

1. **Video:** Choose a short H.264 MP4 from your device and check the source preview.
2. **Edit:** Set the start and end points with the timeline or time fields.
3. Select **Reverse** or **Ping-pong**.
4. Choose the output size. **360px or 720px long edge** is the practical initial scope; higher-resolution options are experimental.
5. Leave **No audio** selected, or choose reverse audio if the video's audio track is recognized and that option is available.
6. Create the MP4. Wait for the result; use Cancel if you need to stop.
7. **Result:** Preview the output, choose a filename and select **Save MP4**.

Choosing another source while an unsaved result is present asks for confirmation. Failed or incomplete results are not offered as valid MP4 downloads. Download initiation does not by itself guarantee that the browser or operating system finished saving the file.

### Screenshots

| Desktop (English) | Mobile-size viewport (English) |
| --- | --- |
| ![Reverse Clip desktop result](assets/screenshot-en.png) | ![Reverse Clip mobile result](assets/screenshot-mobile-en.png) |

[Japanese desktop](assets/screenshot.png) · [Japanese mobile viewport](assets/screenshot-mobile.png) · [Screenshot verification record](docs/release/RC_SCREENSHOT_ASSET_MANIFEST.json)

These images were captured in desktop Chrome at desktop/mobile viewport sizes after a real local MP4 conversion; they do not demonstrate a physical phone test.

## GitHub Pages deployment

A push to `main` triggers [the Pages workflow](.github/workflows/deploy-pages.yml), which builds the pinned assets and deploys the generated pages.

- `/` serves the single-thread standalone app.
- `/mt/` serves the multi-thread build with a locally hosted, pinned cross-origin-isolation Service Worker.

On other hosting services, MT requires equivalent isolation support. Do not serve the MT file without the necessary browser security environment.

## Development and build

```text
.
├─ src/index.template.html             # Editable app source (JA/EN)
├─ app.config.json                     # App version and output paths
├─ reverse-runtime.lock.json           # ST/MT WASM and corresponding-source hashes
├─ build-standalone.bat / .ps1          # Windows single-HTML builder
├─ scripts/prepare-pages.ps1           # ST/MT GitHub Pages layout
├─ dist/index.html                     # Generated readable ST HTML
├─ dist/index.self-extract.html        # Generated compressed ST HTML
├─ dist/index.mt.html                  # Generated MT HTML
└─ .github/workflows/                   # Validation and deployment
```

The default build also generates the standalone MT self-extract version and `reverse-clip.html` as a copy of the readable ST output. Generated HTML files are build products; edit the source template instead.

To build and validate from PowerShell:

```powershell
./scripts/check-repository.ps1
```

The build pins its FFmpeg WebAssembly files by SHA-256 and embeds them in the output HTML. See [APP_SPEC.md](APP_SPEC.md), [DEVELOPMENT_PLAN.md](DEVELOPMENT_PLAN.md), [CONTRIBUTING.md](CONTRIBUTING.md) and [v1.0.0 readiness](docs/release/V100_RELEASE_READINESS.md) for architecture, tests and release work.

## Privacy and offline behavior

- Your selected video is not uploaded by the app. Decoding, reversal, preview and export run in the browser.
- The generated HTML uses a restrictive Content Security Policy including `connect-src 'none'`; the runtime has no remote FFmpeg/CDN requirement.
- The GitHub Pages version makes normal requests to load the page. Its MT path also loads a same-origin isolation helper; this does not upload the video.
- Some Android file providers cannot be read directly by the Worker. For source files **up to 64 MiB**, the app may conditionally make a temporary copy **in device memory** to retry. This is not a server upload.

## Limitations and compatibility

- **H.264 MP4** is the main verified input. Windows Chrome and Android Chrome are the intended initial platforms. Desktop Chrome tests also cover selected H.264 MOV, frame-rate and rotation cases, but that does not guarantee every camera file works.
- Output is **H.264 MP4 at 15 fps**. Source frame rate is not preserved, and selection boundaries can be adjusted slightly to frame boundaries.
- The ordinary recommended range is about **0.5–5 seconds**. Up to 10 seconds is experimental; the 1080p-class option is limited to 5 seconds. Processing time and memory use vary by device.
- **Silent output is the default.** Optional reversed audio is available only when the source audio can be read and processed; multiple audio-track selection is not supported.
- HEVC/H.265, HDR/10-bit color fidelity and iPhone Safari are **not guaranteed or claimed supported**.
- MT requires a browser with SharedArrayBuffer and proper cross-origin isolation; the offline `file://` version uses ST.
- Saving is initiated through the browser. Check your Downloads location if the output does not appear.

## Dependencies and licenses

| Component | Version / source | License | Purpose |
| --- | --- | --- | --- |
| Reverse Clip application | This repository | [MIT](LICENSE) | UI and browser-side workflow |
| FFmpeg + x264 WASM (ST/MT) | [Builder video-reverse-v1.10.6](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/tag/video-reverse-v1.10.6) | GPL-2.0-or-later | Video/audio processing |
| coi-serviceworker (Pages MT only) | 0.1.7, [pinned commit](coi-serviceworker.lock.json) | MIT | GitHub Pages isolation fallback |

The matching [FFmpeg/x264/Emscripten corresponding source](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/download/video-reverse-v1.10.6/ffmpeg-wasm-sources-v1.10.6.tar.gz) and [GPL notice addendum](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/download/video-reverse-v1.10.6/VIDEO_REVERSE_LICENSE_ADDENDUM.md) are publicly available. The MIT license for the application does **not** relicense the bundled GPL runtime. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

## Project status and contributing

**v0.9.0 RC PREPARATION:** The app code is integrated into `main`, but Reverse Clip itself has **not** had a v1.0.0 GitHub Release. The public FFmpeg WASM dependency is a separate Release. The historic G2 criteria remain unmet and the app's final G3 release decision is pending. [Current release plan](docs/release/V100_RELEASE_READINESS.md) · [Acceptance evidence](docs/release/RC_CHECKLIST.md).

Issues and pull requests are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidance. Reverse Clip will be added to Browser Kitty **after** its v1.0.0 release.
