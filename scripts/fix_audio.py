"""Rebuild the demo's audio track: 48 kHz, a faint floor under the title card, one clean mux.

Usage:
    python scripts/fix_audio.py demo.mp4 demo-final.mp4

vidkit's render leaves the intro delay as exact digital zeros and can emit 96 kHz audio
with broken AAC packet timestamps. This decodes the audio once to a 48 kHz mono WAV, mixes
a -60 dB dark noise floor under the title card only (lowpassed at 1 kHz, nothing under
60 Hz, 30 ms fade in, faded out before the voice), and muxes that WAV with the untouched
video stream.
"""

from __future__ import annotations

import subprocess
import sys
import wave
from pathlib import Path

import numpy as np

SR = 48000
INTRO = 4.15  # seconds of floor: the title card plus the gap before the first word at 4.26 s


def main(src: str, dst: str) -> None:
    tmp = Path(dst).with_suffix(".decoded.wav")
    fixed = Path(dst).with_suffix(".fixed.wav")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vn", "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", str(tmp)], check=True)
    with wave.open(str(tmp)) as w:
        audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).astype(np.float64) / 32768

    n = int(INTRO * SR)
    rng = np.random.default_rng(0)
    noise = rng.standard_normal(n)
    # one-pole lowpass at 1 kHz, then a one-pole highpass at 60 Hz
    a = np.exp(-2 * np.pi * 1000 / SR)
    lp = np.empty(n)
    acc = 0.0
    for i in range(n):
        acc = (1 - a) * noise[i] + a * acc
        lp[i] = acc
    b = np.exp(-2 * np.pi * 60 / SR)
    hp = np.empty(n)
    prev_x = prev_y = 0.0
    for i in range(n):
        y = b * (prev_y + lp[i] - prev_x)
        prev_x, prev_y = lp[i], y
        hp[i] = y
    target = 10 ** (-60 / 20)
    hp *= target / (np.sqrt(np.mean(hp ** 2)) or 1)
    env = np.ones(n)
    fin = int(0.03 * SR)
    env[:fin] = np.linspace(0, 1, fin)
    fout = int(0.4 * SR)
    env[n - fout:] = np.linspace(1, 0, fout)
    audio[:n] += hp * env

    out = np.clip(audio * 32767, -32768, 32767).astype(np.int16)
    with wave.open(str(fixed), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(out.tobytes())
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-i", str(fixed), "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "192k", "-ar", str(SR), "-movflags", "+faststart", dst], check=True)
    tmp.unlink()
    fixed.unlink()
    print(f"wrote {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
