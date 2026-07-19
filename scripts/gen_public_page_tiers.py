#!/usr/bin/env python3
"""
Generate per-page JPEG tiers for the PUBLIC multi-page objects so browse.html's
page pager (item.pages[]) can flip them like the gated letters — 2026-07-19.

Per page N (1-based, reading order):
  {aid}_{slug}_pNN_{thumb,prev,large}.jpg  →  R2 thumbs/ previews/ large/
The browser derives these from P96 by inserting _pNN before _prev.jpg, and
loads them in <img> (browsers honour the JPEG's EXIF orientation → upright).

ORIENTATION FIX: DOC-03 pages 1-2 carry EXIF orientation=6 (landscape scanned
as portrait). sips + browsers honour it, but Pillow's PDF encoder does NOT — so
the ingest's access PDF came out sideways (the "rotate 90° CCW" report). Fix:
rebuild each access PDF with ImageOps.exif_transpose() baking the orientation.
No pixel rotation of the tiers (they're already upright in-browser).

sRGB baked (cyan-cast rule); NEVER upscale (EGC lesson).
DRY RUN default (renders a rebuilt PDF page to Desktop). --execute to write.
"""
import os
import shutil
import subprocess
import sys

from PIL import Image, ImageOps

FH = os.path.expanduser("~/Desktop/Frances Hunter Archive")
SB = f"{FH}/Letters/ASketchbooks"
ICC = "/System/Library/ColorSync/Profiles/sRGB Profile.icc"
R2 = "hh-r2:hunter-house-archive"
CDIR = "frances-hunter-collection"
PUBLIC_BASE = "https://archive.hunterhousefoundation.com"
TIERS = {"_thumb.jpg": ("thumbs", 600, 75), "_prev.jpg": ("previews", 2000, 82),
         "_large.jpg": ("large", 3840, 85)}
PDF_Q = 80

ITEMS = [
    dict(aid="HH-FRH-DOC-03", slug="UVicSonicLabConcertProgram_1986-11-14",
         sources=[f"{FH}/May25_2026/FH_2026-05-25{n}.tif" for n in ("11", "12", "13", "14")],
         rebuild_pdf=True),
    dict(aid="HH-FRH-SKB-01", slug="Arguments_2015-2022",
         sources=[f"{SB}/Sketchbook_Arguments001.tif",
                  f"{SB}/Sketchbook_Arguments002.tif",
                  f"{SB}/Sketchbook_Arguments003-2.tif"],
         rebuild_pdf=False),   # pages all upright (o=1) — existing PDF fine
    dict(aid="HH-FRH-SKB-02", slug="Sketchbook_2022",
         sources=[f"{SB}/Sketchbook2_Arguments001.tif",
                  f"{SB}/Sketchbook2_Arguments003.tif",   # crayon arches
                  f"{SB}/Sketchbook2_Arguments002.tif"],  # ink maze — last drawing
         rebuild_pdf=False),   # pages all upright (o=1) — existing PDF fine
]

EXECUTE = "--execute" in sys.argv
PURGE_URLS = []


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def dims(p):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", p],
                         capture_output=True, text=True).stdout
    w = h = None
    for ln in out.splitlines():
        if "pixelWidth" in ln:
            w = int(ln.split()[-1])
        if "pixelHeight" in ln:
            h = int(ln.split()[-1])
    return w, h


def sips_jpeg(src, dst, max_px, quality):
    w, h = dims(src)
    args = ["sips", "-m", ICC, "-s", "format", "jpeg",
            "-s", "formatOptions", str(quality)]
    if max(w, h) > max_px:
        args += ["-Z", str(max_px)]
    run(args + [src, "--out", dst], capture_output=True)


def upload(local, key):
    if key.endswith(".pdf"):
        run(["rclone", "copyto", local, f"{R2}/{key}",
             "--header-upload", "Content-Disposition: attachment"])
    else:
        run(["rclone", "copyto", local, f"{R2}/{key}"])


def main():
    for it in ITEMS:
        for p in it["sources"]:
            if not os.path.isfile(p):
                raise SystemExit(f"source missing: {p}")

    print(f"{'EXECUTE' if EXECUTE else 'DRY RUN'} — {len(ITEMS)} multi-page items\n")

    for it in ITEMS:
        aid, slug = it["aid"], it["slug"]
        n = len(it["sources"])
        work = f"/tmp/hh_pagetiers_{aid}"
        shutil.rmtree(work, ignore_errors=True)
        os.makedirs(work)
        print(f"── {aid}  ({n} pages)")

        page_prev = {}  # page# -> 2000px sips jpeg (feeds the PDF)
        for i, src in enumerate(it["sources"], 1):
            for suffix, (sub, px, q) in TIERS.items():
                out = os.path.join(work, f"{aid}_{slug}_p{i:02d}{suffix}")
                sips_jpeg(src, out, px, q)
                if suffix == "_prev.jpg":
                    page_prev[i] = out
                if EXECUTE:
                    upload(out, f"{CDIR}/{sub}/{aid}_{slug}_p{i:02d}{suffix}")
        print(f"   per-page tiers: {n}×3 {'uploaded' if EXECUTE else 'planned'}")

        # access PDF — rebuild with EXIF orientation baked (Pillow ignores the tag)
        if it["rebuild_pdf"]:
            imgs, oriented = [], []
            for i in range(1, n + 1):
                im = Image.open(page_prev[i])
                o = im.getexif().get(274)
                imgs.append(ImageOps.exif_transpose(im).convert("RGB"))
                if o not in (None, 1):
                    oriented.append(f"p{i}(o={o})")
            pdf = os.path.join(work, f"{aid}_{slug}.pdf")
            imgs[0].save(pdf, "PDF", save_all=True, append_images=imgs[1:],
                         resolution=150.0, quality=PDF_Q)
            note = f"  [re-oriented {', '.join(oriented)}]" if oriented else "  [all upright]"
            print(f"   PDF rebuilt: {os.path.getsize(pdf)/1e6:.1f} MB{note}")
            key = f"{CDIR}/pdf/{aid}_{slug}.pdf"
            if EXECUTE:
                upload(pdf, key)
                PURGE_URLS.append(f"{PUBLIC_BASE}/{key}")
            else:
                # render page 1 to Desktop for eyeball
                try:
                    d = os.path.expanduser(f"~/Desktop/{aid}_PDF-page1_PREVIEW.jpg")
                    run(["pdftoppm", "-jpeg", "-r", "60", "-f", "1", "-l", "1",
                         pdf, os.path.join(work, "pv")], capture_output=True)
                    shutil.copyfile(os.path.join(work, "pv-1.jpg"), d)
                    print(f"   PDF p1 preview → {d}")
                except Exception as e:
                    print(f"   (preview skipped: {e})")
        print()

    if EXECUTE and PURGE_URLS:
        print(f"CF-purging {len(PURGE_URLS)} overwritten PDF URL(s)…")
        try:
            run([sys.executable, "scripts/cf_purge.py", *PURGE_URLS])
        except Exception as e:
            print(f"  ⚠ purge failed (non-fatal): {e}")

    print("done.")


if __name__ == "__main__":
    main()
