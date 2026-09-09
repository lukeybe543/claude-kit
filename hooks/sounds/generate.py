"""Synthesise the notification sounds that ship beside notify.py.

Pure standard library. Run it to (re)write the five WAVs in this directory:

    python3 generate.py

The output is deterministic, so a regenerated file is byte-identical and shows
no diff. Sounds are soft on purpose -- sine tones with a little second-harmonic
warmth, a fast attack and an exponential decay, peaking well below full scale.
Edit a NOTES entry and re-run to retune.

WAV specifically, not ogg: winsound (Windows) and aplay both play only WAV, and
notify.py's _sound_seconds reads duration with wave.open.
"""

import math
import struct
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent

RATE = 44_100
PEAK = 0.34            # headroom -- these should never be startling
FADE_IN = 0.008        # seconds, enough to kill the leading click

# Equal-tempered pitches, A4 = 440.
_A4 = 440.0
def note(semitones_from_a4):
    return _A4 * 2 ** (semitones_from_a4 / 12)

A4, F5, A5, C6, E6, G6 = (
    note(0), note(8), note(12), note(15), note(19), note(22)
)

# event -> list of (frequency_hz, start_s, duration_s, gain)
NOTES = {
    # a gentle rising arpeggio -- "someone's asking for you", not an alarm
    "needs-you": [
        (A5, 0.00, 0.30, 1.00),
        (C6, 0.13, 0.30, 0.95),
        (E6, 0.26, 0.42, 0.90),
    ],
    # one soft note to close a long turn
    "done": [
        (C6, 0.00, 0.34, 0.75),
    ],
    # two notes rising -- verification passed
    "pass": [
        (C6, 0.00, 0.22, 0.85),
        (G6, 0.13, 0.34, 0.85),
    ],
    # two notes falling, unhurried -- something needs a look, still not harsh
    "fail": [
        (A5, 0.00, 0.26, 0.85),
        (F5, 0.16, 0.50, 0.80),
    ],
    # low and quiet -- the session is getting expensive
    "compacting": [
        (A4, 0.00, 0.50, 0.70),
    ],
}


def _render(voices):
    length = int(RATE * max(start + dur for _, start, dur, _ in voices)) + 1
    buf = [0.0] * length
    for freq, start, dur, gain in voices:
        n = int(RATE * dur)
        s0 = int(RATE * start)
        for i in range(n):
            t = i / RATE
            env = math.exp(-t / (dur * 0.32))               # exponential decay
            if t < FADE_IN:
                env *= t / FADE_IN                            # smooth the onset
            sample = (
                math.sin(2 * math.pi * freq * t)
                + 0.18 * math.sin(4 * math.pi * freq * t)     # a little warmth
            )
            buf[s0 + i] += sample * env * gain
    peak = max(abs(x) for x in buf) or 1.0
    scale = PEAK / peak
    return b"".join(
        struct.pack("<h", int(max(-1.0, min(1.0, x * scale)) * 32767)) for x in buf
    )


def main():
    for event, voices in NOTES.items():
        frames = _render(voices)
        with wave.open(str(HERE / f"{event}.wav"), "wb") as w:
            w.setnchannels(1)
            w.setsampwidth(2)
            w.setframerate(RATE)
            w.writeframes(frames)
        print(f"{event}.wav  {len(frames) / 2 / RATE:.2f}s")


if __name__ == "__main__":
    main()
