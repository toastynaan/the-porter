"""A face in the wood grain (placeholder texture, no licence): two hollow
eyes, a long nose and an open mouth, faint and dark, on transparent, for the
drug's "faces in the wood grain" (game/drug/hallucinations.gd).
Writes art/tex/tex_face_grain.png. Run: python3 tools/build/tex_face_grain.py
"""

import math
import os
import random

from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(__file__), "..", "..", "art", "tex", "tex_face_grain.png")
SIZE = 128


def main():
    rng = random.Random(7)
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ink = (24, 14, 8)
    # Grain lines that bend round the face.
    for k in range(18):
        y0 = 6 + k * 7
        pts = [(x, y0 + 4 * math.sin(x / 13.0 + k) + (10 if 30 < x < 98 and 30 < y0 < 100 else 0) * math.sin((x - 30) / 68 * math.pi)) for x in range(0, SIZE, 4)]
        d.line(pts, fill=ink + (60,), width=1)
    # The face.
    d.ellipse((38, 40, 56, 60), fill=ink + (170,))
    d.ellipse((72, 40, 90, 60), fill=ink + (170,))
    d.line([(64, 52), (62, 76), (67, 80)], fill=ink + (120,), width=3)
    d.ellipse((52, 88, 76, 104), fill=ink + (190,))
    img = img.filter(ImageFilter.GaussianBlur(1.6))
    # Fade to nothing at the edges.
    px = img.load()
    for y in range(SIZE):
        for x in range(SIZE):
            r, g, b, a = px[x, y]
            dist = math.hypot(x - SIZE / 2, y - SIZE / 2) / (SIZE / 2)
            px[x, y] = (r, g, b, int(a * max(0.0, 1.0 - dist ** 3)))
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    img.save(OUT)
    print("wrote", os.path.normpath(OUT))


if __name__ == "__main__":
    main()
