"""Placeholder sounds for the greybox, synthesised (no recordings, no licence).

Writes 22.05 kHz mono 16-bit WAVs to art/sfx/:
  sfx_step_<surface>_<n>.wav   footsteps on stone, wood, mud and grass (4 each)
  sfx_door_open.wav            heavy door: latch click and a creak
  sfx_door_close.wav           heavy door: thud and latch
  sfx_door_locked.wav          a locked door rattling
  amb_wind_night.wav           20 s seamless wind loop
  sfx_breath_loop.wav          the porter breathing (loop)
  sfx_pant_loop.wav            out of breath (loop): the porter winded, the hunter winded
  sfx_gasp.wav                 a held breath running out
  sfx_heartbeat_loop.wav       heartbeat while hiding (loop)
  sfx_ring_loop.wav            ringing ears while staring at the demon (loop)
  sfx_hoof_<n>.wav             carved hoof soles on stone (3)
  sfx_felt_<n>.wav             felt overshoes, barely there (3)
  sfx_hum_loop.wav             a hummed plainchant phrase (loop)
  sfx_rummage.wav              a hunter searching a hiding spot
  sfx_hide.wav                 climbing into a hiding spot
  sfx_key_turn.wav             a key turning in a lock
  sfx_capture.wav              caught
  sfx_rook_<n>.wav             rooks (3)
  sfx_rat_<n>.wav              rats (3)
  sfx_cat_0.wav                the abbey cat

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


def breath_cycle(rng, seconds, rate, depth=1.0):
    """Breathing: band-passed noise swelling on each in and out breath."""
    n = int(seconds * RATE)
    air = bandpass(noise(n, rng), 900, 0.6)
    out = []
    for i in range(n):
        ph = (i / RATE * rate) % 1.0
        # In-breath (0..0.4) then a softer, longer out-breath.
        a = math.sin(math.pi * ph / 0.4) if ph < 0.4 else 0.6 * math.sin(math.pi * (ph - 0.4) / 0.6)
        out.append(air[i] * max(0.0, a) ** 1.5 * depth)
    return out


def loopable(x, fade=0.3):
    """Crossfades the last `fade` seconds into the start."""
    f = int(fade * RATE)
    body, tail = x[:-f], x[-f:]
    for i in range(f):
        k = i / f
        body[i] = body[i] * k + tail[i] * (1.0 - k)
    return body


def gasp(rng):
    n = int(0.9 * RATE)
    air = bandpass(noise(n, rng), 1300, 0.9)
    return [s * (min(1.0, i / (0.05 * RATE)) * math.exp(-i / (0.25 * RATE))) for i, s in enumerate(air)]


def heartbeat(rng, bpm=96.0, beats=8):
    period = 60.0 / bpm
    n = int(period * beats * RATE)
    out = [0.0] * n
    for b in range(beats):
        for k, (delay, g) in enumerate(((0.0, 1.0), (0.24, 0.7))):
            thump = tone(int(0.2 * RATE), 48 + 6 * k, 0.05, rng, detune=0.0)
            start = int((b * period + delay) * RATE)
            for i, s in enumerate(thump):
                if start + i < n:
                    out[start + i] += s * g
    return out


def ring(seconds=6.0):
    n = int(seconds * RATE)
    # Two close tones beating slowly; whole cycles so it loops.
    f1, f2 = 3500.0, 3500.0 + 1.0 / seconds * 3
    return [0.6 * math.sin(2 * math.pi * f1 * i / RATE) + 0.4 * math.sin(2 * math.pi * f2 * i / RATE) for i in range(n)]


def hoof(rng):
    n = int(0.25 * RATE)
    clack = mix(tone(n, 620, 0.02, rng, 0.06), gain(tone(n, 1240, 0.012, rng, 0.06), 0.5))
    crack = [a * b for a, b in zip(highpass(noise(n, rng), 2000), env(n, 0.0005, 0.008))]
    return mix(clack, crack, gain(tone(n, 90, 0.04, rng), 0.6))


def felt(rng):
    n = int(0.2 * RATE)
    return [a * b for a, b in zip(lowpass(noise(n, rng), 350), env(n, 0.01, 0.04))]


def hum(rng):
    """A slow modal phrase hummed through the nose: harmonics under a soft formant."""
    notes = [(146.8, 1.2), (164.8, 0.8), (174.6, 1.2), (164.8, 0.8), (146.8, 1.6), (130.8, 1.0),
             (146.8, 2.0), (0.0, 1.4)]
    out, phase = [], 0.0
    for f, d in notes:
        n = int(d * RATE)
        for i in range(n):
            t = i / n
            if f == 0.0:
                out.append(0.0)
                continue
            vib = 1.0 + 0.006 * math.sin(2 * math.pi * 5.0 * i / RATE)
            phase += f * vib / RATE
            v = sum(math.sin(2 * math.pi * h * phase) / h ** 1.3 for h in range(1, 7))
            a = min(1.0, t * 6) * min(1.0, (1.0 - t) * 6)
            out.append(v * a)
    return bandpass(lowpass(out, 1200), 300, 0.5)


def rummage(rng):
    n = int(2.2 * RATE)
    base = bandpass(noise(n, rng), 1100, 0.7)
    out = []
    for i in range(n):
        t = i / RATE
        a = max(0.0, math.sin(2 * math.pi * 1.7 * t + rng.uniform(-0.2, 0.2))) ** 4
        out.append(base[i] * a)
    return mix(out, pad(gain(thud(rng), 0.5), 0.6), pad(gain(latch(rng), 0.6), 1.5))


def scrape(rng, seconds):
    n = int(seconds * RATE)
    base = bandpass(noise(n, rng), 600, 1.2)
    return [s * math.sin(math.pi * i / n) for i, s in enumerate(base)]


def key_turn(rng):
    clicks = [pad(gain(latch(rng), g), d) for d, g in ((0.0, 0.5), (0.12, 0.7), (0.3, 1.0))]
    return mix(*clicks, pad(gain(tone(int(0.3 * RATE), 1800, 0.05, rng), 0.2), 0.3))


def capture(rng):
    n = int(2.0 * RATE)
    boom = mix(tone(n, 41, 0.6, rng, 0.0), gain(tone(n, 62, 0.4, rng, 0.0), 0.6))
    hit = [a * b for a, b in zip(lowpass(noise(n, rng), 1500), env(n, 0.002, 0.15))]
    return mix(boom, hit)


def rook(rng):
    n = int(rng.uniform(0.25, 0.4) * RATE)
    out, phase = [], 0.0
    f0 = rng.uniform(380, 480)
    for i in range(n):
        t = i / n
        phase += f0 * (1.0 + 0.3 * t) / RATE
        saw = 2.0 * (phase % 1.0) - 1.0
        out.append(saw * (rng.uniform(0.6, 1.0)) * math.sin(math.pi * t) ** 0.5)
    caw = bandpass(out, 1400, 1.0)
    return mix(caw, pad(gain(bandpass(out, 1100, 1.0), 0.8), 0.45))


def rat(rng):
    out = []
    for k in range(rng.randint(2, 4)):
        n = int(rng.uniform(0.04, 0.08) * RATE)
        f = rng.uniform(3200, 4500)
        chirp = [math.sin(2 * math.pi * f * (1.0 + 0.2 * i / n) * i / RATE) * math.sin(math.pi * i / n) for i in range(n)]
        out = mix(out, pad(chirp, k * rng.uniform(0.08, 0.14))) if out else chirp
    return out


def cat(rng):
    n = int(0.9 * RATE)
    out, phase = [], 0.0
    for i in range(n):
        t = i / n
        f = 520 + 260 * math.sin(math.pi * min(1.0, t * 1.4))
        phase += f / RATE
        v = sum(math.sin(2 * math.pi * h * phase) / h for h in range(1, 6))
        out.append(v * math.sin(math.pi * t) ** 0.7)
    return bandpass(out, 900, 0.8)


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
    write("sfx_breath_loop.wav", loopable(breath_cycle(rng, 8.3, 0.36)), peak=0.5)
    write("sfx_pant_loop.wav", loopable(breath_cycle(rng, 4.3, 1.4)), peak=0.6)
    write("sfx_gasp.wav", gasp(rng))
    write("sfx_heartbeat_loop.wav", heartbeat(rng), peak=0.7)
    write("sfx_ring_loop.wav", ring(), peak=0.25)
    for k in range(3):
        write(f"sfx_hoof_{k}.wav", hoof(rng), peak=0.9)
        write(f"sfx_felt_{k}.wav", felt(rng), peak=0.4)
    write("sfx_hum_loop.wav", hum(rng), peak=0.5)
    write("sfx_rummage.wav", rummage(rng), peak=0.7)
    write("sfx_hide.wav", mix(scrape(rng, 0.6), pad(gain(thud(rng), 0.4), 0.45)), peak=0.6)
    write("sfx_key_turn.wav", key_turn(rng), peak=0.6)
    write("sfx_capture.wav", capture(rng), peak=0.9)
    for k in range(3):
        write(f"sfx_rook_{k}.wav", rook(rng), peak=0.6)
        write(f"sfx_rat_{k}.wav", rat(rng), peak=0.4)
    write("sfx_cat_0.wav", cat(rng), peak=0.5)


if __name__ == "__main__":
    main()
