# Reverse Clip v0.9.0 — RCチェックリスト / Release Candidate acceptance

**Current status 2026-10-19: v0.9.0 merged to main, app NOT RELEASED. Gate G3 NOT PASSED.**
PR #1, PR #2, PR #6 and Builder PR #16 have all been merged. The dedicated GPL Builder WASM/source Release is public. The RC is not an app GitHub Release. Earlier entries below are retained as dated historical evidence. The user requested **less excessive testing while keeping real safeguards**. Refer to [revised initial-release scope](REVISED_ACCEPTANCE_SCOPE.md) for the proposed P0/P1/P2 criteria. These revised criteria are a proposal applied to RC planning, **not** a retrospective PASS of the original G2 or authorization to publish.

References: [APP_SPEC.md A-01–A-14](../../APP_SPEC.md), [DEVELOPMENT_PLAN.md](../../DEVELOPMENT_PLAN.md), [historical G2 evidence](../feasibility/G2.md), [v0.8 compatibility matrix](../feasibility/V080_COMPATIBILITY_MATRIX.md), [2026-10-17 Android ST owner smoke](ANDROID_ST_RC_OWNER_SMOKE.md), [latest MT test deployment](MT_QA_BROWSER_EVIDENCE.md), [2026-10-17 Android MT owner smoke](ANDROID_MT_RC_OWNER_SMOKE.md).

## 2026-10-19 — Builder dedicated FFmpeg WASM Release PUBLISHED; app RC integrated into main

