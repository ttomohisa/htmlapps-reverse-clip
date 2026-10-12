# Third-party notices — experimental build

The Reverse Clip application source is MIT-licensed. Its **embedded FFmpeg 9.0.1 + x264** single-thread WASM runtime is separately **GPL-2.0-or-later**, not MIT. Distribution of the binary requires satisfying the relevant licenses and making the corresponding source available. This PoC must not be tagged as a general public release before those obligations are reviewed.

Provenance: `ttomohisa/htmlapps-ffmpeg-wasm-builder` at commit `b67b1e2f19eef802791ca733884709155f10dfb5`, Builder 1.10.4, FFmpeg ref n9.0.1 (commit `bf1b838f2ab88b4f8fd83443325c782ea0e0f7fa`) and x264 stable (commit `31e19f92f00c7003fa115047ce50978bc98c3a0d`). See `reverse-runtime.lock.json` for asset SHA-256; build tooling rejects mismatches.

The BrowserFFmpeg loader and the public-libav runner are supplied from the same Builder source revision. The Builder repository's pinned dependencies, license metadata, notices, corresponding sources and release packaging must accompany any eventual permanent release.

Temporary CI artifact ID 11715866319 expires. Use only for preview / technical G1 testing until a stable, source-complete Builder Release is available.

## GitHub Pages MT-only isolation helper

The GitHub Pages `/mt/` deployment conditionally loads `coi-serviceworker` **v0.1.7** by Guido Zuidhof and contributors (MIT license). Exact commit and SHA-256 are pinned in `coi-serviceworker.lock.json`, and its full MIT notice is in `licenses/coi-serviceworker-MIT.txt`. This script is **not embedded in either ST or MT single HTML artifact**, because it is only a Pages fallback for COOP/COEP; Browser Kitty supplies HTTP isolation headers instead. It contains no video upload or telemetry.
