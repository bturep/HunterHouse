#!/usr/bin/env python3
"""
recolor_previews.py
Convert R2 preview/thumb/large JPEGs from the embedded KIP 2300 scanner
ICC profile ("kip2300-v6-", ~435 KB) to a small sRGB profile in place.

Why: Chrome on wide-gamut Mac displays color-manages the kip2300-v6-
profile in a way that introduces a cyan cast on the archive images.
Safari and Firefox color-manage it cleanly. Converting the JPEGs so they
carry an sRGB profile (the universal browser-trusted reference) fixes
Chrome with no regression in Safari/Firefox.

What it does (per file):
  1. download bytes via `rclone cat`
  2. read embedded ICC profile (PIL)
  3. if no profile OR profile is sRGB OR profile is NOT kip2300       → skip
  4. else: ImageCms.profileToProfile(src=kip2300, dst=sRGB, intent=PERCEPTUAL)
  5. save JPEG with the small built-in sRGB profile embedded
  6. upload back to the same R2 key via `rclone rcat`

Modes:
  --dry-run               (default) scan + report counts. No writes.
  --one KEY               convert exactly one R2 key (test on a single file).
                          Example:
                            --one hunter-house-collection/previews/HH-HHC-0035_Hunter_Haus_Phase_2_2008-03-31_prev.jpg
  --execute               convert every kip2300-profiled JPEG bucket-wide.
  --prefix P              limit to a path prefix (repeatable); default = both
                          collections, all 3 tiers.
  --quality N             JPEG re-save quality. Default 90 (high enough to
                          avoid visible re-compression on already-lossy
                          previews; this is the only place we re-encode).

Idempotent: a file that's already sRGB-tagged is skipped, so running
--execute repeatedly is safe and a no-op after the first pass.

Dependencies: PIL (already installed), and the `rclone` remote `hh-r2`
configured against the bucket (same one the rest of the scripts use).
No boto3 / no python-dotenv required.
"""

from __future__ import annotations

import argparse
import io
import subprocess
import sys
import time
from pathlib import Path

from PIL import Image, ImageCms

# ---------- config ----------------------------------------------------------

RCLONE_REMOTE = "hh-r2:hunter-house-archive"

# Scanner profile to look for. Match is case-insensitive on profile name or
# description. We're conservative: must contain "kip2300".
SCANNER_PROFILE_TOKEN = "kip2300"

# Collection prefixes to scan (only these; skips /web/, /masters/, /pdf/).
DEFAULT_PREFIXES = [
    "hunter-house-collection/thumbs/",
    "hunter-house-collection/previews/",
    "hunter-house-collection/large/",
    "canadian-architecture-archive/thumbs/",
    "canadian-architecture-archive/previews/",
    "canadian-architecture-archive/large/",
]

# Pre-build the destination sRGB profile once (cheap, small).
SRGB_PROFILE = ImageCms.createProfile("sRGB")
SRGB_BYTES   = ImageCms.ImageCmsProfile(SRGB_PROFILE).tobytes()


# ---------- rclone helpers --------------------------------------------------

def rclone_list(prefix: str) -> list[str]:
    """Return every JPEG key under a prefix (recursive)."""
    cp = subprocess.run(
        ["rclone", "lsf", "--recursive", "--files-only",
         f"{RCLONE_REMOTE}/{prefix}"],
        capture_output=True, text=True, check=True,
    )
    keys: list[str] = []
    for line in cp.stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        # rclone lsf returns paths relative to the prefix
        if line.lower().endswith((".jpg", ".jpeg")):
            keys.append(prefix + line)
    return keys


def rclone_cat(key: str) -> bytes:
    """Stream a single object's bytes out of R2."""
    cp = subprocess.run(
        ["rclone", "cat", f"{RCLONE_REMOTE}/{key}"],
        capture_output=True, check=True,
    )
    return cp.stdout


def rclone_rcat(key: str, data: bytes) -> None:
    """Stream bytes back into R2 at the given key. Atomic replace."""
    p = subprocess.Popen(
        ["rclone", "rcat",
         "--header-upload", "Content-Type: image/jpeg",
         f"{RCLONE_REMOTE}/{key}"],
        stdin=subprocess.PIPE,
    )
    p.communicate(input=data)
    if p.returncode != 0:
        raise RuntimeError(f"rclone rcat failed for {key} (exit {p.returncode})")


# ---------- per-file work ---------------------------------------------------

def classify(icc: bytes | None) -> str:
    """Return one of: 'none' | 'srgb' | 'scanner' | 'other'."""
    if not icc:
        return "none"
    try:
        prof = ImageCms.ImageCmsProfile(io.BytesIO(icc))
        desc = (ImageCms.getProfileDescription(prof) or "").strip().lower()
        name = (ImageCms.getProfileName(prof) or "").strip().lower()
    except Exception:
        return "other"
    if SCANNER_PROFILE_TOKEN in desc or SCANNER_PROFILE_TOKEN in name:
        return "scanner"
    if "srgb" in desc or "srgb" in name:
        return "srgb"
    return "other"


