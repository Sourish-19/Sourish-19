"""Turn source-prepped.png into data/portrait.txt (ASCII rows for the hero card).

Run locally when the photo changes; CI only reads the text file, so it
doesn't need numpy/Pillow.

    python scripts/make_portrait.py [source-prepped.png]
"""
import sys

import numpy as np
from PIL import Image, ImageOps

RAMP = " .'`:-=+*cs#%@"   # light -> dark, so ink on paper reads as shading
COLS = 92
ROWS = 62
CROP = (80, 165, 520, 625)  # head and shoulders of the 576x1024 photo


def main(src="source-prepped.png", out="data/portrait.txt"):
    img = Image.open(src).convert("L").crop(CROP)
    img = ImageOps.autocontrast(img, cutoff=1)
    img = img.resize((COLS, ROWS), Image.Resampling.LANCZOS)
    a = np.asarray(img, dtype=float) / 255.0

    # Vignette: fade the busy background towards paper (white) at the edges
    yy, xx = np.mgrid[0:ROWS, 0:COLS]
    cx, cy = COLS * 0.5, ROWS * 0.47
    d = np.sqrt(((xx - cx) / (COLS * 0.55)) ** 2 + ((yy - cy) / (ROWS * 0.62)) ** 2)
    fade = np.clip((d - 0.5) / 0.32, 0, 1) ** 1.1
    a = a ** 1.2           # deepen mid-tones so skin shades in instead of vanishing
    a = a * (1 - fade) + fade

    idx = ((1 - a) * (len(RAMP) - 1)).round().astype(int)
    rows = ["".join(RAMP[i] for i in r).rstrip() for r in idx]
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(rows) + "\n")
    print(f"wrote {out} ({ROWS} rows x {COLS} cols)")


if __name__ == "__main__":
    main(*sys.argv[1:2])
