"""Night 0's recorded sounds (docs/systems/assets.md, "Sounds"): fetches each
Freesound CC0 recording below into art/_src/sfx/ (not committed), then cuts,
filters, loops and levels them into art/sfx/. Every source is in
art/credits.csv; sfx_placeholders.py leaves these files alone.

Needs numpy and ffmpeg; Blender's own Python has numpy:
  /Applications/Blender.app/Contents/Resources/5.2/python/bin/python3.13 -I tools/build/sfx_recorded.py [rain dog ...]
With names, only those are made. Downloads are untrusted data: they stay in
art/_src/sfx/, and nothing there is run.
"""
import json
import os
import re
import subprocess
import sys
import urllib.request
import wave

import numpy as np

UA = {"User-Agent": "Mozilla/5.0"}
## Each download: its name here -> (Freesound id, its author).
SOURCES = {
    "bell": (73678, "daytripper"),
    "buckboard": (437077, "craigsmith"),
    "cat": (412017, "skymary"),
    "cry_c": (221544, "joseppujol"),
    "dog_b": (522921, "Sheyvan"),
    "door_b": (402465, "LampEight"),
    "drag_a": (507473, "Wallch503"),
    "fall_a": (504626, "leonelmail"),
    "fire": (414767, "samarobryn"),
    "hooves_cobble": (437103, "craigsmith"),
    "knock": (119833, "kbnevel"),
    "lantern": (637099, "jamesdrake89"),
    "oxcart": (437078, "craigsmith"),
    "rain": (81731, "silencyo"),
    "rain_tiles": (669487, "xkeril"),
    "rat_b": (728086, "macohibs"),
    "rook_a": (556221, "Walking.With.Microphones"),
    "rook_b": (556223, "Walking.With.Microphones"),
    "shut_a": (524800, "SamuelGremaud"),
    "shut_b": (524801, "SamuelGremaud"),
    "step_grass": (521587, "Fission9"),
    "step_mud": (548384, "Nox_Sound"),
    "step_stone": (521590, "Fission9"),
    "step_wood": (485421, "IENBA"),
    "wagon_dirt": (137843, "thefilmbakery"),
    "walla_a": (675072, "craigsmith"),
    "walla_b": (438431, "craigsmith"),
    "wind_a": (719095, "lakewoodsound"),
    "wind_b": (567356, "TRP"),
}

FF = "/opt/homebrew/bin/ffmpeg"
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DL = os.path.join(ROOT, "art", "_src", "sfx")
OUT = os.path.join(ROOT, "art", "sfx")
ONLY = [a for a in sys.argv[1:] if not a.startswith("-")]


def src(name):
    return os.path.join(DL, name, "%d.ogg" % SOURCES[name][0])


def fetch():
    """Downloads each source's HQ preview into art/_src/sfx/<name>/ unless it
    is there, after checking its page still says Creative Commons 0."""
    for name, (sid, user) in SOURCES.items():
        path = src(name)
        if os.path.exists(path):
            continue
        os.makedirs(os.path.dirname(path), exist_ok=True)
        page_url = "https://freesound.org/people/%s/sounds/%d/" % (user, sid)
        page = urllib.request.urlopen(urllib.request.Request(page_url, headers=UA), timeout=60).read().decode("utf-8", "ignore")
        if "Creative Commons 0" not in page:
            sys.exit("%s (%s) is not CC0 any more: pick another" % (name, page_url))
        found = re.search(r"https://cdn\.freesound\.org/previews/\d+/%d_\d+-[hl]q\.ogg" % sid, page)
        if not found:
            sys.exit("no preview found on " + page_url)
        url = found.group(0).replace("-lq.ogg", "-hq.ogg")
        print("fetch", name, url)
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=300) as r, open(path, "wb") as f:
            f.write(r.read())


def dec(name, start=0.0, dur=None, af="", rate=22050, ch=1):
    """Decode a slice to float32 (n, ch), through an ffmpeg filter chain."""
    cmd = [FF, "-v", "error", "-ss", str(start)]
    if dur:
        cmd += ["-t", str(dur)]
    cmd += ["-i", src(name)]
    if af:
        cmd += ["-af", af]
    cmd += ["-ac", str(ch), "-ar", str(rate), "-f", "f32le", "-"]
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, ch).copy()