**Builder dependency release available:** [video-reverse-v1.10.6](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/releases/tag/video-reverse-v1.10.6) with exact ST/MT original binary ZIPs, corresponding source, two BUILDINFO, SHA256SUMS and separately pinned GPL/x264 disclosure. [Builder public publishing CI #39179947875](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/actions/runs/39179947875) **SUCCESS**, including unauthenticated public-download SHA-256 proof. The app's active `reverse-runtime.lock.json` is now `github-release-st-mt` / `release-approved`: this approves **only the published WASM dependency**, not Reverse Clip's own v0.9.0 release.

**Current action:** App v0.9.0 was built from the public Release and ST/MT desktop Chrome, AAC, isolated MT and preview passed. The merged main Pages build/deploy also passed [CI #39182815120](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/39182815120). Prepare the focused [v1.0.0 acceptance](V100_RELEASE_READINESS.md) and app release artifacts. No new real-phone matrix, binary rebuild or additional licensing review requested. Historical October 17–18 notes below describe the *then*-unpublished state and are not the current dependency status.

## 2026-10-19 — original Actions dependency expires; review-only build fallback verified (historical)

The active lock still pins Builder 1.10.6 compiled assets from Actions artifact **11914029733**, expiring **2026-10-21T17:11:44Z**. Without mitigation, a clean build could fail once that artifact disappears, even though a later audited source-complete review archive is retained.

- Added `scripts/restore-reviewed-video-reverse-runtime.ps1` as a **build-time-only, temporary** fallback. The existing importer uses it only after the original artifact returns HTTP **404/410**, or when explicitly requested for an isolated CI test. Authentication/server errors are not silently downgraded.
- The fallback uses retained Builder review artifact **12145680508**, expiring **2026-11-17T17:48:11Z**. It refuses unexpected/missing stage payloads, compares the original whole ST/MT ZIP and source TAR SHA-256 digests, GPL notice digest, original five `SHA256SUMS` entries, review-only/unapproved metadata, BUILDINFO, and exact existing JS/WASM/browser-loader lock SHA values.
- [Actual Windows backup test CI #39152055729](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/39152055729) **PASS**: both ST and MT imported from the review archive and subsequently reused their verified caches. No original WASM rebuild, new binary, production import, app runtime downloads, or owner device retest.
- The application `reverse-runtime.lock.json` remains **unchanged** and **`temporary-not-release`**. This backup is not a durable public GPL distribution or a release-approved source. It too expires on November 17 and remains subordinate to final corresponding-source/licensing review and permanent Release publication.

Gate G3 remains **NOT PASSED**. This protects continued Draft build/QA; it does not authorize PR merges, publication, or calling the runtime released.
## 2026-10-17 — Android ST + MT four-action owner smoke

The owner confirmed **「4つともOK」** for the v0.9 **ST** Preview and then separately **「MTも4つOK」** after testing the latest **MT** temporary QA URL on Android Chrome. Both were answers to the same four requested actions: Reverse MP4 save/replay, Ping-pong save/replay, cancel→retry, and audible reversed audio. **ST + MT owner-reported basic Android smoke PASS**, not independently collected phone logs or ffprobe proof. Hardware/browser versions, exact input/output metadata, file-provider details and accurate timings were not supplied. [ST evidence](ANDROID_ST_RC_OWNER_SMOKE.md) · [MT evidence](ANDROID_MT_RC_OWNER_SMOKE.md).

This closes the **user-performed basic Android P0 smoke-feedback task**, not original historical Gate G2, which remains **NOT PASSED**, and not G3, which remains **NOT PASSED**. The final MT distribution must still be verified if hosting/runtime changes; permanent GPL corresponding-source binary/source publication and owner review remain blockers.

## 2026-10-17 — latest MT hosted browser proof (NOT Android device acceptance)

[Temporary QA deployment / build CI #38954969819](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38954969819) **SUCCESS** using branch `8c263294`. The exact current MT standalone was rebuilt on Windows, staged under [`/mt/`](https://rc-reverse-clip-mt-qa.ttomohisa.workers.dev/mt/) with the existing pinned COI Service Worker, and a **real remote Chrome test** confirmed cross-origin isolation, SharedArrayBuffer, conversion and saving of a 1-second H.264 reversed MP4. ST at root stayed non-isolated even after registration. The standard Wrangler Preview's response headers still did not provide direct COOP/COEP, so do not use its `/index.mt.html` as an MT acceptance URL.

**MT Chrome-hosted CI PASS; Android phone MT four-action owner smoke subsequently USER-REPORTED PASS** (see [MT owner record](ANDROID_MT_RC_OWNER_SMOKE.md)); The QA URL is temporary, not Browser Kitty and not a versioned GPL release; no Android RAM/audio hardware metrics were measured. [Evidence and exact scope](MT_QA_BROWSER_EVIDENCE.md).

## 2026-10-17 — Builder source-complete promotion staged, **NOT released**

Builder [review staging CI #39004330416](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/actions/runs/39004330416) **SUCCESS**: the already-audited ST/MT 1.10.6 byte-identical ZIPs, corresponding-source tarball, original BUILDINFO files and SHA256SUMS were rechecked and staged as review-only Actions artifact **12089984511** (expires **2026-11-16T04:55:02Z**). No rebuild or public distribution occurred.

The Builder-wide `v1.10.6` Release already exists **without video-reverse assets**, so it must not be overwritten. A distinct profile-scoped `video-reverse-v1.10.6` tag is **only a proposed publication name**, currently not created. See [Builder publication handoff](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/blob/feat/video-reverse-poc/docs/VIDEO_REVERSE_PUBLICATION_HANDOFF.md). The app's future Release importer now accepts that exact tag format and checks both the publicly downloadable source archive hash and binary ZIP hash, plus a per-variant verified cache marker. The active `reverse-runtime.lock.json` remains **`temporary-not-release`**.

**Public permanent GPL corresponding-source distribution and owner/legal review remain P0 BLOCKERS**, and G3 is NOT PASSED. The archive is an expiring review copy, not a substitute for public matching-source availability.

## 2026-10-17 — original GPL NOTICE omission and audited addendum

Inspection of the exact original ST/MT Builder 1.10.6 binary ZIPs found
that their included generic `THIRD_PARTY_NOTICES.md` lacks the name
`video-reverse` in its x264/GPL profile enumeration, even though both
binary `BUILDINFO.txt` files explicitly state `Profile: video-reverse`,
`Generated core license: GPL-2.0-or-later` and x264 linkage.

Builder adds a [separate GPL/x264 profile disclosure](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/blob/feat/video-reverse-poc/docs/VIDEO_REVERSE_LICENSE_ADDENDUM.md) to the future publication package **without repacking or changing the SHA-256 of either existing WASM ZIP or the corresponding source**. [Builder staging CI #39006344474](https://github.com/ttomohisa/htmlapps-ffmpeg-wasm-builder/actions/runs/39006344474) **SUCCESS**, including explicit regression checks for the legacy notice omission, actual core GPL/x264 BUILDINFO, and separate addendum SHA-256. Refreshed **review-only** Actions artifact **12090973204**, expires **2026-11-16T05:28:00Z**.

The app's future `github-release-st-mt` importer will now fail closed unless the public Release has exact pinned `supplementalNoticeAsset` and `supplementalNoticeSha256` as well as matching source/binary SHA hashes. The **active** `reverse-runtime.lock.json` remains `temporary-not-release` and is not promoted. **P0 GPL/legal/publication gate remains PENDING; original G2 and G3 are NOT PASSED.** Never treat a review-only Actions artifact or this disclosure addendum as permanent matching-source publication or legal compliance approval.

## P0 — mandatory for proposed initial scope

| Requirement | Evidence and action | Status |
| --- | --- | --- |
| ST and MT actual H.264 Reverse + Ping-pong, bounded trim and playable MP4 | Desktop Chrome source/MP4 frame-order tests PASS [CI #38866625722](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38866625722). Verify release candidate bytes on next build | **AUTOMATED PASS** |
| Actual Android Chrome H.264 5s Reverse at long edge ≤720px and 1–3s Ping-pong, one run **each** | Owner confirmed all four requested workflows on latest ST PR Preview ([smoke record](ANDROID_ST_RC_OWNER_SMOKE.md)); settings/phone/provider not independently logged. the temporary MT QA owner smoke also passed four requested operations; exact phone/settings metadata not supplied. Final distributed MT deployment still requires release review | **ST+MT OWNER SMOKE PASS; final distribution PENDING** |
| Android cancellation/retry and one supported audio listening check | Owner replied “4つともOK” for ST Preview cancel/retry and reversed audio listening; AAC structural/sync checks remain desktop CI only. MT QA Android owner likewise confirmed four actions OK; precision AAC and memory metrics not collected | **ST+MT OWNER SMOKE PASS; final distribution PENDING** |
| Incorrect output prevention and privacy | Reject truncated/unsupported input, no stale/partial MP4, verify original+output association, no runtime uploads/external dependencies, truthful saving, bounded fallback behavior. Actual ST/MT Chrome PASS; final distribution review still needed | **PARTIAL** |
| Final artifact and GPL distribution | Pinned ST single HTML direct `file://` and hosted isolated MT; fixed hashes, corrected third-party notices, reviewed **publicly obtainable matching GPL source** with a visible link at each app download/distribution point, full JA/EN README and actual screenshots | **BUILDER DISTRIBUTION PASS; APP G3 QA PENDING** |
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
| A-02 | Ping-pong order/turn | ST/MT Chrome full-frame and join checks PASS; Android ST Preview and MT QA turn/save both user-reported OK; exact files unavailable | **P0 ST+MT owner smoke PASS** |
| A-03 | Trim boundaries | Chrome half-frame/fractional source trim PASS; exhaustive all-device frame-difference report **P2** | **P0 automated PASS** |
| A-04 | Silent, AAC, A/V synchronization | Chrome PCM/AAC tests PASS; owner-reported ST Android reversed audio audible. MT QA Android audio user-reported OK; exact device sync unmeasured; ≤150ms hardware measurement **P2** unless a defect is found | **P0 ST+MT owner smoke PASS; sync unmeasured** |
| A-05 | Portrait MOV/rotation/VFR | Synthetic H.264 MOV 90/180/270° + VFR Chrome PASS. Real HEVC/HDR/mobile combination **P2** outside claimed supported input | **P0 for claimed format; P2 others** |
| A-06 | Actual MP4 playable | Desktop Chrome/ffprobe PASS; owner replied OK to save/replay instructions for Android ST Preview. No original saved MP4 or hash received; MT QA phone save/replay user-reported OK | **P0 ST+MT owner smoke PASS; no output hashes** |
| A-07 | No stale output after cancellation/change | Chrome generation+Abort, source changes/retry PASS; owner-reported ST Android cancel→retry OK. MT QA Android cancel→retry also user-reported OK; explicit stale-output phone audit unlogged | **P0 ST+MT owner smoke PASS; stale-output detail unlogged** |
| A-08 | Empty/loading/completion/error/unsupported | Localized Chrome flow and broken/HEVC fail-closed PASS; real device representative error PENDING | **P0 automated / manual** |
| A-09 | 320/360/390, long names, small height, dialogs | Browser 320×420, 320×568, 360/390px PASS. ST and MT QA Android main workflows owner-reported OK; full keyboard matrix **P1** | **P0 ST+MT owner smoke PASS; keyboard P1** |
| A-10 | JA and EN UI/help/errors | Automated toggle and error messages PASS. JA/EN genuine Chrome desktop/mobile-viewport screenshots reviewed and committed; physical Android language/error review not separately captured | **P0 automated/docs PASS, device partial** |
| A-11 | No upload or runtime external dependency | `connect-src 'none'`, real ST/MT no unexpected network on Chrome PASS; verify final exact distribution | **P0 pending final build** |
| A-12 | Standalone ST/self-extract file:// | Real desktop Chrome standalone MP4 PASS; MT hosted isolation validated. Windows Edge direct manual **P1** | **P0 automated PASS** |
| A-13 | README JA/EN, licenses, favicon, real screenshots, CI | Four genuine Chrome JA/EN desktop/mobile-viewport screenshot PNGs are committed, SHA-256 locked; README links reviewed. Corrected runtime provenance in `THIRD_PARTY_NOTICES.md`; the public matching source URL is now available; the final app's distribution page must link to it | **P0 Builder source Release PASS; final app distribution QA PENDING** |
| A-14 | Source/settings/result/filename linked | Confirmation/invalidation/filename/no-partial-MP4 Chrome tests PASS; Android ST save/replay owner-reported OK. MT QA Android save/replay owner-reported OK; actual filename/provider/output hashes not supplied | **P0 ST+MT owner smoke PASS; details unlogged** |

## Five-minute Android smoke form (one representative handset; no unnecessary matrix)

Capture: device and Android/Chrome versions, whether testing ST or isolated MT, H.264 source dimensions and provider (Camera/Gallery/Downloads), selected range/quality/mode and observed result.

- [ ] **Reverse:** choose one local H.264 MP4, select ~0–5 s, long edge 360px or 720px, generate, save and replay the MP4 in the phone's player.
- [ ] **Ping-pong:** same video, choose ~0–2 s, verify turn direction and saved MP4 playback.
- [ ] **Cancel/retry:** stop one conversion, restart and confirm no stale/partial MP4 is available.
- [ ] **Audio if source supported:** select reverse-audio once, listen for obvious noise, silence or gross A/V misalignment. No laboratory millisecond measurement.
- [ ] **Input/provider and save:** verify chosen source appears correctly, user-editable output filename and file destination are understandable. If a provider cannot be read, report error and memory fallback rather than force high-resolution repetitions.

The previous Android v0.6 Pages smoke was not promoted to a v0.9 pass. On 2026-10-17, the owner separately confirmed **all four requested checks for the v0.9 ST Cloudflare PR Preview**, recorded in [ANDROID_ST_RC_OWNER_SMOKE.md](ANDROID_ST_RC_OWNER_SMOKE.md). On 2026-10-17, the owner also confirmed **all four MT QA checks** separately. Both are owner-reported smoke feedback, not independently captured device metadata or final production distribution acceptance.

## 2026-10-17 — v0.9 Android ST owner smoke (separate from MT)

The owner replied **「4つともOK」** after being asked to test (1) ~5s H.264 Reverse MP4 save/replay, (2) ~2s Ping-pong save/replay, (3) Cancel→Retry, and (4) audible reversed audio on the **latest ST Cloudflare PR Preview**, not Pages MT. Record this as **ST USER-REPORTED PASS for those four smoke items only**. Exact actual input properties, phone/browser versions and saved output hashes were not supplied; this is not a lab result. The temporary MT QA phone checks are now user-reported OK, but the final production MT distribution has not been signed off; permanent GPL source-complete WASM distribution, original G2 and G3 still remain open. [Detailed evidence and boundaries](ANDROID_ST_RC_OWNER_SMOKE.md).

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
