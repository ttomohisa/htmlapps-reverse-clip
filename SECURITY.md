# Security Policy

## Supported version

Security fixes target the latest version on the default branch.

## Reporting a vulnerability

Do not publish sensitive vulnerability details in a public issue. Use the repository owner's private security reporting channel when available.

Include:

- Affected commit or version.
- Reproduction steps.
- Expected and actual behavior.
- Security impact.
- A minimal test file when file parsing is involved.

## Trust model

The default template is a static browser application with no backend. Its primary protections are:

- No ordinary runtime CDN/API connection (`connect-src 'none'`). Optional peer-to-peer WebRTC must be explicit in the product specification and must not introduce hidden signaling/STUN/TURN services.
- Explicitly pinned and embedded third-party files.
- Committed `dependencies.lock.json` tarball SHA-256 values verified before embedding.
- SHA-256 records in the generated dependency manifest.
- No analytics, telemetry, remote fonts, or silent update checks.
- User-initiated downloads rather than automatic uploads.

A generated HTML file is executable code. Distribute it through a trusted channel and verify hashes for high-trust workflows.

If an app uses `components/webrtc-qr-pairing.html`, treat the paired browser as an explicit data recipient. “No server upload” does not mean “data never leaves this device.” Keep the manual signaling and `iceServers: []` boundary visible in the UI/help text, and do not silently add STUN/TURN later.

## Input files

Applications created from this template may parse untrusted local files. Implementations should:

- Validate type, size, and structure before expensive processing.
- Avoid unbounded allocation or recursion.
- Handle malformed data without exposing stack traces to users.
- Release Blob URLs, workers, canvas resources, and large buffers.
- Make destructive transformations reversible where practical.
- Never upload a selected file unless the product explicitly requires it and the user is clearly informed.

## Dependency review

Before adding or upgrading a package:

- Confirm the package identity and exact version.
- Review the scheduled dependency Issue; never treat an available update as an automatic approval to upgrade.
- Review its license and required notices.
- Inspect the browser bundle and package scripts.
- Confirm every runtime support asset is embedded.
- Refresh the selected lock entry with the dependency scripts; never hand-edit a lock hash to bypass a mismatch.
- Rebuild with a clean cache.
- Test with the network disabled.

## Reverse Clip experimental binary boundary

The app embeds a single-thread FFmpeg/x264 WASM core licensed GPL-2.0-or-later, **not MIT**, and a small public-libav runner. The runtime is retrieved only at build time from a pinned Builder GitHub Actions artifact; every core file is SHA-256 verified against `reverse-runtime.lock.json`. There is no per-user runtime fetch: `connect-src 'none'` remains active. Actions artifacts are temporary, not a stable release distribution channel. The final release requires corresponding source and license-notice validation.

Video inputs may be untrusted or provider-backed on Android. Files up to 64MiB may be copied to browser memory, then used by MEMFS to avoid unreliable Worker-side `FileReaderSync` grants. Output bytes and buffers must be released on source change, cancel and page exit. Peak memory must be measured on actual mobile hardware before raising length/resolution limits.

## v0.1.4 frame count / long-running conversion guard

The experimental 10s mode executes no more than 2 seconds per independent WASM reversal segment, then remuxes the completed H.264 chunks. The Builder checks **encoded video packet counts** against the caller's expected frame total for each segment and the final MP4, refusing partial or mismatched results. The original input is still copied into MEMFS on Android only up to 64 MiB; that temporary copy plus the WASM heap and the accumulated compressed MP4 chunks consumes additional memory. Do not interpret a per-chunk YUV420 estimate as a hard peak-memory ceiling. Memory and cancellation/retry on physical Android require validation before stable distribution.
