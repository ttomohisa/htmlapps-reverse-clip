# Real embedded-WASM browser regression (optional)

With a local checkout, execute the **Windows template build** first. The resulting `dist/index.html` and `dist/index.self-extract.html` must have the pinned, SHA-256-verified Builder binary embedded.

```powershell
# Python Playwright, Chromium and native FFmpeg + ffprobe are required.
python -m playwright install chromium
python tests/feasibility/browser-video-smoke.py
```

The script creates a locally generated **15-second, 150-frame H.264** source with monotonic frame-color markers. It tests a **0–10-second reverse output (150 frames at 15fps, exact 10.000s)** in both standalone variants, repeated-run file integrity, a non-frame-aligned selection (0.1–9.87s → 146 frames), the original 0–5s path, cancellation/partial output, MP4 download, 390px overflow, console errors and network calls. The second HTML is tested under an *emulated Android user-agent in Linux Chromium*, which is **not a real Android device**. MP4 output is checked through native FFmpeg/ffprobe for frames, duration, codec and descending color order.

Set `CHROMIUM_EXE` to your system's Chromium binary if appropriate. These tests load standalone bytes through `about:blank`/`page.set_content`; they **do not** validate direct `file://` navigation, Android real-device performance, iPhone, HEVC MOV, input-provider permissions, or binary source/license release obligations. The large suite is opt-in to conserve Actions minutes; Node timeline tests still run in CI.