def transform_bytes(jpeg_bytes: bytes, quality: int) -> bytes:
    """Convert a kip2300-tagged JPEG to an sRGB-tagged JPEG. Returns new bytes."""
    im = Image.open(io.BytesIO(jpeg_bytes))
    src_icc = im.info.get("icc_profile")
    if not src_icc:
        raise ValueError("no icc profile (caller should have skipped)")
    src_profile = ImageCms.ImageCmsProfile(io.BytesIO(src_icc))
    # PERCEPTUAL intent preserves the overall look (vs RELATIVE which can clip
    # paper-whites). These are paper scans, so PERCEPTUAL is correct.
    converted = ImageCms.profileToProfile(
        im, src_profile, SRGB_PROFILE,
        renderingIntent=ImageCms.Intent.PERCEPTUAL,
        outputMode="RGB",
    )
    out = io.BytesIO()
    converted.save(
        out, format="JPEG",
        quality=quality,
        optimize=True,
        progressive=True,
        icc_profile=SRGB_BYTES,   # small sRGB profile, not the 435KB kip2300
    )
    return out.getvalue()


def process_one(key: str, *, execute: bool, quality: int) -> tuple[str, int, int]:
    """Returns (classification, original_size, new_size_or_0)."""
    data = rclone_cat(key)
    im = Image.open(io.BytesIO(data))
    cls = classify(im.info.get("icc_profile"))
    orig_size = len(data)
    if cls != "scanner":
        return cls, orig_size, 0
    if not execute:
        return "scanner", orig_size, 0       # would convert
    new_bytes = transform_bytes(data, quality=quality)
    rclone_rcat(key, new_bytes)
    return "scanner-converted", orig_size, len(new_bytes)


# ---------- CLI -------------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--dry-run", action="store_true",
                   help="default; scan and report only")
    g.add_argument("--execute", action="store_true",
                   help="actually convert and re-upload")
    g.add_argument("--one", metavar="KEY",
                   help="process exactly one R2 key (writes unless --dry-run also passed)")
    ap.add_argument("--prefix", action="append",
                    help="restrict to a path prefix (repeatable); default = both collections, all 3 tiers")
    ap.add_argument("--quality", type=int, default=90,
                    help="JPEG re-save quality (default 90)")
    args = ap.parse_args()

    execute = args.execute or (args.one and not args.dry_run)

    # Single-file mode -------------------------------------------------------
    if args.one:
        key = args.one
        print(f"[one] {key}")
        try:
            result, orig, new = process_one(key, execute=execute, quality=args.quality)
        except subprocess.CalledProcessError as e:
            print(f"  rclone failed: exit {e.returncode}")
            return 2
        verb = {
            "none": "no embedded profile — skipped",
            "srgb": "already sRGB — skipped",
            "other": "non-scanner non-sRGB profile — skipped",
            "scanner": "scanner-profile (would convert; dry-run, no write)",
            "scanner-converted": f"converted + re-uploaded  {orig//1024} KB → {new//1024} KB",
        }[result]
        print(f"  {verb}")
        if result == "scanner-converted":
            url = f"https://archive.hunterhousefoundation.com/{key}"
            print(f"  live URL: {url}")
            print(f"  reload that in Chrome (hard-refresh) to confirm cast is gone")
        return 0

    # Bulk mode --------------------------------------------------------------
    prefixes = args.prefix or DEFAULT_PREFIXES
    print(f"[{'EXECUTE' if execute else 'DRY-RUN'}] scanning {len(prefixes)} prefix(es)")
    for p in prefixes:
        print(f"  - {p}")
    print()

    totals = {"none": 0, "srgb": 0, "scanner": 0, "scanner-converted": 0, "other": 0}
    errors: list[tuple[str, str]] = []
    started = time.time()
    n_seen = 0

    for prefix in prefixes:
        try:
            keys = rclone_list(prefix)
        except subprocess.CalledProcessError as e:
            print(f"  ERR listing {prefix}: rclone exit {e.returncode}")
            continue
        for key in keys:
            n_seen += 1
            try:
                result, _, _ = process_one(key, execute=execute, quality=args.quality)
            except Exception as e:
                errors.append((key, str(e)))
                print(f"  ERR  {key}  {e}")
                continue
            totals[result] += 1
            marker = {
                "none": ".",
                "srgb": ".",
                "other": "?",
                "scanner": "S",
                "scanner-converted": "✓",
            }[result]
            print(f"  {marker}  {key}")

    elapsed = time.time() - started
    print()
    print(f"--- summary ({elapsed:.1f}s, {n_seen} files seen) ---")
    print(f"  scanner profile (kip2300) : {totals['scanner'] + totals['scanner-converted']}"
          + (f"  → converted: {totals['scanner-converted']}" if execute else "  (dry-run; not written)"))
    print(f"  already sRGB              : {totals['srgb']}")
    print(f"  no embedded profile       : {totals['none']}")
    print(f"  other / unknown profile   : {totals['other']}")
    if errors:
        print(f"  ERRORS                    : {len(errors)}")
        for k, e in errors[:10]:
            print(f"    {k}  {e}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
