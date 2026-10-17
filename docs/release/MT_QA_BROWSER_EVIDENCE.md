# Reverse Clip v0.9.0 — current MT QA browser evidence (2026-10-17)

**Status: remote desktop Chrome MT PASS; subsequent Android MT four-action owner smoke USER-REPORTED PASS.** Not an approved release and no change to historical G2 or Gate G3 (both NOT PASSED).

## Endpoints and exact build

- Temporary, non-portal QA Worker: `rc-reverse-clip-mt-qa`, separate from `bk-previews` and Browser Kitty's production site.
- **MT QA test URL:** https://rc-reverse-clip-mt-qa.ttomohisa.workers.dev/mt/
- ST control: https://rc-reverse-clip-mt-qa.ttomohisa.workers.dev/
- Actual source commit in [first passing GitHub Actions run #38954969819](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38954969819): `8c26329424a2123a847b252fefd401e16ce05d52`. Later documentation-only commits do not change the tested runtime. Verify subsequent staging workflow runs if source/build inputs change.
- Exact pinned Builder runtime from `reverse-runtime.lock.json`: FFmpeg 1.10.6 experimental ST/MT binary still downloaded from temporary Actions provenance. This QA deployment is **not** an immutable Builder Release.

## Why this route uses a Service Worker

Cloudflare `wrangler preview` produced the genuine v0.9 ST and MT HTML, but actual response probes found **no** `Cross-Origin-Opener-Policy`, `Cross-Origin-Embedder-Policy` or `Cross-Origin-Resource-Policy` headers on `/index.mt.html`. An application-controlled Worker diagnostic header (`X-RC-Preview-Worker: active`) was present, establishing that the script did execute but the isolation headers did not survive that Preview response. A separately deployed temporary Workers.dev QA Worker had the same missing-header behavior.

Rather than declaring this MT-supported, the QA pipeline reuses the **already-tested GitHub Pages distribution layout**: Windows builds genuine `dist/index.html` (ST) and `dist/index.mt.html` (MT), then `scripts/prepare-pages.ps1` writes `pages-dist/index.html` (ST) and `pages-dist/mt/index.html` (MT) plus the source-pinned `coi-serviceworker.js`. The temporary QA Worker serves these exact files. The MT-only Service Worker reloads/isolates `/mt/` without changing the normal ST root. Direct downloadable MT standalone HTML still requires appropriate isolation from its actual HTTP host; `file://` MT is **not** promised.

## Live browser acceptance evidence

GitHub Actions [#38954969819](https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38954969819) **all jobs SUCCESS** (the earlier missing-`tar.exe` Linux build and direct-COOP failed staging attempts are superseded):

1. Windows `scripts/check-repository.ps1` built and verified pinned ST/MT assets; `scripts/prepare-pages.ps1` validated SHA-256-pinned same-origin COI Worker and generated Pages-style outputs.
2. Ubuntu deployed these exact outputs to the separate QA Workers.dev service and installed actual Chrome, Playwright and native FFmpeg/ffprobe.
3. [`tests/feasibility/pages-browser-smoke.py`](../../tests/feasibility/pages-browser-smoke.py) ran against **the deployed Workers.dev hostname**, not a local test HTTP server: ST root was non-isolated; `/mt/` acquired cross-origin isolation, SharedArrayBuffer and active Service Worker; MT converted and downloaded a genuine 1-second H.264 reversed MP4, validated by ffprobe; returning to root remained non-isolated.

CI stdout included:

```text
[PASS] GitHub Pages ST root is available without isolation
[PASS] Pages MT first-visit COI worker and real reversed MP4
[PASS] Pages ST remains unisolated after MT worker install
```

The test uses the GitHub Pages-style SW implementation but targets the temporary Cloudflare QA origin. This CI is **desktop Linux Chrome proof only**, not Android physical performance/memory/sound testing. Separately, the owner later reported **「MTも4つOK」** after testing the four requested operations on Android Chrome ([owner evidence](ANDROID_MT_RC_OWNER_SMOKE.md)); no phone logs/measurements were obtained. A separate owner-reported Android **ST** smoke is recorded in [`ANDROID_ST_RC_OWNER_SMOKE.md`](ANDROID_ST_RC_OWNER_SMOKE.md).

## Android MT owner smoke completed; next release action

The owner was given the **MT QA URL** and four specific checks: (a) reverse/save/replay, (b) ping-pong/save/replay, (c) cancel/retry, (d) listen to reversed audio. On 2026-10-17 the owner responded **「MTも4つOK」**. Record this as **USER-REPORTED PASS for all four MT QA phone smoke actions**; see [Android MT owner smoke](ANDROID_MT_RC_OWNER_SMOKE.md). Do not infer phone metadata or exact codec/timing from that reply.

**Next:** permanent corresponding-source-complete GPL Builder distribution, verify the exact final hosted MT runtime and release scope, and close G3 only after explicit review. Avoid requiring redundant high-load phone tests outside the agreed release scope.

No external user-video upload, no Builder release, tag, PR merge or Browser Kitty import is included. The QA Worker should be removed once acceptance is complete to avoid an indefinite publicly reachable development copy.
