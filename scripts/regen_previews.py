#!/usr/bin/env python3
"""
Regenerate preview images for HHC and CAA collections.

Downloads each master TIF from R2, resizes to 2000px on the longest side
at 82% JPEG quality, uploads back as _prev.jpg replacing the existing preview.

Options:
  --dry-run              Print what would be done; no downloads or uploads
  --collection hhc|caa   Process one collection only (default: both)

Example:
  python3 scripts/regen_previews.py --dry-run
  python3 scripts/regen_previews.py --collection caa
  python3 scripts/regen_previews.py
"""

import subprocess, os, sys, tempfile, shutil

DRY_RUN    = "--dry-run" in sys.argv
THUMB_MODE = "--thumb" in sys.argv
COLLECTION = next((a for a in sys.argv[1:] if a in ("hhc", "caa")), None)

R2 = "hh-r2:hunter-house-archive"
COLLECTIONS = {
    "hhc": {
        "masters":  f"{R2}/hunter-house-collection/masters",
        "previews": f"{R2}/hunter-house-collection/previews",
        "thumbs":   f"{R2}/hunter-house-collection/thumbs",
    },
    "caa": {
        "masters":  f"{R2}/canadian-architecture-archive/masters",
        "previews": f"{R2}/canadian-architecture-archive/previews",
        "thumbs":   f"{R2}/canadian-architecture-archive/thumbs",
    },
}

if THUMB_MODE:
    SIZE    = 600  # px on longest side
    QUALITY = 75   # JPEG quality
    SUFFIX  = "_thumb.jpg"
    DEST_KEY = "thumbs"
else:
    SIZE    = 2000  # px on longest side
    QUALITY = 82    # JPEG quality
    SUFFIX  = "_prev.jpg"
    DEST_KEY = "previews"


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True)


def list_masters(path):
    result = run(["rclone", "lsf", path])
    return [f.strip() for f in result.stdout.decode().splitlines()
            if f.strip().endswith(".tif")]


def process(name, paths, tmpdir):
    masters = list_masters(paths["masters"])
    print(f"\n{name.upper()}: {len(masters)} masters")
    ok = err = 0

    for master in masters:
        base      = master[:-4]              # strip .tif
        outname   = f"{base}{SUFFIX}"
        local_tif = os.path.join(tmpdir, master)
        local_jpg = os.path.join(tmpdir, outname)

        print(f"  {base}", end="", flush=True)

        if DRY_RUN:
            print(f"  →  {outname}  (dry run)")
            ok += 1
            continue

        try:
            run(["rclone", "copy", f"{paths['masters']}/{master}", tmpdir])
            print(" ↓", end="", flush=True)

            run(["sips", "-Z", str(SIZE),
                 "-s", "format", "jpeg",
                 "-s", "formatOptions", str(QUALITY),
                 local_tif, "--out", local_jpg])

            kb = os.path.getsize(local_jpg) // 1024
            print(f" → {kb}KB", end="", flush=True)

            run(["rclone", "copy", local_jpg, paths[DEST_KEY]])
            print(" ↑ done")
            ok += 1

        except Exception as e:
            print(f"  ERROR: {e}")
            err += 1
        finally:
            for f in (local_tif, local_jpg):
                if os.path.exists(f):
                    os.remove(f)


    return ok, err


def main():
    targets = {COLLECTION: COLLECTIONS[COLLECTION]} if COLLECTION else COLLECTIONS
    tmpdir  = tempfile.mkdtemp(prefix="hh_prev_")

    mode = "THUMB (600px/75%)" if THUMB_MODE else "PREVIEW (2000px/82%)"
    print(f"Mode: {mode}")
    print(f"Target: {SIZE}px longest side, {QUALITY}% JPEG quality → {SUFFIX}")
    print(f"Collections: {', '.join(targets).upper()}")
    if DRY_RUN:
        print("DRY RUN — no changes will be made")

    total_ok = total_err = 0
    try:
        for name, paths in targets.items():
            ok, err = process(name, paths, tmpdir)
            total_ok += ok
            total_err += err
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

    print(f"\nDone.  OK: {total_ok}   Errors: {total_err}")


main()
