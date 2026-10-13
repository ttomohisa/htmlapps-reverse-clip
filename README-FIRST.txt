Reverse Clip v0.4.0 — Reverse & Ping-pong experimental development milestone (NOT stable).
Select local MP4/MOV, trim with accessible handles, choose Reverse or forward-and-back Ping-pong.
The new source-to-WASM run encodes exactly 2N−2 H.264 frames for ping-pong,
excluding repeated turning/loop endpoint frames; no audio until v0.5.0.
Real desktop Chrome ST/MT CI passed 15→28, 31→60 and 150→298 output frames,
minimum 0.5s, true VFR, black source media and portrait 90x160 input.
Evidence: https://github.com/ttomohisa/htmlapps-reverse-clip/actions/runs/38347758127
Browser runtime bytes are pinned to ST/MT Builder commit fa52f86b27675f5c7b6c7fba52a73d38ac766687.
WARNING: Builder Actions artifact ID 11789347043 EXPIRES ON 2026-10-20.
A permanent versioned GPL source-complete release is still required.
ST direct file:// and self-extract builds are verified; MT requires isolation.
Pending: physical Android MT/memory/quality, 720p10s/1080p5s stress, camera
rotation metadata, audio, GPL release verification and final acceptance gates.
Browser Kitty integration is deferred; its original Draft PR #41 closed unmerged.
