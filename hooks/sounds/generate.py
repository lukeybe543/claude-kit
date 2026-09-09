"""Synthesise the notification sounds that ship beside notify.py.

Pure standard library. Run it to (re)write the WAVs in this directory:

    python3 generate.py                 # the five sounds notify.py plays
    python3 generate.py --candidates    # also write candidates/ to audition

FM synthesis (one carrier, one modulator, the modulation index decaying) gives a
struck-bell / music-box timbre from a few lines of maths -- far warmer than
stacked sine waves. Output is deterministic, so a regenerated file is
byte-identical.

WAV, not ogg: winsound (Windows) and aplay both play only WAV, and
_sound_seconds reads duration with wave.open.
"""

import math
import struct
import sys
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent

RATE = 44_100
PEAK = 0.30
FADE_IN = 0.006

_A4 = 440.0
def _p(semitones):                       # equal-tempered pitch, semitones from A4
    return _A4 * 2 ** (semitones / 12)

A4, C5, F5, A5, C6, D6, E6, G6, A6 = (
    _p(0), _p(3), _p(8), _p(12), _p(15), _p(17), _p(19), _p(22), _p(24)
)


def _voice(freq, ratio, index0, dur, gain=1.0):
    """One FM-bell note: carrier `freq`, modulator `freq*ratio`, index decaying.

    ratio near a small integer sounds like wood; inharmonic (1.4, 2.4, 3.5)
    sounds like glass or metal. index0 is how bright the strike is.
    """
    n = int(RATE * dur)
    for i in range(n):
        t = i / RATE
        amp = math.exp(-t / (dur * 0.30))
        if t < FADE_IN:
            amp *= t / FADE_IN
        index = index0 * math.exp(-t / (dur * 0.22))
        mod = index * math.sin(2 * math.pi * freq * ratio * t)
        yield (i, math.sin(2 * math.pi * freq * t + mod) * amp * gain)


def _render(parts):
    rendered = [(int(RATE * start), list(gen)) for start, gen in parts]
    length = 1 + max(offset + (block[-1][0] if block else 0)
                     for offset, block in rendered)
    buf = [0.0] * length
    for offset, block in rendered:
        for i, sample in block:
            buf[offset + i] += sample
    peak = max((abs(x) for x in buf), default=1.0) or 1.0
    scale = PEAK / peak
    return b"".join(struct.pack("<h", int(max(-1.0, min(1.0, x * scale)) * 32767))
                    for x in buf)


def _write(path, parts):
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(_render(parts))
    with wave.open(str(path)) as w:
        return w.getnframes() / w.getframerate()


# Each sound is a list of (start_seconds, FM voice).
SOUNDS = {
    # a warm struck bell, low index so it is round rather than clangy
    "needs-you": [
        (0.00, _voice(A5, 1.41, 3.2, 1.0)),
        (0.00, _voice(A5 * 2, 1.41, 1.4, 0.8, gain=0.35)),
    ],
    "done": [
        (0.00, _voice(C6, 2.0, 1.6, 0.7, gain=0.8)),
    ],
    "pass": [
        (0.00, _voice(C6, 2.0, 1.8, 0.5)),
        (0.14, _voice(G6, 2.0, 1.8, 0.7)),
    ],
    "fail": [
        (0.00, _voice(A5, 3.5, 2.2, 0.5)),
        (0.17, _voice(F5, 3.5, 2.4, 0.9, gain=0.9)),
    ],
    "compacting": [
        (0.00, _voice(A4, 1.41, 2.4, 1.1, gain=0.75)),
    ],
}

# Alternatives for "needs-you", to audition and copy over needs-you.wav.
CANDIDATES = {
    "1-music-box": [
        (0.00, _voice(E6, 2.0, 2.2, 1.0)),
        (0.00, _voice(E6 * 2, 2.0, 1.0, 0.8, gain=0.3)),
    ],
    "2-soft-bell": [                       # = the current needs-you
        (0.00, _voice(A5, 1.41, 3.2, 1.5)),
        (0.00, _voice(A5 * 2, 1.41, 1.4, 1.2, gain=0.35)),
    ],
    "3-marimba": [
        (0.00, _voice(C6, 3.0, 1.4, 0.45)),
        (0.10, _voice(G6, 3.0, 1.4, 0.55, gain=0.9)),
    ],
    "4-two-note-chime": [
        (0.00, _voice(A5, 2.0, 1.6, 0.5, gain=0.9)),
        (0.22, _voice(D6, 2.0, 1.6, 0.9)),
    ],
    "5-glass-ping": [
        (0.00, _voice(A6, 2.4, 1.1, 1.4, gain=0.9)),
    ],
}


def main():
    for name, parts in SOUNDS.items():
        print(f"{name}.wav  {_write(HERE / f'{name}.wav', parts):.2f}s")
    if "--candidates" in sys.argv:
        out = HERE / "candidates"
        out.mkdir(exist_ok=True)
        for name, parts in CANDIDATES.items():
            print(f"candidates/{name}.wav  {_write(out / f'{name}.wav', parts):.2f}s")


if __name__ == "__main__":
    main()
