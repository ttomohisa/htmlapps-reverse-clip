# Reverse Clip v0.9.0 — Release Notes (DRAFT ONLY)

**NOT FOR PUBLICATION.** RC preparation, NOT a signed-off release candidate; G2/G3 OPEN.

Reverse Clip creates locally processed reversed or forward-back (Ping-pong) H.264 MP4 clips. Output is 15fps and silent by default; supported source audio can use reverse AAC. Source files are not uploaded.

Validated only in desktop Chrome ST / isolated MT: marked H.264 frame order, AAC mono/stereo, VFR/sparse, 30/60fps input to 15fps output, H.264 MOV with 90/180/270° display-matrix orientation, invalid/corrupt input fail-closed, and local ST `file://` readable/self-extract HTML. Some Android basic use was reported on an older pinned test version, NOT on v0.9.

Limits: HEVC/HDR color fidelity not guaranteed; unsupported synthetic HEVC 8/10-bit rejected in the tested desktop Chrome. Multiple source audio tracks cannot be selected. Android input providers may trigger <=64MiB whole-source fallback copy, conflicting with original G2. Higher quality and long export remain experimental. Download initiation does not prove OS save completion. iPhone deferred.

See [RC_CHECKLIST.md](RC_CHECKLIST.md). No tag, release, merge or Browser Kitty integration until actual Android QA, source-complete immutable GPL Builder distribution, supported-platform scope and Gate G2/G3 acceptance are resolved.
