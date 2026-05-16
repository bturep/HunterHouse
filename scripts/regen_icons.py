#!/usr/bin/env python3
"""
Regenerate PWA icons: dark background, dim warm-cream lettermark.
Source: /tmp/icon-512-dark.png (original dark bg, white artwork from git)
"""
from PIL import Image
import numpy as np
import os

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
SRC = "/tmp/icon-512-dark.png"   # original dark-bg version from git history

BG      = (6, 5, 4)              # #060504 — near-black
MARK    = (184, 180, 172)        # #B8B4AC — dim warm cream, ~72% brightness

def make_icon(size):
    src = Image.open(SRC).convert("RGBA").resize((size, size), Image.LANCZOS)

    # Solid dark background
    bg_arr = np.full((size, size, 4), [BG[0], BG[1], BG[2], 255], dtype=np.uint8)
    bg = Image.fromarray(bg_arr, "RGBA")

    # Source has white lettermark on dark bg.
    # Use luminance as alpha to paint MARK colour where original was white.
    src_arr = np.array(src).astype(np.float32)
    lum = (src_arr[:,:,0]*0.299 + src_arr[:,:,1]*0.587 + src_arr[:,:,2]*0.114) / 255.0

    mark_arr = np.zeros((size, size, 4), dtype=np.uint8)
    mark_arr[:,:,0] = MARK[0]
    mark_arr[:,:,1] = MARK[1]
    mark_arr[:,:,2] = MARK[2]
    mark_arr[:,:,3] = (lum * 255).astype(np.uint8)

    mark_layer = Image.fromarray(mark_arr, "RGBA")
    return Image.alpha_composite(bg, mark_layer)

SIZES = {
    "icon-512.png": 512,
    "icon-192.png": 192,
    "icon-180.png": 180,
}

for fname, size in SIZES.items():
    out_path = os.path.join(ASSETS, fname)
    img = make_icon(size)
    img.save(out_path, "PNG", optimize=True)
    print(f"  wrote {fname} ({size}px)")

print("Done.")
