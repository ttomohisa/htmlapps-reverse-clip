# Reverse Clip v0.9.0 — RCチェックリスト / Release Candidate acceptance

**Status: PREPARATION / NOT APPROVED (2026-10-16).** Version 0.9.0 is a development milestone, NOT a signed-off RC, Gate G2 pass or Gate G3 pass. All PRs stay Draft and unmerged, and no release, tag or Browser Kitty main-site update is authorized. iPhone Safari is deferred, not marked as passed.

Authoritative acceptance: [APP_SPEC.md](../../APP_SPEC.md) A-01–A-14; [DEVELOPMENT_PLAN.md](../../DEVELOPMENT_PLAN.md) Gates G1–G3; [G2 evidence](../feasibility/G2.md); [v0.8 source compatibility](../feasibility/V080_COMPATIBILITY_MATRIX.md).

## Individual acceptance cases

| Case | Requirement | Evidence and limits | Result |
| --- | --- | --- | --- |
| A-01 | Correct reverse frame order | Actual desktop Chrome ST/isolated MT 10-second reverse H.264 full-frame fixture [CI #38864099711](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38864099711) | **PASS desktop** |
| A-02 | Ping-pong turn no noticeable missing/duplicate/black frames | Actual Chrome frame & join test PASS; physical-device viewing pending | **PARTIAL** |
| A-03 | Accurate start/end trim | Fractional, .5s, end boundary MP4 regression PASS; expanded device frame-difference evidence pending | **PARTIAL** |
| A-04 | Correct silent/AAC and ~150ms audio sync | Desktop Chrome reversed/ping-pong AAC decoded PCM mono/stereo PASS; actual phone listening and explicit ±150ms not accepted | **PARTIAL** |
| A-05 | Portrait MOV, 90/180/270° orientation, VFR | Synthetic H.264 MOV orientation verified against pixels; real phone HEVC/HDR/VFR unknown | **PARTIAL** |
| A-06 | MP4 playback on target device player | Browser preview/ffprobe PASS; Android Downloads/Photos OS player for current version and iPhone pending | **PARTIAL** |
| A-07 | No stale result on change/cancel/taps/reload | Source generation and Abort, actual Chrome lifecycle tests PASS; physical device suspend/retry pending | **PARTIAL** |
| A-08 | Distinguishable empty/running/success/error/unsupported | Localized Chrome states and safe corruption/HEVC rejection PASS; human device review pending | **PARTIAL** |
| A-09 | Mobile widths, long filename, short view, modal/soft keyboard | Browser 320×420, 320×568, 360/390px PASS; physical Android soft keyboard pending | **PARTIAL** |
| A-10 | Japanese and English UI/help/errors | Automated toggling and locale error tests PASS; human JA/EN screenshot/review pending | **PARTIAL** |
| A-11 | No runtime data upload or external dependency | CSP connect-src 'none' and ST/MT real Chrome network tests PASS; distribution bytes not released | **PARTIAL** |
| A-12 | Normal and self-extract ST file://, CSP/Worker/WASM/save | Both direct file:// ST standalone variants generated/saved MP4 on desktop Chrome; hosted MT needs COOP/COEP, Windows Edge manual QA pending | **PARTIAL** |
| A-13 | README JA/EN, changelog, licenses, favicon, JA/EN screenshots and CI | Docs/lock/favicon exist. **Real screenshots absent, permanent source-complete GPL Builder distribution missing** | **PENDING** |
| A-14 | Correct source/settings/result/filename correspondence | Chrome confirms stale MP4 invalidation, replacement confirmation, filename and no partial download; physical input providers pending | **PARTIAL** |

## Release blockers

| Gate or item | Status | Required action |
| --- | --- | --- |
| Gate G2 actual Android 720p10s/1080p5s Reverse+Ping-pong ×3 | **OPEN / NOT PASSED** | Real device/browser/source, RAM, timing, files from gallery/Downloads, cancellation, speaker audio and sync |
| Android <=64MiB file-provider fallback | **KNOWN G2 DEVIATION** | Source entire file may be copied in memory after WorkerFS failure. Remove or obtain explicit revised G2 acceptance; do not silently waive |
| Gate G3 | **NOT PASSED** | Confirm every A-01–A-14 item, supported platform scope and final build/license/screenshot readiness |
| iPhone Safari / HEVC MOV | **DEFERRED / NOT VERIFIED** | Owner postponed iPhone; must decide formal release target/platform claims before stable version |
| Runtime source license and permanence | **BLOCKED** | `reverse-runtime.lock.json` remains `temporary-not-release`, Builder 1.10.6 action artifact 11914029733 with documented Oct 21 2026 expiry; need reviewed immutable GPL corresponding-source Release |
| Actual screenshots | **PENDING** | Capture actual rendered JA and EN application screenshots (result, not just empty state) without mockups |
| Windows Edge and current Android phone | **PENDING** | Capture exact version/OS/device, real camera, picker/cloud, keyboard, performance and save results |

## Feature freeze and verification

No new codecs or features in RC preparation. Keep existing source guards, silent default, 15fps, bounded segments, ST file://, MT isolation, privacy and all v0.7/v0.8 tested functionality.

- [x] v0.9 development version (not tagged)
- [x] Earlier ST/MT real browser media regressions and source compatibility
- [ ] Final `0.9.0` head CI, offline ST and real MT browser PASS
- [ ] Current Android G2 evidence, no-copy mitigation/revised acceptance, audible joins and measured resource usage
- [ ] Permanent source-complete GPL distribution, JA/EN screenshots, manual Edge/Android UI
- [ ] Separate Gate G2 and Gate G3 final signoff and user-approved merge/publication

**Gate G3 NOT PASSED.** A version number is not release approval.
