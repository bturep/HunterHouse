#!/usr/bin/env python3
"""
Regenerate PWA icons with iOS-style grey gradient background.
Source: assets/icon-512.png (dark bg, white artwork)
Output: same files with grey gradient bg, dark artwork.
"""
from PIL import Image, ImageDraw
import numpy as np
import os

ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
SRC = os.path.join(ASSETS, "icon-512.png")

# Grey gradient: top slightly lighter, bottom slightly darker
# Approximates iOS system icon aesthetic
TOP_GREY = (172, 172, 176)    # #ACACB0
BOT_GREY = (154, 154, 158)    # #9A9A9E
INK     = (26, 24, 22)        # #1A1816 — matches site ink

def make_icon(size):
    src = Image.open(SRC).convert("RGBA").resize((size, size), Image.LANCZOS)

    # Build grey gradient background
    bg = Image.new("RGBA", (size, size))
    pixels = np.zeros((size, size, 4), dtype=np.uint8)
    for y in range(size):
        t = y / (size - 1)
        r = int(TOP_GREY[0] + t * (BOT_GREY[0] - TOP_GREY[0]))
        g = int(TOP_GREY[1] + t * (BOT_GREY[1] - TOP_GREY[1]))
        b = int(TOP_GREY[2] + t * (BOT_GREY[2] - TOP_GREY[2]))
        pixels[y, :] = [r, g, b, 255]
    bg = Image.fromarray(pixels, "RGBA")

    # Extract artwork: treat brightness of source as mask for ink overlay
    # White areas in source → dark ink on output
    src_arr = np.array(src).astype(np.float32)
    # Luminance (0=black, 1=white in source)
    lum = (src_arr[:,:,0]*0.299 + src_arr[:,:,1]*0.587 + src_arr[:,:,2]*0.114) / 255.0

    # Build ink layer: where source is white, paint INK
    ink_arr = np.zeros((size, size, 4), dtype=np.uint8)
    ink_arr[:,:,0] = INK[0]
    ink_arr[:,:,1] = INK[1]
    ink_arr[:,:,2] = INK[2]
    ink_arr[:,:,3] = (lum * 255).astype(np.uint8)  # alpha = luminance

    ink_layer = Image.fromarray(ink_arr, "RGBA")
    result = Image.alpha_composite(bg, ink_layer)
    return result

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
