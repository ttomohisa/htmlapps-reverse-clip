# Reverse Clip v0.8.0 — Compatibility & Hardening Acceptance Matrix

**State (2026-10-16): OPEN / IN PROGRESS.** This is a development and QA log, **not** a stable format-support promise. Target build is v0.8.0 on [app Draft PR #2](https://github.com/ttomohisa/htmlapps-reverse-clip/pull/2). The original Android user report concerns a pinned older v0.6.0 Pages snapshot. iPhone hardware is deferred by owner direction. G2 remains INVESTIGATE / NOT PASSED.

## Case-by-case verification

| Case | Expected | Evidence / current status |
| --- | --- | --- |
| H.264 MP4, baseline ST/MT | Real output reverses correctly, H.264 MP4 saved and decoded | **PASS on desktop Chrome** in prior v0.7.0 CI #38850394911 |
| H.264 input at 30fps | Output explicitly 15fps, 1s = 15 frames | **PASS real ST/isolated MT Chrome #38853679777**: generated 30fps H.264, saved & probed 15-frame/1s H.264 MP4 |
| H.264 input at 60fps | Output explicitly 15fps, 1s = 15 frames | **PASS real ST/isolated MT Chrome #38853679777**: generated 60fps H.264, saved & probed 15-frame/1s H.264 MP4 |
| Playable source shorter than 0.5s | Reject as *too short*, not as corrupt codec; preserve localized error across language switch | **PASS real ST/isolated MT Chrome #38853679777**, 4-frame 15fps (~0.27s) H.264; JA/EN and stale result checks |
| VFR / ~1fps source | Exact frame grid, no missing/duplicate frames | Desktop ST/MT and user-specific Android/PC regression **PASS** on earlier snapshots; not exhaustive VFR acceptance |
| Portrait native dimensions | Aspect and orientation correct after export | Native 90×160 output previously desktop Chrome **PASS**; 90/180/270° rotation metadata remains **UNVERIFIED** |
| HEVC/H.265 MOV from iPhone | Preview, rotate and MP4 export or actionable unsupported state | **DEFERRED / UNVERIFIED** on physical iPhone; do not advertise iPhone HEVC support |
| HDR, 10-bit, BT.2020/PQ/HLG | Detect/preserve color or reject/explicitly warn | **LIMITATION DISCLOSED, NOT VERIFIED**. No reliable HDR/10-bit detection or preserved colors claimed; a successful preview alone is insufficient |
| Multiple audio tracks | Known track selected or unsupported explained accurately | **NOT IMPLEMENTED** as a selectable feature. Single supported audio source may work, with no multi-track fidelity guarantee |
| Silent source | AAC option disabled, H.264-only export | **PASS in prior real ST/MT Chrome suites** |
| Supported AAC audio source | Reverse/ping-pong AAC with expected time and channels | **PASS in prior real ST/MT Chrome suites**; device seam listening still pending |
| Invalid extension / MIME / renamed fake MP4 | Clear unsupported/invalid-header error, no output | **PASS prior ST/MT browser/Node tests** |
| Truncated/corrupt/unreadable source | No stale result or partial MP4; relevant error | **Partially PASS** for fake header/decoder failures. Extended real corrupt-file matrix **PENDING** |
| Source >1GiB, empty input, Android provider | Reject huge/empty; fallback bounded to <=64MiB if direct reading fails | **Implemented and browser-simulated**, full-copy fallback remains a **known G2 violation** and real provider matrix pending |
| 720p10s / 1080p5s repeated device stability | Three repeat exports, timing/RAM, no crash | **G2 NOT PASSED**. Selected desktop ST/MT full-size results exist, not full phone repeats |
| Single HTML `file://`, ST readable / self-extract | Real local selection/reverse/MP4 save without network access | **PASS prior desktop Chrome CI #38850394911** |
| Isolated MT website / CSP / network | Correct COI and local media handling, no runtime upload | **PASS on previous Chrome/CI build**; test again after each material change |
| Native iPhone Safari save | End-to-end including Files/Photos destination | **DEFERRED / NOT VERIFIED** |

## 2026-10-16 verified v0.8 browser checkpoint

[App CI #38853679777](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38853679777) **ALL SUCCESS**:
Windows standalone build/Node, genuine ST and isolated MT Chrome
H.264 30fps/60fps sources both exported as decoded/ffprobed
15-frame/1s H.264 MP4, decodable 0.27s source given the distinct
too-short error in JA/EN, and v0.7 regression of 10s frame order,
VFR/sparse frame checks, real AAC/Ping-pong, source replacement,
cancellation, invalid inputs, CSP/no unexpected external requests,
and direct ST `file://` readable/self-extract. The [PR preview
#38853679768](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38853679768) succeeded. The high-resolution MT
endurance job was SKIPPED, not measured.

The initial 30fps fixture passed while the next test discovered
the source compatibility disclosure stayed open after replacing a
video. The source-specific disclosure is now reset by `releaseSource`,
and the corrected [full browser CI #38853679777](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38853679777) passes.

These results cover locally generated H.264 test files on desktop
Chrome. **No claim** is made about physical Android performance,
iPhone HEVC MOV, HDR color fidelity, or all real-world 30/60fps VFR
decoding behavior.

## Acceptance and release policy

- Keep source bytes on the device. No new runtime CDN, telemetry, fetch or media upload.
- Never treat a successful preview, 15fps export, or missing frame-count mismatch as proof of HDR color fidelity or HEVC/iPhone compatibility.
- On an unsupported or corrupt input, fail closed. Never enable download of an unverified MP4.
- v0.8 acceptance requires a reviewed compatibility matrix and absence of **known serious regressions** in the defined supported scope. Mark anything not tested as unknown, not PASS.
- Distinguish **v0.8 development progression** from formal G2, v0.9 RC and v1 stable release. Do not merge app Draft PR #1/#2 or Builder Draft PR #16 and do not modify Browser Kitty main repository.
