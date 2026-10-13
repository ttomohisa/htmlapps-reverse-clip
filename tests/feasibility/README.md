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
process tree aggregate RSS sampled every 250ms**, and on supported Linux
systems **proportional/unique set size (PSS/USS) sampled about every second**
with optional `psutil`, plus Chromium JS heap after each job. RSS can
heavily double-count shared pages across MT browser processes; PSS apportions
shared pages but still is not a per-tab peak.
they are **not accurate per-tab peak RAM, WASM peak memory, or a physical
Android/iPhone memory measurement**. The fixture is synthetic H.264,
not representative camera VFR/HEVC/HDR footage. Results from this script
must be explicitly copied into `docs/feasibility/G2.md` and distinguished
from physical-phone acceptance.

### v0.6 full-resolution frame identity checks and measured desktop evidence

The opt-in harness now decodes every generated output at 96×54 grayscale,
compares its source-frame identity against both adjacent input frames,
and rejects duplicated/shifted/reordered output even if the total H.264
frame count and MP4 duration happen to match. This checks both Reverse and
Ping-pong's return and segment boundaries. It also compares AAC stream
duration with the expected video duration if the stream reports it.

When `--cancel-retry` is selected, it clicks Create twice, waits until
**actual segment processing has reported progress**, cancels, verifies
that there is no stale downloadable MP4, and demands a new real decoded
MP4 after retry. This is an opt-in, CPU/RAM-intensive suite and remains
excluded from default PR Actions.

One separately measured Linux desktop ST run set with **11/11 PASS**
(including 720p10s, 1080p5s, three repeated silent Ping-pong exports
per quality and high-resolution AAC) is documented with all limitations
in [`docs/feasibility/V060_DESKTOP_ST_MEASUREMENTS.md`](../../docs/feasibility/V060_DESKTOP_ST_MEASUREMENTS.md).
A Playwright/Chromium test is not a physical-phone memory or audio
quality acceptance test; the local execution container had restricted
file/http navigation, so the measurement used an in-memory HTML document.

### Running the expensive isolated MT proof on demand

The full-size MT proof successfully ran on [CI #38464029860](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38464029860)
(one 720p10s AAC Ping-pong and one 1080p5s silent Reverse), with
numerical results and limitations in
[`V060_DESKTOP_MT_MEASUREMENTS.md`](../../docs/feasibility/V060_DESKTOP_MT_MEASUREMENTS.md).

To avoid unnecessary GitHub Actions costs, subsequent PR pushes do **not**
automatically execute the high-resolution MT job. When the current workflow
revision is available to the GitHub Actions workflow-dispatch UI (the
workflow must exist on the default branch), explicitly launch
`Validate standalone HTML` with **`run_hd_mt: true`** to run it.
The default is `false`. Normal ST/MT real browser regressions continue to
run on PRs. For broader 3-repeat, audio or cancel/retry cases run this
script against a sufficiently provisioned locally hosted, isolated browser,
and record machine/OS/browser, timings and proper memory methodology.
