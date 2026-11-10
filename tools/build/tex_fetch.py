#!/usr/bin/env python3
"""Fetches the CC0 textures the build uses and finishes them for the game.

Every texture comes from Poly Haven (https://polyhaven.com, CC0: any use, no
credit needed). tools/build/textures.json lists them: for each, its Poly
Haven id, the size it is kept at, and how its colour is pulled toward the
game's palette (Look and Feel, "Finishing pass": downscale to 512 or 1024,
desaturate, cool the greys).

For each one this writes, in art/tex/:
    tex_<name>_col.jpg   colour, finished
    tex_<name>_nrm.jpg   normal map (OpenGL: +Y up, as Godot wants)
    tex_<name>_orm.jpg   ambient occlusion, roughness, metal in R, G, B
and a row in art/credits.csv. The files as downloaded are kept in art/_src/
(not in the repository), so a second run only redoes the finishing.

    tools/build/tex_fetch.py            everything in textures.json
    tools/build/tex_fetch.py mud grass  only names containing these words

Needs python3, curl and ffmpeg.
"""
import csv
import json
import os
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SRC = os.path.join(ROOT, "art", "_src", "polyhaven")
OUT = os.path.join(ROOT, "art", "tex")
CREDITS = os.path.join(ROOT, "art", "credits.csv")
AGENT = "the-porter-build/1.0"
MAPS = {"col": "Diffuse", "nrm": "nor_gl", "orm": "arm"}


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)


def download(url, path):
    if os.path.exists(path) and os.path.getsize(path) > 0:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    subprocess.run(["curl", "-sS", "-L", "--fail", "-A", AGENT, "-o", path, url], check=True)


def finish(src, dst, size, kind, look):
    """Scales `src` to `size` and, for colour, pulls it toward the palette."""
    filters = ["scale=%d:%d:flags=lanczos" % (size, size)]
    if kind == "col":
        sat = look.get("saturation", 0.7)
        gain = look.get("gain", 1.0)
        gamma = look.get("gamma", 1.0)
        # Cool the greys a little: less red, more blue in the midtones.
        cool = look.get("cool", 0.04)
        filters.append("eq=saturation=%.3f:gamma=%.3f" % (sat, gamma))
        filters.append("colorbalance=rm=%.3f:bm=%.3f" % (-cool, cool))
        filters.append("lutrgb=r='clip(val*%.3f,0,255)':g='clip(val*%.3f,0,255)':b='clip(val*%.3f,0,255)'"
                       % ((gain,) * 3))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", src, "-vf", ",".join(filters),
                    "-q:v", "3", dst], check=True)


def credit(rows, path, ph_id, authors):
    rel = os.path.relpath(path, ROOT)
    rows[rel] = [rel, "https://polyhaven.com/a/" + ph_id, "; ".join(sorted(authors)), "CC0 1.0",
                 "no"]


def main():
    words = sys.argv[1:]
    with open(os.path.join(os.path.dirname(__file__), "textures.json")) as f:
        wanted = json.load(f)
    with open(CREDITS, newline="") as f:
        table = list(csv.reader(f))
    header, rows = table[0], {r[0]: r for r in table[1:] if r}
    os.makedirs(OUT, exist_ok=True)
    for name, spec in wanted.items():
        if words and not any(w in name for w in words):
            continue
        ph_id = spec["polyhaven"]
        size = spec.get("size", 1024)
        files = get_json("https://api.polyhaven.com/files/" + ph_id)
        info = get_json("https://api.polyhaven.com/info/" + ph_id)
        for kind, ph_map in MAPS.items():
            if kind in spec.get("skip", []):
                continue
            entry = files[ph_map]["2k" if size > 1024 else "1k"]
            fmt = "jpg" if "jpg" in entry else "png"
            raw = os.path.join(SRC, "%s_%s.%s" % (ph_id, kind, fmt))
            download(entry[fmt]["url"], raw)
            dst = os.path.join(OUT, "tex_%s_%s.jpg" % (name, kind))
            finish(raw, dst, size if kind != "orm" else max(size // 2, 256), kind, spec)
            credit(rows, dst, ph_id, info.get("authors", {}).keys())
        print("finished", name, "(%s, %d px)" % (ph_id, size))
    with open(CREDITS, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        for key in sorted(rows, key=lambda k: (not k.startswith("art/fonts"), k)):
            w.writerow(rows[key])


if __name__ == "__main__":
    main()
