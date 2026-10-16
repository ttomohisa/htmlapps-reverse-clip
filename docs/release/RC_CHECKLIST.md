# Reverse Clip v0.9.0 — RCチェックリスト / Release Candidate acceptance

**2026-10-17: PREPARATION / NOT APPROVED. Gate G3 NOT PASSED.**
The RC is not a published release; PR #2, PR #1 and Builder PR #16 remain open Drafts. The user requested **less excessive testing while keeping real safeguards**. Refer to [revised initial-release scope](REVISED_ACCEPTANCE_SCOPE.md) for the proposed P0/P1/P2 criteria. These revised criteria are a proposal applied to RC planning, **not** a retrospective PASS of the original G2 or authorization to publish.

References: [APP_SPEC.md A-01–A-14](../../APP_SPEC.md), [DEVELOPMENT_PLAN.md](../../DEVELOPMENT_PLAN.md), [historical G2 evidence](../feasibility/G2.md), [v0.8 compatibility matrix](../feasibility/V080_COMPATIBILITY_MATRIX.md).

## P0 — mandatory for proposed initial scope

| Requirement | Evidence and action | Status |
| --- | --- | --- |
| ST and MT actual H.264 Reverse + Ping-pong, bounded trim and playable MP4 | Desktop Chrome source/MP4 frame-order tests PASS [CI #38866625722](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38866625722). Verify release candidate bytes on next build | **AUTOMATED PASS** |
| Actual Android Chrome H.264 5s Reverse at long edge ≤720px and 1–3s Ping-pong, one run **each** | Record device/version, source, input provider, save destination and MP4 playback on latest v0.9 RC HTML. No mandatory triple repetitions | **PENDING — PHYSICAL DEVICE** |
| Android cancellation/retry and one supported audio listening check | One cancel→retry and one short AAC Reverse (when supported); no obvious click/no-audio/large A/V desync. Automated PCM/AAC tests PASS but latest phone run PENDING | **PENDING — PHYSICAL DEVICE** |
| Incorrect output prevention and privacy | Reject truncated/unsupported input, no stale/partial MP4, verify original+output association, no runtime uploads/external dependencies, truthful saving, bounded fallback behavior. Actual ST/MT Chrome PASS; final distribution review still needed | **PARTIAL** |
| Final artifact and GPL distribution | Reproducible pinned ST single HTML direct `file://` and hosted isolated MT; fixed hashes, third-party notices, reviewed **permanent source-complete GPL Builder distribution**, full JA/EN README and actual screenshots | **PENDING — DISTRIBUTION** |
| Critical bugs in **claimed** core features | 0 known P0 failures (data leak, broken output, normal supported input unable to save); no claim of unverified formats/phones | **PENDING — FINAL REVIEW** |

The 64MiB Android provider fallback is a **KNOWN G2 DEVIATION** from the original strict zero-copy requirement. For this revised initial-release scope, the proposed P0 safety rule permits a **conditional local whole-file copy only when direct reads fail and file size ≤64MiB**, with clear error and no large-file silent copy. **This is not a historical G2 pass** and still requires code/phone acceptance under the scoped RC review.

## P1 / P2 — not unconditional initial-release blockers

- **P1 useful spot checks:** Windows Edge 1 workflow, extra Android phone or input provider, different H.264 source, a11y/help/keyboard manual review. Required only if that browser/source is *advertised* as fully supported.
- **P2 experimental stress:** Android and iPhone **720p10s / 1080p5s, Reverse and Ping-pong ×3 each**, detailed peak RAM benchmark, exhaustive 90/180/270° with real HEVC/HDR/VFR combinations, sample-rate matrices and an unconditional **no-whole-input-copy up to 1 GiB**. Useful for promoting the pilot quality options, not a base-scope requirement.
- If high quality or HEVC/other browsers remain in the UI, they must be **clearly experimental/unsupported and fail safely**. A defect affecting core P0 output, users' data or privacy can never be downgraded to P2.

## APP_SPEC A-01–A-14 traceability (all reviewed, evidence scoped)

| ID | Acceptance | Source of evidence / remaining check | Classification |
| --- | --- | --- | --- |
| A-01 | Reverse frame order | ST/MT real H.264 Chrome 10s frame markers CI #38866625722 | **P0 automated PASS** |
| A-02 | Ping-pong order/turn | ST/MT Chrome full-frame and join checks PASS; Android one short case PENDING | **P0 pending device** |
| A-03 | Trim boundaries | Chrome half-frame/fractional source trim PASS; exhaustive all-device frame-difference report **P2** | **P0 automated PASS** |
| A-04 | Silent, AAC, A/V synchronization | Chrome PCM/AAC tests PASS; one human audible Android check PENDING. Exact ≤150ms hardware measurement **P2** unless a defect is found | **P0 pending device** |
| A-05 | Portrait MOV/rotation/VFR | Synthetic H.264 MOV 90/180/270° + VFR Chrome PASS. Real HEVC/HDR/mobile combination **P2** outside claimed supported input | **P0 for claimed format; P2 others** |
| A-06 | Actual MP4 playable | Desktop Chrome and ffprobe PASS; latest Android Downloads/player playback PENDING | **P0 pending device** |
| A-07 | No stale output after cancellation/change | Chrome generation+Abort, source changes/retry PASS; one Android cancellation PENDING | **P0 pending device** |
| A-08 | Empty/loading/completion/error/unsupported | Localized Chrome flow and broken/HEVC fail-closed PASS; real device representative error PENDING | **P0 automated / manual** |
| A-09 | 320/360/390, long names, small height, dialogs | Browser 320×420, 320×568, 360/390px PASS. Full real keyboard matrix **P1**; one Android flow **P0** | **P0 automated / manual** |
| A-10 | JA and EN UI/help/errors | Automated toggle, error messages PASS. Editorial review and actual screenshots PENDING | **P0 pending docs** |
| A-11 | No upload or runtime external dependency | `connect-src 'none'`, real ST/MT no unexpected network on Chrome PASS; verify final exact distribution | **P0 pending final build** |
| A-12 | Standalone ST/self-extract file:// | Real desktop Chrome standalone MP4 PASS; MT hosted isolation validated. Windows Edge direct manual **P1** | **P0 automated PASS** |
| A-13 | README JA/EN, licenses, favicon, real screenshots, CI | Four genuine Chrome JA/EN desktop/mobile-viewport screenshot PNGs are committed, SHA-256 locked; README links reviewed. Permanent GPL corresponding-source distribution still missing | **P0 partial: screenshots PASS, GPL release PENDING** |
| A-14 | Source/settings/result/filename linked | Confirmation/invalidation/filename, no partial MP4 browser tests PASS; one Android saved file verification PENDING | **P0 pending device** |

## Five-minute Android smoke form (one representative handset; no unnecessary matrix)

Capture: device and Android/Chrome versions, whether testing ST or isolated MT, H.264 source dimensions and provider (Camera/Gallery/Downloads), selected range/quality/mode and observed result.

- [ ] **Reverse:** choose one local H.264 MP4, select ~0–5 s, long edge 360px or 720px, generate, save and replay the MP4 in the phone's player.
- [ ] **Ping-pong:** same video, choose ~0–2 s, verify turn direction and saved MP4 playback.
- [ ] **Cancel/retry:** stop one conversion, restart and confirm no stale/partial MP4 is available.
- [ ] **Audio if source supported:** select reverse-audio once, listen for obvious noise, silence or gross A/V misalignment. No laboratory millisecond measurement.
- [ ] **Input/provider and save:** verify chosen source appears correctly, user-editable output filename and file destination are understandable. If a provider cannot be read, report error and memory fallback rather than force high-resolution repetitions.

No certification from the owner's earlier Android v0.6 Pages smoke carries over automatically to the latest v0.9 bytes. Record real QA before marking the device P0 PASS.

## 2026-10-17 — verified desktop Chrome screenshots and pinned GPL package audit

**Screenshots:** [app CI #38939628625](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38939628625)
**ALL SUCCESS** including ST/MT real H.264/AAC MP4 smoke and the
`reverse-clip-v090-real-ui-e8a8ce59664ff25bfc37112e60eac6730d614b04`
GitHub artifact (ID **12062302953**, GitHub expiry **2026-11-15T17:29:47Z**).
The screenshot runner first generated and downloaded a 1-second,
15-frame H.264 MP4 and verified the output with ffprobe, then captured
its Result UI in **Japanese/English × desktop 1360×900/mobile 390×844**.
A Japanese-capable font was installed **only on the CI runner**
to prevent missing glyphs. Screenshots were independently reviewed
from the downloaded ZIP (manifest and all four SHA-256 hashes matched,
all results contained a visible video, heading and Save button).
They are *synthetic local H.264 media in desktop Chrome viewports*,
not a physical phone or browser-OS save screenshot.

**Historical screenshot note:** the initial testsrc2/calibration images were not suitable for README use and were intentionally rejected. The later representative-motion screenshots from [CI #38944766865](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38944766865) passed technical checks, were visually reviewed without buffering overlays, and their exact bytes were checked into `assets/` by [one-time checksum-verified import CI #38945924515](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38945924515). Both READMEs now link the image assets. See [image digest manifest](RC_SCREENSHOT_ASSET_MANIFEST.json). **A-13 screenshots PASS but A-13 overall still PENDING permanent GPL source-complete distribution**; these Chrome viewport images are not Android physical proof.

**Matching video-reverse 1.10.6 GPL review package:** independently
downloaded Builder [review run #38617100332](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/actions/runs/38617100332)
artifact ID **11920042823** (~74.6 MB; expires **2026-10-21T18:41Z**).
All **5 SHA256SUMS** entries passed. The two inner ST/MT ZIP bundles'
four JS/WASM hashes and shared browser loader hash were independently
recomputed and exactly matched `reverse-runtime.lock.json`;
FFmpeg, x264, Emscripten upstream source trees, Builder build recipe,
BUILDINFO and applicable notices were present in the corresponding
source archive. See [Builder technical audit](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/blob/feat/video-reverse-poc/docs/VIDEO_REVERSE_SOURCE_RELEASE.md)
and [Builder Draft PR #16](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/pull/16).

**Source-release status:** package/hash/source-*presence* technical
audit PASS. **LEGAL CORRESPONDING-SOURCE REVIEW AND PERMANENT PUBLIC
DOWNLOAD STILL PENDING**; current app runtime lock remains
`temporary-not-release`. No tag, release, merge or portal import.

## RC exit decision

- P0 evidence all complete, no known severe core bug; exact claimed platform/source compatibility clearly stated.
- Permanent corresponding-source FFmpeg/x264/Emscripten GPL distribution and asset hashes reviewed.
- **G3 NOT PASSED** until final checklist, device proof and explicit approval. Historical G2 remains **NOT PASSED**, with separate revised release acceptance documented.
- No automatic merge or release. User merges after review; Browser Kitty main site is a separate future task.
