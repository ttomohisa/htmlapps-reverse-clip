# Reverse Clip v1.0.0

Reverse Clip creates reversed and forward-and-back (ping-pong) H.264 MP4s from short sections of your videos. It processes media in the browser, without an account, installation or uploading the original video.

## What's new
- Short MP4 Reverse and Ping-pong export, 15fps H.264, optional reversed AAC (silent by default).
- Mobile Video → Edit → Result flow and Japanese/English interface.
- Local MP4 preview/save, cancel/retry and error protection.
- The v1.0.0 interface removes old developer diagnostic and development-status panels; error details remain.
- Four downloadable single-HTML builds with exact pinned FFmpeg WASM assets.

## Download
| File | Use |
| --- | --- |
| `reverse-clip-v1.0.0.html` | ST standalone HTML; works directly from `file://` |
| `reverse-clip-v1.0.0.self-extract.html` | Compressed ST standalone HTML; works directly from `file://` |
| `reverse-clip-v1.0.0.mt.html` | MT standalone HTML; requires cross-origin isolation from the host |
| `reverse-clip-v1.0.0.mt.self-extract.html` | Compressed MT standalone; same isolation requirement |

The release also includes `LICENSE`, `THIRD_PARTY_NOTICES.md`, `SHA256SUMS.txt` and these release notes. Verify checksums after download where desired.

## Compatibility and limitations
The initial practical scope is short (around 0.5–5s), H.264 MP4 sources in Windows Chrome and Android Chrome. Output is 15fps and does not preserve the input frame rate. Higher resolution and 5–10 second operations may need more memory or processing time; the 1080p-class pilot limits selection to 5 seconds. Multiple audio-track selection is unavailable. HEVC/HDR fidelity and iPhone Safari are not supported claims.

Some Android file providers need a **conditional local memory copy** for files at or below 64 MiB when direct reading fails. Your video is not sent to the server. Web use initially downloads the HTML; ST standalone works without network after download.

The original broader Android+iPhone/HD repeated-stress G2 gate was not met. Existing automation verified ST/MT short MP4 reversing, ping-pong frame order, optional AAC, cancellation, offline ST and hosted isolated MT; the user reported success on Android Chrome ST/MT basic tasks. No blanket compatibility or high-memory performance claim is made.

## Libraries and sources
- The Reverse Clip UI/application source is MIT-licensed.
- The bundled FFmpeg+x264 video-reverse ST/MT runtime is **GPL-2.0-or-later**, [Builder video-reverse-v1.10.6](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/tag/video-reverse-v1.10.6). The [matching source archive](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/download/video-reverse-v1.10.6/ffmpeg-wasm-sources-v1.10.6.tar.gz) and [GPL addendum](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/download/video-reverse-v1.10.6/VIDEO_REVERSE_LICENSE_ADDENDUM.md) are publicly available. MIT does not relicense GPL runtime code.
- GitHub Pages MT uses pinned `coi-serviceworker` MIT v0.1.7; the ST/MT standalone HTML does not embed the Pages helper.

**Browser Kitty integration is a separate task and is not included in this release.**
