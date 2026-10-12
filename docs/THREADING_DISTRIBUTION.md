# Reverse Clip — ST / MT distribution

**Development target:** Android Chrome and Windows Chrome/Edge. iPhone testing is deferred. Both runtime builds are experimental until the pinned FFmpeg/x264/Emscripten GPL-corresponding-source release and RC tests are complete.

| Distribution | Actual runtime | Delivery / isolation |
| --- | --- | --- |
| GitHub Pages root `/` | **Single-thread** (`dist/index.html`) | No special headers; ordinary browser use and direct `file://` standalone |
| GitHub Pages `/mt/` | **Multi-thread** (`dist/index.mt.html`) | Same-origin pinned `coi-serviceworker` loads conditionally to provide COOP/COEP; first visit can reload |
| Browser Kitty `/apps/reverse-clip.html` (once added) | **Multi-thread** (from Pages `/mt/`) | Cloudflare static asset response headers only for this route: COOP `same-origin`, COEP `require-corp`, CORP `same-origin`; no SW bootstrap request when `crossOriginIsolated` is already true |
| Standalone ST `reverse-clip.html` | **Single-thread** | Single offline HTML; `file://` is intended |
| Standalone MT `reverse-clip.mt.html` | **Multi-thread** | Single HTML but requires HTTPS/localhost with cross-origin isolation, cannot work from a raw `file://` navigation |

**Reference implementation:** `ttomohisa/htmlapps-ffmpeg-filter-builder`, particularly `docs/MULTI_THREAD_DEPLOYMENT.md`, `scripts/prepare-pages.ps1` and its dual-profile Builder metadata. Reverse Clip uses its **own dedicated `video-reverse` WASM runner**, not the Filter Builder's FFmpeg UI or assets.

## Build and immutability

The Reverse Clip app pins a **specific `htmlapps-ffmpeg-wasm-builder` commit**, a dedicated **ST+MT dual-profile Actions artifact**, independent SHA-256 for both WASM+JS cores, and one common hashed `browser-ffmpeg.js` loader. The Windows template build imports only during build and embeds all assets into:

- `dist/index.html` (ST) and `dist/index.self-extract.html` (ST compressed self-extract)
- `dist/index.mt.html` (MT) and `dist/index.mt.self-extract.html` (MT compressed self-extract)
- root copies `reverse-clip.html` and `reverse-clip.mt.html` (the respective standalone HTML bytes)

`scripts/prepare-pages.ps1` stages `pages-dist/index.html` for ST and `pages-dist/mt/index.html` for MT. A vendor-pinned, SHA-checked `coi-serviceworker.js` is deployed only into `pages-dist/mt/`; **standalone MT HTML does not contain or require this file** when hosted on a server that provides the correct COOP/COEP headers. MIT license: `licenses/coi-serviceworker-MIT.txt`; source pin: `coi-serviceworker.lock.json`.

`tests/feasibility/threading-distribution.test.mjs` checks the actual generated ST+MT HTML manifests, SHA-256 of embedded decompressed WASM/JS, correct pthread/isolation metadata and lack of runtime CDN. `tests/feasibility/pages-dual-thread.test.mjs` checks ST Pages root, MT Pages wrapper and pinned worker.

## Runtime behavior

The multi-thread app checks both `globalThis.crossOriginIsolated` and `SharedArrayBuffer` before letting the user convert. If missing, the page remains readable and shows a localized instruction; **do not silently fall back to ST while claiming MT**. ST is an explicit alternative at GitHub Pages root. Browser Kitty routes must be isolated server-side; do not apply these headers globally.

The original Android ST-mode user reports (10-second clip, 84.73s) are not proof of MT performance. Do not promise a conversion speedup or suggest the new binary has been tested on a physical Android phone before that result exists.

## Publication ordering

1. Review and merge the **Builder dual-profile Draft PR**, build both outputs with actual Docker + browser smoke, and publish a fixed, GPL source-complete runtime release (not an expiring Actions zip).
2. Merge the **Reverse Clip dual-output PR** after CI and MT Pages isolation tests. GitHub Pages root and `/mt/` become available from the deployed main branch; direct MT HTML remains a separate artifact.
3. Import/verify **only MT** into Browser Kitty's `/apps/reverse-clip.html`, with COOP/COEP/CORP route headers. Check the actual downloaded app HTML and runtime manifest, its HTTP headers, output MP4, cancel/retry and user-file privacy. Do not edit the Browser Kitty portal homepage copy.
4. Owner merges every PR. Do not treat successful static packaging as proof of end-to-end physical-device MT or as final release approval.

**Limitation:** The Pages MT worker is a functional fallback on browsers allowing same-origin service workers and isolation; private browsing or restrictive service-worker settings may prevent activation. Browser Kitty MT uses direct HTTP response headers instead.
