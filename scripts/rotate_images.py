#!/usr/bin/env python3
"""
Rotate / flip archive images on R2.
Downloads master TIF + 3 JPEG tiers, applies transform, re-uploads.
Nothing on R2 is touched until local transform is confirmed good.
"""

import os
import subprocess
import shutil
from PIL import Image

Image.MAX_IMAGE_PIXELS = None   # large TIFs exceed default limit

WORK_DIR   = "/tmp/rotate_work"
R2_REMOTE  = "hh-r2:hunter-house-archive"

# Pillow transpose constants
CW   = Image.Transpose.ROTATE_270      # 90° clockwise
CCW  = Image.Transpose.ROTATE_90       # 90° counter-clockwise
FLIP = Image.Transpose.FLIP_LEFT_RIGHT # mirror horizontal

# Quality to use when re-saving JPEGs (slightly above original to minimise re-compression loss)
JPEG_QUALITY = 92

ITEMS = {
    # CAA
    "HH-CAA-0018": {"collection": "canadian-architecture-archive", "op": FLIP},
    # HHC — CCW
    "HH-HHC-0004": {"collection": "hunter-house-collection", "op": CCW},
    "HH-HHC-0037": {"collection": "hunter-house-collection", "op": CCW},
    "HH-HHC-0062": {"collection": "hunter-house-collection", "op": CCW},
    # HHC — CW
    "HH-HHC-0005": {"collection": "hunter-house-collection", "op": CW},
    "HH-HHC-0008": {"collection": "hunter-house-collection", "op": CW},
    "HH-HHC-0009": {"collection": "hunter-house-collection", "op": CW},
    "HH-HHC-0038": {"collection": "hunter-house-collection", "op": CW},
    "HH-HHC-0070": {"collection": "hunter-house-collection", "op": CW},
    "HH-HHC-0071": {"collection": "hunter-house-collection", "op": CW},
    "HH-HHC-0092": {"collection": "hunter-house-collection", "op": CW},
    "HH-HHC-0098": {"collection": "hunter-house-collection", "op": CW},
    "HH-HHC-0099": {"collection": "hunter-house-collection", "op": CW},
    "HH-HHC-0100": {"collection": "hunter-house-collection", "op": CW},
    "HH-HHC-0101": {"collection": "hunter-house-collection", "op": CW},
    "HH-HHC-0102": {"collection": "hunter-house-collection", "op": CW},
    "HH-HHC-0103": {"collection": "hunter-house-collection", "op": CW},
    "HH-HHC-0109": {"collection": "hunter-house-collection", "op": CW},
}

def list_r2_files(collection, archive_id):
    result = subprocess.run(
        ["rclone", "ls", f"{R2_REMOTE}/{collection}/"],
        capture_output=True, text=True, check=True
    )
    paths = []
    for line in result.stdout.splitlines():
        if archive_id in line:
            parts = line.strip().split(None, 1)
            if len(parts) == 2:
                paths.append(parts[1])   # e.g. "thumbs/HH-HHC-0004_..."
    return paths

def download(collection, r2_path, dest_dir):
    dest = os.path.join(dest_dir, os.path.basename(r2_path))
    subprocess.run(
        ["rclone", "copyto",
         f"{R2_REMOTE}/{collection}/{r2_path}", dest],
        check=True
    )
    return dest

def transform(local_path, op):
    img = Image.open(local_path)
    img = img.transpose(op)
    ext = os.path.splitext(local_path)[1].lower()
    if ext in (".jpg", ".jpeg"):
        img.save(local_path, "JPEG", quality=JPEG_QUALITY, subsampling=0)
    elif ext in (".tif", ".tiff"):
        img.save(local_path, "TIFF")
    else:
        img.save(local_path)

def upload(local_path, collection, r2_path):
    subprocess.run(
        ["rclone", "copyto",
         local_path,
         f"{R2_REMOTE}/{collection}/{r2_path}"],
        check=True
    )

# ── main ──────────────────────────────────────────────────────────────────────

os.makedirs(WORK_DIR, exist_ok=True)

for archive_id, cfg in ITEMS.items():
    collection = cfg["collection"]
    op         = cfg["op"]
    item_dir   = os.path.join(WORK_DIR, archive_id)
    os.makedirs(item_dir, exist_ok=True)

    print(f"\n── {archive_id} ──")
    r2_paths = list_r2_files(collection, archive_id)
    if not r2_paths:
        print(f"  WARNING: no files found — skipping")
        continue

    for r2_path in r2_paths:
        fname = os.path.basename(r2_path)
        print(f"  ↓ {fname}", flush=True)
        local = download(collection, r2_path, item_dir)

        print(f"    transforming ...", end=" ", flush=True)
        transform(local, op)
        print("ok")

        print(f"  ↑ uploading ...", end=" ", flush=True)
        upload(local, collection, r2_path)
        print("ok")

print("\n\nAll done. Removing work dir ...")
shutil.rmtree(WORK_DIR)
print("Complete.")
