# Reverse Clip v0.5.0 — Audio modes acceptance matrix

**Status: IMPLEMENTATION IN PROGRESS; audio output not yet approved or publicly released.**

Separate the existing v0.4 working video-only function from v0.5 candidate audio. The audio selector defaults to silent and **must remain disabled** while the pinned `reverse-runtime.lock.json` lacks `audio-mux`.

| Check | Expected behavior | Current status |
|---|---|---|
| Builder ST: source audio header inspection | Return codec/channel info without whole-file read, distinguish audio-free media | PENDING real CI |
| Builder MT: reverse one selected AAC interval | Real encoded AAC track, no silent-only success | PENDING real CI |
| Builder ST+MT: ping-pong audio 0..N−1,N−2..1 | Positive directional waveform / correct duration | PENDING real CI |
| Builder ST+MT: H.264 + AAC MP4 remux | Exactly 1 H.264 video + 1 AAC audio, no temporary placeholder video | PENDING real CI |
| App ST+MT real Chrome MP4 | 300Hz/990Hz reverse tone correlation, ping-pong return, duration/sync | PENDING real CI |
| Mono and stereo source; source without audio | Source audio recognized; absent/unsupported audio clearly disables option | PENDING |
| Cancellation, source switch, retry | No stale audio or download survives | PENDING |
| 0.5/5/10 second clips | Audio in tolerance, no gross clip silence or end gap | PENDING |
| Android physical hardware ST+MT | Repeat export and listen for clicks, no memory crash | PENDING |
| Permanent GPL corresponding-source WASM Release | Source, notices, versioned archives, SHA fixed | PENDING |

**v0.5 release gate:** set `audio-mux` on the SHA-pinned runtime only after full Builder ST/MT A/V smoke, then run `audio-browser-smoke.py` with real MP4 downloads and actual decoded PCM checks. Physical audio quality and mobile performance are additional required product acceptance evidence, not proven by desktop emulation.

Browser Kitty import remains deferred; earlier portal Draft PR #41 closed unmerged. Reverse Clip PR #2 and Builder PR #16 are Draft/unmerged.
