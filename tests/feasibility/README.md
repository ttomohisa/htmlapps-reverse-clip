# Real embedded-WASM browser regression (optional)

With a local checkout, execute the **Windows template build** first. The resulting `dist/index.html` and `dist/index.self-extract.html` must have the pinned, SHA-256-verified Builder binary embedded.

```powershell
# Python Playwright, Chromium and native FFmpeg + ffprobe are required.
python -m playwright install chromium
python tests/feasibility/browser-video-smoke.py
```

The script creates a locally generated **15-second, 150-frame H.264** source with monotonic frame-color markers. It tests a **0–10-second reverse output (150 frames at 15fps, exact 10.000s)** in both standalone variants, repeated-run file integrity, a non-frame-aligned selection (0.1–9.87s → 146 frames), the original 0–5s path, cancellation/partial output, MP4 download, 390px overflow, console errors and network calls. The second HTML is tested under an *emulated Android user-agent in Linux Chromium*, which is **not a real Android device**. MP4 output is checked through native FFmpeg/ffprobe for frames, duration, codec and descending color order.

Set `CHROMIUM_EXE` to your system's Chromium binary if appropriate. These tests load standalone bytes through `about:blank`/`page.set_content`; they **do not** validate direct `file://` navigation, Android real-device performance, iPhone, HEVC MOV, input-provider permissions, or binary source/license release obligations. The large suite is opt-in to conserve Actions minutes; Node timeline tests still run in CI.

## v0.6.0 opt-in HD load / repeated export test

`v060-stress-browser-smoke.py` is a **desktop-only endurance harness**, deliberately
excluded from default CI to avoid consuming substantial Actions minutes and
crashing shared runners with 1080p loads. It is not an Android/iPhone test,
and it is not evidence of product Gate G2 by itself.

After building both standalone ST and MT variants, and installing Python
Playwright/Chromium plus system `ffmpeg` and `ffprobe`:

```powershell
python -m pip install playwright psutil
python -m playwright install chromium
python tests/feasibility/v060-stress-browser-smoke.py --profile standard --runtime ST --mode both --runs 3 --cancel-retry --report v060-standard-st.json
python tests/feasibility/v060-stress-browser-smoke.py --profile standard --runtime MT --mode both --runs 3 --audio --cancel-retry --report v060-standard-mt-aac.json
python tests/feasibility/v060-stress-browser-smoke.py --profile high --runtime ST --mode reverse --runs 3 --report v060-high-st.json
```

Every run creates a real 1280x720/10s or 1920x1080/5s fixture, generates
and downloads actual H.264 (and optionally AAC) MP4, validates exact frames,
geometry, duration and decodes the output with native FFmpeg. With
`--cancel-retry`, an immediately aborted conversion must be followed by
another real, valid MP4. `--runtime both --profile both` expands coverage,
but may be expensive; run one profile/runtime at a time first.

The JSON records wall-clock duration, approximate **Playwright/Chrome child
process tree aggregate RSS sampled every 250ms** if the optional `psutil`
package is present, and Chromium JS heap after each job. These are useful
desktop trend indicators, but shared pages may be counted multiple times;
they are **not accurate per-tab peak RAM, WASM peak memory, or a physical
Android/iPhone memory measurement**. The fixture is synthetic H.264,
not representative camera VFR/HEVC/HDR footage. Results from this script
must be explicitly copied into `docs/feasibility/G2.md` and distinguished
from physical-phone acceptance.
