# Reverse Clip v0.6.0 — real isolated MT high-resolution desktop evidence

**Test date:** 2026-10-14 JST (2026-10-13 20:37 UTC)  
**Result:** 2/2 real **multi-thread WASM** full-resolution MP4 exports PASSED.  
**Gate G2: INVESTIGATE / NOT PASSED.** Desktop CI does not establish real Android/iPhone stability or physical-device memory use.

## Exact reproducible run

- Application branch: `feat/reverse-wasm-preview`, commit [`aa7207db5e557a1048bcc225449e6a9f9aefbb09`](https://github.com/ttomohisa/htmlapps-reverse-clip/commit/aa7207db5e557a1048bcc225449e6a9f9aefbb09), Draft [PR #2](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/2).
- Successful GitHub Actions [`Validate standalone HTML #38464029860`](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38464029860), job **One-time isolated MT 720p/1080p video proof**, job ID `115526587618`. Baseline build + real ST/MT regression jobs in the same workflow also passed.
- Input/export checks performed by `tests/feasibility/v060-stress-browser-smoke.py`. Actual completed MP4s were saved, probed with ffprobe, fully decoded by FFmpeg and compared against the input frame sequence **at every position** in a reduced grayscale representation (including chunk/turn boundaries).
- Environment: GitHub-hosted Linux `ubuntu-latest`, Google Chrome from `browser-actions/setup-chrome@v2.2.0`, Python 3.12, Playwright, ffmpeg/ffprobe and psutil.
- Served from a local **HTTP server with explicit COOP: same-origin and COEP: require-corp on `/index.mt.html`**. The browser test verifies `crossOriginIsolated === true` and does **not** silently substitute ST. Neither experiment contacted a nonlocal host during media processing.
- Input fixtures: generated locally from FFmpeg `testsrc2` H.264 15fps yuv420p, either 1280×720 for 10 seconds or 1920×1080 for 5 seconds; 720p audio source has AAC derived from 440Hz sine, 48kHz stereo. These are not real phone videos, and stereo source channels are not independent.

## Actual output measurements — isolated MT

| Input / mode | AAC | Elapsed | MP4 frames | MP4 duration | MP4 bytes | Post-run JS heap | Sum of sampled Chrome-related process RSS |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| **1280×720 / 10s Ping-pong** | Yes | **11.20s** | **298** | **19.866667s** | 2,821,532 | 38,823,680 B | 3,358,507,008 B (~3,203 MiB) |
| **1920×1080 / 5s Reverse** | No | **5.87s** | **75** | **5.000s** | 1,276,718 | 21,791,614 B | 2,984,267,776 B (~2,846 MiB) |

Both exact-frame checks, output video decoding, source frame-identity comparisons, MP4 timing, output geometry and network/console checks passed.

**Crucial memory interpretation:** The reported number is the sum of **resident set sizes (RSS)** across the Python process's entire Playwright/Chrome subprocess tree sampled every 250ms. RSS is **not additive when mappings are shared**: multi-thread Chrome can have many processes referencing the same pages, so it can double-count heavily. It is **not** the process-tree unique physical footprint, JS heap peak, WebAssembly heap, a single-tab measurement, or Android memory. No memory-leak diagnosis or direct speedup percentage over the previous ST test can be inferred from this result: the ST and MT measurements used different machines and browser launch methods. The enhanced opt-in benchmark will additionally record proportional set size (PSS) and unique set size (USS) when available; **this run did not collect PSS/USS**.

## Non-claims and remaining G2 conditions

- This proves *one* 720p10s AAC Ping-pong export and *one* 1080p5s silent Reverse export on a hosted desktop CI runner. It **does not** prove three consecutive MT conversions, 720p silent Reverse, 1080p AAC Ping-pong, stress cancellation/recovery or low memory pressure at these sizes.
- No physical Android ST/MT full-resolution runs or headphone tests were performed. iPhone physical testing is deferred by the owner.
- Camera HEVC/HDR/MOV, VFR, rotation metadata, truly distinct stereo channels, measured audio clicks and reliable provider-backed `File` reads remain separate acceptance items.
- Current Android file-provider workaround copies the entire input into memory when file size is ≤64MiB, contrary to the strict original Gate G2 condition forbidding a whole-file copy for files ≤1GiB. This gate is still OPEN; do not silently reclassify it as compliant.
- The current ST/MT WASM was pinned from temporary Builder Actions artifact `11794061552` (expires **2026-10-20**). An immutable Builder release with suitable complete corresponding GPL sources and notices has not been made.

## How to reproduce later without spending Actions minutes every PR

The existing `.github/workflows/build-standalone.yml` can be manually dispatched with **`run_hd_mt=true`** to opt into this expensive MT workload, once the workflow-dispatch configuration is accessible on the repository's default branch. Normal PR updates **do not execute the full-resolution MT job**. The CLI harness also supports selective profile, ST/MT, audio, three repetitions and cancellation/retry; see `tests/feasibility/README.md`.

**Decision:** Full-resolution MT desktop feasibility for these **two exact scenarios** is established. Gate G2 remains INVESTIGATE pending phone, repetition, objective sound quality and memory measurements, no-copy input handling and permanent GPL distribution. Keep all Draft PRs unmerged and Browser Kitty unchanged.