def filt(x, af, rate):
    """Run an array through an ffmpeg filter chain."""
    ch = x.shape[1]
    cmd = [FF, "-v", "error", "-f", "f32le", "-ar", str(rate), "-ac", str(ch), "-i", "-",
           "-af", af, "-f", "f32le", "-ar", str(rate), "-ac", str(ch), "-"]
    raw = subprocess.run(cmd, input=x.astype(np.float32).tobytes(), capture_output=True, check=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, ch).copy()


def lufs(x, rate):
    ch = x.shape[1]
    cmd = [FF, "-nostats", "-f", "f32le", "-ar", str(rate), "-ac", str(ch), "-i", "-",
           "-af", "ebur128", "-f", "null", "-"]
    err = subprocess.run(cmd, input=x.astype(np.float32).tobytes(), capture_output=True).stderr.decode()
    lines = [l for l in err.splitlines() if l.strip().startswith("I:")]
    return float(lines[-1].split()[1]) if lines else None


def db(v):
    return 10 ** (v / 20.0)


def peak_db(x):
    return 20 * np.log10(max(1e-9, float(np.max(np.abs(x)))))


def to_lufs(x, rate, target, ceiling=-1.0):
    """Gain to `target` LUFS; peaks above `ceiling` are limited softly."""
    now = lufs(x, rate)
    x = x * db(target - now)
    if peak_db(x) > ceiling:
        x = filt(x, f"alimiter=limit={db(ceiling):.4f}:attack=5:release=80:level=false", rate)
    return x


def to_peak(x, target):
    return x * db(target - peak_db(x))


def fade(x, rate, fin=0.0, fout=0.0):
    x = x.copy()
    a, b = int(fin * rate), int(fout * rate)
    if a:
        x[:a] *= np.linspace(0, 1, a)[:, None] ** 2
    if b:
        x[-b:] *= np.linspace(1, 0, b)[:, None] ** 2
    return x


def loop(x, rate, length, xf):
    """`length` s that loop seamlessly: the tail crossfades (equal power)
    into the material just before the loop's start."""
    n, f = int(length * rate), int(xf * rate)
    assert len(x) >= n + f, (len(x) / rate, length + xf)
    s = x[:n + f]
    out = s[f:n + f].copy()
    t = np.linspace(0, 1, f)[:, None]
    out[-f:] = s[n:n + f] * np.cos(t * np.pi / 2) + s[:f] * np.sin(t * np.pi / 2)
    return out


def mix(*parts):
    """parts: (array, offset seconds, rate) -> summed."""
    rate = parts[0][2]
    n = max(int(o * rate) + len(a) for a, o, _ in parts)
    out = np.zeros((n, parts[0][0].shape[1]), dtype=np.float32)
    for a, o, _ in parts:
        i = int(o * rate)
        out[i:i + len(a)] += a
    return out


def add(*xs):
    n = min(len(x) for x in xs)
    return sum(x[:n] for x in xs)


