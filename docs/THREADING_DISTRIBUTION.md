# Reverse Clip — ST / MT distribution

**Latest-build distribution:** Pages publishes raw MT at `/index.mt.html` for import by header-isolated hosts such as Browser Kitty. This updates the distribution route only, not app/runtime versions, release assets, security policy, or device-support claims. The current `reverse-runtime.lock.json` remains the source of truth for pinned runtime assets; the historical publication and migration notes below do not describe the current integration state.

| Distribution | Actual runtime | Delivery / isolation |
| --- | --- | --- |
| GitHub Pages root `/` | **Single-thread** (`dist/index.html`) | No special headers; ordinary browser use and direct `file://` standalone |
| GitHub Pages `/mt/` | **Multi-thread** (`dist/index.mt.html`) | Same-origin pinned `coi-serviceworker` loads conditionally to provide COOP/COEP; first visit can reload |
| GitHub Pages `/index.mt.html` | **Multi-thread** (byte-identical to `dist/index.mt.html`) | Raw import/download artifact only; no SW bootstrap and no isolation headers on Pages. Not a directly usable Pages MT entry point. |
| Browser Kitty `/apps/reverse-clip.html` | **Multi-thread** (latest-build import source: Pages `/index.mt.html`) | Cloudflare static asset response headers only for this route: COOP `same-origin`, COEP `require-corp`, CORP `same-origin`; raw HTML has no SW bootstrap. Importer configuration is maintained separately in Browser Kitty. |
| Standalone ST `reverse-clip.html` | **Single-thread** | Single offline HTML; `file://` is intended |
| Standalone MT `reverse-clip.mt.html` | **Multi-thread** | Single HTML but requires HTTPS/localhost with cross-origin isolation, cannot work from a raw `file://` navigation |

**Reference implementation:** `ttomohisa/htmlapps-ffmpeg-filter-builder`, particularly `docs/MULTI_THREAD_DEPLOYMENT.md`, `scripts/prepare-pages.ps1` and its dual-profile Builder metadata. Reverse Clip uses its **own dedicated `video-reverse` WASM runner**, not the Filter Builder's FFmpeg UI or assets.

## Build and immutability

The Reverse Clip app pins a **specific `htmlapps-ffmpeg-wasm-builder` commit and release** in `reverse-runtime.lock.json`, independent SHA-256 for both WASM+JS cores, and one common hashed `browser-ffmpeg.js` loader. The Windows template build imports only during build and embeds all assets into:

- `dist/index.html` (ST) and `dist/index.self-extract.html` (ST compressed self-extract)
- `dist/index.mt.html` (MT) and `dist/index.mt.self-extract.html` (MT compressed self-extract)
- root copies `reverse-clip.html` and `reverse-clip.mt.html` (the respective standalone HTML bytes)

`scripts/prepare-pages.ps1` stages `pages-dist/index.html` for ST, `pages-dist/mt/index.html` for Service Worker-isolated MT, and a byte-identical raw copy at `pages-dist/index.mt.html`. The raw URL tracks the latest successful main-branch Pages deployment, not an immutable app release. A vendor-pinned, SHA-checked `coi-serviceworker.js` is deployed only into `pages-dist/mt/`; **standalone/raw MT HTML does not contain or require this file** when hosted on a server that provides the correct COOP/COEP headers. On GitHub Pages itself, use `/mt/` for MT or `/` for ST; raw `/index.mt.html` cannot convert without cross-origin isolation. MIT license: `licenses/coi-serviceworker-MIT.txt`; source pin: `coi-serviceworker.lock.json`.

`tests/feasibility/threading-distribution.test.mjs` checks the actual generated ST+MT HTML manifests, SHA-256 of embedded decompressed WASM/JS, correct pthread/isolation metadata and lack of runtime CDN. `tests/feasibility/pages-dual-thread.test.mjs` checks ST Pages root, MT Pages wrapper, pinned worker, and raw MT byte parity with no SW bootstrap.

## Runtime behavior

The multi-thread app checks both `globalThis.crossOriginIsolated` and `SharedArrayBuffer` before letting the user convert. If missing, the page remains readable and shows a localized instruction; **do not silently fall back to ST while claiming MT**. ST is an explicit alternative at GitHub Pages root. Browser Kitty routes must be isolated server-side; do not apply these headers globally.

The original Android ST-mode user reports (10-second clip, 84.73s) are not proof of MT performance. Do not promise a conversion speedup or suggest the new binary has been tested on a physical Android phone before that result exists.

## Historical publication ordering

1. Review and merge the **Builder dual-profile Draft PR**, build both outputs with actual Docker + browser smoke, and publish a fixed, GPL source-complete runtime release (not an expiring Actions zip).
2. Merge the **Reverse Clip dual-output PR** after CI and MT Pages isolation tests. GitHub Pages root and `/mt/` become available from the deployed main branch; direct MT HTML remains a separate artifact.
3. **After Reverse Clip is feature-complete, device-verified and stable-release-ready, and the owner chooses portal integration:** only then open a Browser Kitty PR to import **MT** at `/apps/reverse-clip.html`, with route-scoped COOP/COEP/CORP. Validate actual deployed HTML, SHA-256, headers, output MP4, cancel/retry and user-file privacy. Until then, do not create or update Browser Kitty integration PRs.
4. Owner merges every PR. Do not treat successful static packaging as proof of end-to-end physical-device MT or as final release approval.

**Limitation:** The Pages MT worker is a functional fallback on browsers allowing same-origin service workers and isolation; private browsing or restrictive service-worker settings may prevent activation. Browser Kitty MT uses direct HTTP response headers instead.

## Historical immutable release migration plan

The following pre-release plan is retained as history. The active lock now uses `kind: github-release-st-mt`; this raw Pages copy does not modify it or any immutable release asset.

The current `reverse-runtime.lock.json` still uses `kind: experimental-dual-github-actions-artifact` with an expiring Actions artifact ID. An additional code path now supports `kind: github-release-st-mt` **after** a reviewed, permanent Builder Release is published. Do not switch the active lock to a nonexistent or unreviewed version.

The reviewed lock will need the exact `builderTag` equal to `v<builderVersion>`, `correspondingSourceAsset` and `correspondingSourceSha256`, plus each variant's exact `releaseAsset` and `releaseArchiveSha256`. The importer accepts only the expected `ffmpeg-wasm-video-reverse-<single-thread|multi-thread>-v<version>.zip` names, checks the downloaded ZIP SHA-256, verifies its own profile/threading/isolation manifest, verifies SHA-256 for FFmpeg JS/WASM and loader, and requires FFmpeg/x264/Emscripten notices and BUILDINFO inside the ZIP. It does **not** need GITHUB_TOKEN for a public immutable Release.

Both variant hashes and the public corresponding-source archive must be reviewed against the actual Builder Release and source tree before updating the lock. Merely writing SHA-256 fields in JSON does not establish license compliance. The `video-reverse` source-bundle packaging workflow in Builder is **manual/review-only** and does not publish the release. No Browser Kitty PR is to be opened while the app is unfinished.
