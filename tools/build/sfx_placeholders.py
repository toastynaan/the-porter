"""Placeholder sounds for the greybox, synthesised (no recordings, no licence).

Writes 22.05 kHz mono 16-bit WAVs to art/sfx/:
  sfx_step_<surface>_<n>.wav   footsteps on stone, wood, mud and grass (4 each)
  sfx_door_open.wav            heavy door: latch click and a creak
  sfx_door_close.wav           heavy door: thud and latch
  sfx_door_locked.wav          a locked door rattling
  amb_wind_night.wav           20 s seamless wind loop

Replace them with recordings when the sound pass comes; keep the file names.
Run: python3 tools/build/sfx_placeholders.py
"""

import math
import os
import random
import struct
import wave

RATE = 22050
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "art", "sfx")


def write(name, samples, peak=0.8):
    top = max(1e-9, max(abs(s) for s in samples))
    scale = peak / top
    path = os.path.join(OUT, name)
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(RATE)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, s * scale)) * 32767)) for s in samples))
    print("wrote", os.path.normpath(path))


def noise(n, rng):
    return [rng.uniform(-1.0, 1.0) for _ in range(n)]


def lowpass(x, cutoff):
    a = 1.0 - math.exp(-2.0 * math.pi * cutoff / RATE)
    y, out = 0.0, []
    for s in x:
        y += a * (s - y)
        out.append(y)
    return out


def highpass(x, cutoff):
    low = lowpass(x, cutoff)
    return [s - l for s, l in zip(x, low)]


def bandpass(x, f0, q):
    """RBJ biquad band-pass (constant peak gain)."""
    w0 = 2.0 * math.pi * f0 / RATE
    alpha = math.sin(w0) / (2.0 * q)
    b0, b2 = alpha, -alpha
    a0, a1, a2 = 1.0 + alpha, -2.0 * math.cos(w0), 1.0 - alpha
    x1 = x2 = y1 = y2 = 0.0
    out = []
    for s in x:
        y = (b0 * s + b2 * x2 - a1 * y1 - a2 * y2) / a0
        x2, x1, y2, y1 = x1, s, y1, y
        out.append(y)
    return out


def env(n, attack, decay):
    """Attack (s) then exponential decay with time constant `decay` (s)."""
    a = max(1, int(attack * RATE))
    return [(i / a) if i < a else math.exp(-(i - a) / (decay * RATE)) for i in range(n)]


def tone(n, freq, decay, rng, detune=0.03):
    f = freq * (1.0 + rng.uniform(-detune, detune))
    return [math.sin(2.0 * math.pi * f * i / RATE) * math.exp(-i / (decay * RATE)) for i in range(n)]


def mix(*tracks):
    n = max(len(t) for t in tracks)
    return [sum(t[i] if i < len(t) else 0.0 for t in tracks) for i in range(n)]


def gain(x, g):
    return [s * g for s in x]


def step(surface, rng):
    if surface == "stone":
        n = int(0.14 * RATE)
        click = [a * b for a, b in zip(highpass(noise(n, rng), 1800), env(n, 0.001, 0.012))]
        scuff = [a * b for a, b in zip(bandpass(noise(n, rng), 900, 0.8), env(n, 0.004, 0.04))]
        thump = tone(n, 110, 0.03, rng)
        return mix(click, gain(scuff, 0.5), gain(thump, 0.6))
    if surface == "wood":
        n = int(0.2 * RATE)
        knock = mix(tone(n, 95, 0.06, rng), gain(tone(n, 190, 0.04, rng), 0.6), gain(tone(n, 350, 0.025, rng), 0.35))
        tap = [a * b for a, b in zip(bandpass(noise(n, rng), 1500, 1.2), env(n, 0.001, 0.01))]
        return mix(knock, gain(tap, 0.5))
    if surface == "mud":
        n = int(0.24 * RATE)
        squelch = [a * b for a, b in zip(lowpass(noise(n, rng), 500), env(n, 0.02, 0.07))]
        suck = [a * b for a, b in zip(bandpass(noise(n, rng), 300 + rng.uniform(-40, 40), 3.0), env(n, 0.06, 0.05))]
        return mix(squelch, gain(suck, 1.2), gain(tone(n, 70, 0.05, rng), 0.4))
    # grass
    n = int(0.18 * RATE)
    rustle = [a * b for a, b in zip(bandpass(noise(n, rng), 2400, 0.7), env(n, 0.015, 0.05))]
    return mix(rustle, gain(tone(n, 80, 0.03, rng), 0.3))


def creak(rng, seconds=0.7):
    n = int(seconds * RATE)
    out, phase = [], 0.0
    for i in range(n):
        t = i / n
        f = 170 + 90 * t + 25 * math.sin(2 * math.pi * 3.0 * t)
        phase += f / RATE
        saw = 2.0 * (phase % 1.0) - 1.0
        stick = 0.5 + 0.5 * math.sin(2 * math.pi * 23 * t + rng.uniform(-0.3, 0.3))
        a = min(1.0, t * 8) * (1.0 - t) ** 0.6
        out.append(saw * stick * a)
    return bandpass(out, 700, 1.5)


def latch(rng):
    n = int(0.08 * RATE)
    return [a * b for a, b in zip(highpass(noise(n, rng), 2500), env(n, 0.0005, 0.006))]


def thud(rng):
    n = int(0.5 * RATE)
    body = mix(tone(n, 55, 0.12, rng), gain(tone(n, 110, 0.06, rng), 0.5))
    hit = [a * b for a, b in zip(lowpass(noise(n, rng), 800), env(n, 0.002, 0.04))]
    return mix(body, gain(hit, 0.8))


def pad(x, seconds):
    return [0.0] * int(seconds * RATE) + x


def wind(rng, seconds=20.0, fade=2.0):
    n = int((seconds + fade) * RATE)
    src = lowpass(noise(n, rng), 900)
    # Two band-passed layers whose centre and level drift slowly: gusts.
    low = bandpass(src, 180, 0.7)
    high = bandpass(src, 520, 2.5)
    out = []
    for i in range(n):
        t = i / RATE
        gust = 0.55 + 0.25 * math.sin(2 * math.pi * t / 7.3) + 0.2 * math.sin(2 * math.pi * t / 3.1 + 1.3)
        whistle = max(0.0, math.sin(2 * math.pi * t / 9.7 + 0.4)) ** 3
        out.append(low[i] * gust + high[i] * whistle * 0.5)
    # Seamless loop: crossfade the extra tail into the start.
    body = out[: int(seconds * RATE)]
    f = int(fade * RATE)
    tail = out[int(seconds * RATE):]
    for i in range(f):
        k = i / f
        body[i] = body[i] * k + tail[i] * (1.0 - k)
    return body


def main():
    os.makedirs(OUT, exist_ok=True)
    rng = random.Random(1340)
    for surface in ("stone", "wood", "mud", "grass"):
        for k in range(4):
            write(f"sfx_step_{surface}_{k}.wav", step(surface, rng), peak=0.7)
    write("sfx_door_open.wav", mix(latch(rng), pad(creak(rng), 0.06)))
    write("sfx_door_close.wav", mix(thud(rng), pad(gain(latch(rng), 0.6), 0.03)))
    write("sfx_door_locked.wav", mix(*[pad(gain(latch(rng), 1.0 - 0.15 * k), 0.07 * k) for k in range(5)]))
    write("amb_wind_night.wav", wind(rng), peak=0.6)


if __name__ == "__main__":
    main()