def write(name, x, rate):
    x = np.clip(x, -1.0, 1.0)
    path = os.path.join(OUT, name)
    with wave.open(path, "wb") as w:
        w.setnchannels(x.shape[1])
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes((x * 32767).astype("<i2").tobytes())
    info = {"file": name, "s": round(len(x) / rate, 2), "rate": rate, "ch": x.shape[1],
            "peak": round(peak_db(x), 1), "lufs": lufs(x, rate) if len(x) > rate else None,
            "kb": os.path.getsize(path) // 1024}
    print(json.dumps(info))


MADE = {}


def made(fn):
    MADE[fn.__name__] = fn
    return fn


# Ambience beds ------------------------------------------------------------

@made
def rain():
    r = 22050
    court = dec("rain", 30.0, 30.0, "highpass=f=120", r, 2)       # 81731: village courtyard, stone
    tiles = dec("rain_tiles", 6.0, 30.0, "highpass=f=180", r, 2)  # 669487: rain on roof tiles
    court = to_lufs(court, r, -23.0, -3.0)
    tiles = to_lufs(tiles, r, -25.0, -3.0)
    bed = add(court, tiles)
    write("amb_rain_loop.wav", to_lufs(loop(bed, r, 24.0, 3.0), r, -21.0), r)


@made
def wagon():
    r = 22050
    horse = dec("wagon_dirt", 8.5, 29.0, "highpass=f=90,lowpass=f=9000", r)  # 137843: horse and carriage, dirt
    cart = dec("oxcart", 6.0, 29.0, "highpass=f=60", r)                       # 437078: wooden wheels, creak
    horse = to_lufs(horse, r, -22.0, -3.0)
    cart = to_lufs(cart, r, -28.0, -3.0)
    write("amb_wagon_loop.wav", to_lufs(loop(add(horse, cart), r, 26.0, 2.5), r, -21.0), r)


@made
def wagon_cobbles():
    r = 22050
    hooves = dec("hooves_cobble", 16.0, 29.0, "highpass=f=90", r)  # 437103: horse walking on cobbles
    rattle = dec("buckboard", 5.0, 29.0, "highpass=f=70", r)       # 437077: wagon on hard ground
    hooves = to_lufs(hooves, r, -22.0, -3.0)
    rattle = to_lufs(rattle, r, -26.0, -3.0)
    write("amb_wagon_cobbles_loop.wav", to_lufs(loop(add(hooves, rattle), r, 26.0, 2.5), r, -21.0), r)


@made
def taproom():
    r = 22050
    room = dec("walla_a", 0.0, 25.4, "highpass=f=100", r)                   # 675072: group walla, no words
    more = dec("walla_b", 1.0, 16.0, "highpass=f=100,lowpass=f=3500", r)    # 438431: indoor walla, no words
    room = to_lufs(room, r, -23.0, -3.0)
    more = fade(to_lufs(more, r, -29.0, -3.0), r, 2.0, 2.0)
    bed = mix((room, 0.0, r), (more, 4.0, r))[:len(room)]
    write("amb_taproom_loop.wav", to_lufs(loop(bed, r, 23.0, 2.2), r, -22.0), r)


@made
def fire():
    r = 44100
    # 414767: fire in a fireplace; the crackles squeezed a little so the bed
    # under them carries.
    x = dec("fire", 8.0, 24.0, "highpass=f=60,acompressor=threshold=0.06:ratio=3:attack=2:release=60", r)
    write("amb_fire_loop.wav", to_lufs(loop(x, r, 21.0, 2.0), r, -24.0, -2.0), r)


@made
def wind():
    r = 22050
    roar = dec("wind_a", 2.0, 27.0, "highpass=f=35", r, 2)   # 719095: high wind in bare trees
    moan = dec("wind_b", 21.0, 27.0, "highpass=f=60", r, 2)  # 567356: cold gusts moaning at a window
    roar = to_lufs(roar, r, -22.0, -3.0)
    moan = to_lufs(moan, r, -24.0, -3.0)
    write("amb_wind_night.wav", to_lufs(loop(add(roar, moan), r, 24.0, 2.5), r, -20.0), r)


# One-shots ----------------------------------------------------------------

@made
def bell():
    r = 44100
    x = dec("bell", 0.0, 7.85, "highpass=f=40", r)  # 73678: a very large bell struck once
    write("sfx_bell.wav", to_peak(fade(x, r, 0.0, 1.6), -1.0), r)


@made
def dog():
    r = 22050
    # 522921: a big dog barking; muffled as if behind a door and a wall.
    x = dec("dog_b", 0.0, 3.17, "highpass=f=120,lowpass=f=1400,lowpass=f=2200,"
            "aecho=0.8:0.6:18|41:0.35|0.2", r)
    write("sfx_dog.wav", to_peak(fade(x, r, 0.0, 0.25), -2.0), r)


@made
def shutters():
    r = 22050
    near = dec("shut_b", 6.70, 0.95, "highpass=f=70", r)                    # 524801: shutters banged closed
    mid = dec("shut_b", 9.20, 1.70, "highpass=f=70,lowpass=f=4500", r)
    far = dec("shut_a", 10.95, 1.55, "highpass=f=90,lowpass=f=2600", r)     # 524800
    near = to_peak(fade(near, r, 0.005, 0.15), -1.5)
    mid = to_peak(fade(mid, r, 0.005, 0.2), -5.0)
    far = to_peak(fade(far, r, 0.005, 0.25), -10.0)
    x = mix((near, 0.0, r), (mid, 0.9, r), (far, 2.3, r))
    write("sfx_shutters.wav", to_peak(x, -1.5), r)


@made
def cry():
    r = 22050
    # 221544: a wounded man's scream, cut off 0.65 s in; a little of the court
    # given back after it.
    x = dec("cry_c", 0.30, 0.66, "highpass=f=180,lowpass=f=5500", r)
    x = fade(x, r, 0.01, 0.025)
    x = np.concatenate([x, np.zeros((int(0.5 * r), 1), np.float32)])
    x = filt(x, "aecho=0.85:0.55:38|95|160:0.32|0.2|0.1", r)
    write("sfx_cry.wav", to_peak(fade(x, r, 0.0, 0.2), -1.5), r)


@made
def body_fall():
    r = 22050
    x = dec("fall_a", 0.0, 1.45, "highpass=f=50,lowpass=f=7000", r)  # 504626: heavy body fall, dirt
    write("sfx_body_fall.wav", to_peak(fade(x, r, 0.0, 0.3), -2.0), r)


@made
def lantern_drop():
    r = 22050
    x = dec("lantern", 0.15, 1.45, "highpass=f=80", r)  # 637099: lantern dropped
    write("sfx_lantern_drop.wav", to_peak(fade(x, r, 0.0, 0.3), -3.0), r)


@made
def drag():
    r = 22050
    # 507473: a body dragged (cloth on the ground) and the slow steps of
    # whoever drags it.
    x = dec("drag_a", 2.4, 9.2, "highpass=f=70,acompressor=threshold=0.03:ratio=4:attack=4:release=120", r)
    write("sfx_drag.wav", to_peak(fade(x, r, 0.3, 0.8), -3.0), r)


@made
def knock():
    r = 22050
    x = dec("knock", 0.22, 2.2, "highpass=f=45", r)  # 119833: knocking on a heavy wooden door
    write("sfx_knock.wav", to_lufs(fade(x, r, 0.0, 0.3), r, -21.5, -1.0), r)


@made
def doors():
    r = 44100
    # 402465: a heavy wooden door opened, then swinging shut on its own.
    o = dec("door_b", 0.0, 1.3, "highpass=f=50", r)
    c = dec("door_b", 2.72, 1.05, "highpass=f=50", r)
    write("sfx_door_open.wav", to_lufs(fade(o, r, 0.0, 0.25), r, -21.0, -1.5), r)
    write("sfx_door_close.wav", to_lufs(fade(c, r, 0.02, 0.3), r, -20.5, -1.0), r)


@made
def steps():
    r = 44100
    sets = {
        "stone": ("step_stone", [0.10, 0.70, 1.26, 2.41], 0.36, -3.0),   # 521590: boots on stone
        "wood": ("step_wood", [0.85, 4.08, 10.23, 13.31], 0.42, -3.0),   # 485421: boots on a wood floor
        "mud": ("step_mud", [10.90, 12.14, 13.12, 7.74], 0.42, -5.0),    # 548384: boots in mud
        "grass": ("step_grass", [0.10, 0.81, 2.29, 3.06], 0.36, -5.0),   # 521587: boots on grass
    }
    for surface, (name, at, length, pk) in sets.items():
        clips = [dec(name, max(0.0, t - 0.02), length, "highpass=f=60", r) for t in at]
        # Each to `pk`, less a little so the four differ the way steps do.
        for k, c in enumerate(clips):
            write(f"sfx_step_{surface}_{k}.wav", fade(to_peak(c, pk - (0.0, 1.0, 0.5, 1.5)[k]), r, 0.003, 0.12), r)


@made
def rooks():
    r = 22050
    cuts = [("rook_a", 0.20, 1.10), ("rook_a", 2.10, 1.85), ("rook_b", 2.35, 0.90)]  # 556221, 556223
    for k, (name, t, d) in enumerate(cuts):
        x = dec(name, t, d, "highpass=f=300", r)
        write(f"sfx_rook_{k}.wav", to_peak(fade(x, r, 0.01, 0.15), -5.0), r)


@made
def rats():
    r = 44100
    cuts = [(5.95, 0.38), (6.35, 0.65), (7.85, 0.65)]  # 728086: a rat squeaking
    for k, (t, d) in enumerate(cuts):
        x = dec("rat_b", t, d, "highpass=f=1500", r)
        write(f"sfx_rat_{k}.wav", to_peak(fade(x, r, 0.01, 0.08), -8.0), r)


@made
def cat():
    r = 44100
    x = dec("cat", 0.0, 1.72, "highpass=f=120", r)  # 412017: a cat meowing
    write("sfx_cat_0.wav", to_peak(fade(x, r, 0.0, 0.15), -4.0), r)


if __name__ == "__main__":
    fetch()
    os.makedirs(OUT, exist_ok=True)
    for name, fn in MADE.items():
        if not ONLY or name in ONLY:
            fn()
