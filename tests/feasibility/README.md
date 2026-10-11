# Manual real-WASM browser regression

Run **after building** the standalone HTML in a trusted checkout.

```powershell
# Requires Python with playwright, FFmpeg + ffprobe, and a Chromium browser.
python -m playwright install chromium
python tests/feasibility/browser-video-smoke.py
```

The optional script generates a 5-second 10fps H.264 test video containing
50 color-coded frames; it does not download example media. For **both**
`dist/index.html` and `dist/index.self-extract.html`, Chromium converts
the 5-second clip to a silent 15fps MP4, saves it through the app, and native
FFmpeg re-decodes it to verify exactly **75 reversed frames**, correct duration,
no horizontal overflow and no observed external HTTP(S) requests. The app's
`tests/feasibility/reverse-chunk-plan.test.mjs` separately validates planner
boundaries and ensures Android picker helpers remain present.

Set `CHROMIUM_EXE` if you use an installed Chromium rather than Playwright's
browser. This script exercises local HTML through `page.set_content` in the
headless browser's `about:blank` document; **it does not test direct `file://`**.
It also is not a substitute for actual Android Chrome and iPhone Safari
recordings, HEVC MOV, memory measurements, or video/audio synchronization.
Large mandatory GitHub Actions jobs are intentionally avoided in the PoC stage.
