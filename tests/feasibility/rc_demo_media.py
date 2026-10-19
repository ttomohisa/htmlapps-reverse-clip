#!/usr/bin/env python3
"""Deterministic H.264 motion sample for real Reverse Clip UI screenshots.

Generated locally using Python stdlib and FFmpeg; no personal or downloaded
video, additional Python packages, font assets or runtime network traffic.
This sample is separate from the existing frame-order/codec test fixtures.
"""
from pathlib import Path
import subprocess
import tempfile


def make_rc_demo_video(destination):
    destination = Path(destination)
    width, height, fps, count = 384, 216, 30, 60
    with tempfile.TemporaryDirectory(prefix="rc-demo-") as scratch:
        frames = Path(scratch)
        for index in range(count):
            pixels = bytearray(width * height * 3)
            ball_x = 52 + index * 4
            ball_y = 149 - round(15 * (1 - abs(29.5 - index) / 29.5))
            for y in range(height):
                for x in range(width):
                    if y < 124:
                        color = (232, 239, 229)
                    elif y < 161:
                        color = (181, 204, 189)
                    else:
                        color = (47, 105, 82)
                    if 155 <= y < 187:
                        color = (215, 220, 203)
                    if 168 <= y < 172 and 25 <= x <= 357 and x % 36 < 18:
                        color = (250, 252, 246)
                    if ((x - 34) ** 2 + (y - 116) ** 2 < 14 ** 2 or
                        (x - 345) ** 2 + (y - 111) ** 2 < 20 ** 2):
                        color = (22, 96, 77)
                    if (x - 319) ** 2 + (y - 49) ** 2 < 30 ** 2:
                        color = (244, 181, 93)
                    if (x - ball_x) ** 2 + (y - ball_y) ** 2 < 17 ** 2:
                        color = (204, 92, 61)
                    off = (y * width + x) * 3
                    pixels[off:off + 3] = bytes(color)
            (frames / f"{index:03d}.ppm").write_bytes(
                f"P6\n{width} {height}\n255\n".encode("ascii") + pixels)
        subprocess.run([
            "ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
            "-framerate", str(fps), "-i", str(frames / "%03d.ppm"),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(destination)
        ], check=True)
    return destination


if __name__ == "__main__":
    make_rc_demo_video(Path("rc-demo.mp4"))
