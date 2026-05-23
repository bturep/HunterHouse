#!/usr/bin/env python3
"""
Push the local Wikibase metadata snapshot up to R2 — second half of
ARCHITECTURE.md §11.1 HIGH. Runs after scripts/backup_metadata.py has
produced a local snapshot dir.

Layout on R2:
    {collection-folder}/metadata/{ARCH_ID}.json    catalogue items
    _wikibase/items/{Qnnn}.json                    referenced (vocab/people)
    _wikibase/properties/{Pnn}.json                property definitions
    _wikibase/_manifest.json                       snapshot manifest

Collection folder map matches the existing image-tier layout:
    HHC → hunter-house-collection
    CAA → canadian-architecture-archive
    EGC → eric-gesinger-collection

Why this script exists separately from backup_metadata.py:
  - backup_metadata.py is read-only against Wikibase + writes to local
    disk only. Zero credentials, zero rclone dependency.
  - This script is transport-only: local snapshot dir → R2. Needs the
    `hh-r2` rclone remote configured (it already is) and the rclone
    binary available; no Wikibase creds.
Keeping them separate means either step can be retried/inspected
without re-running the other.

Idempotent: rclone skips unchanged files by default (size + mod-time;
add --checksum to compare hashes if you ever need to be paranoid).

Usage:
    python3 scripts/sync_metadata_to_r2.py                       # dry-run
    python3 scripts/sync_metadata_to_r2.py --execute             # do it
    python3 scripts/sync_metadata_to_r2.py --snapshot <path>     # specific snapshot
    python3 scripts/sync_metadata_to_r2.py --execute --checksum  # paranoid mode
"""

import argparse
import glob
import os
import subprocess
import sys


# Logical collection key (from sidecar dir name) → R2 prefix folder
COLLECTION_FOLDER = {
    "HHC": "hunter-house-collection",
    "CAA": "canadian-architecture-archive",
    "EGC": "eric-gesinger-collection",
    # FUL items live inside HHC in the current archive shape; add here
    # if/when FUL gets its own R2 prefix.
}

R2_REMOTE = "hh-r2:hunter-house-archive"
DEFAULT_SNAPSHOT_GLOB = "data/snapshots/wikibase_full_*"


def newest_snapshot():
    """Return the most recent local snapshot directory, or None."""
    hits = sorted(glob.glob(DEFAULT_SNAPSHOT_GLOB), reverse=True)
    return hits[0] if hits else None


def rclone(src, dest, dry_run, checksum):
    """Run one rclone copy. Returns (ok, summary_line)."""
    if not os.path.isdir(src) and not os.path.isfile(src):
        return (True, f"  (skip; {src} does not exist)")
    args = ["rclone"]
    if os.path.isfile(src):
        # Single-file copy → use copyto so dest is the full target path
        args.append("copyto")
    else:
        args.append("copy")
    args += [src, dest]
    if dry_run:
        args.append("--dry-run")
    if checksum:
        args.append("--checksum")
    args += ["--stats", "0", "--progress=false"]
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=120)
    except subprocess.TimeoutExpired:
        return (False, "  ✗ rclone timed out after 120s")
    out = (r.stdout + r.stderr).strip()
    line = "  " + (out.replace("\n", "\n  ") if out else "(no output)")
    return (r.returncode == 0, line)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--snapshot", default=None,
                    help="local snapshot dir (default: newest match for "
                         f"{DEFAULT_SNAPSHOT_GLOB})")
    ap.add_argument("--execute", action="store_true",
                    help="actually upload (default: --dry-run for everything)")
    ap.add_argument("--checksum", action="store_true",
                    help="compare hashes instead of size+mtime (slower but safer)")
    args = ap.parse_args()

    snap = args.snapshot or newest_snapshot()
    if not snap or not os.path.isdir(snap):
        sys.exit(f"no snapshot dir found ({snap or DEFAULT_SNAPSHOT_GLOB})")
    snap = os.path.abspath(snap)
    print(f"→ snapshot:  {snap}")
    print(f"→ R2 remote: {R2_REMOTE}")
    print(f"→ mode:      {'EXECUTE' if args.execute else 'DRY-RUN'}"
          f"{' (checksum)' if args.checksum else ''}")
    print()

    dry_run = not args.execute
    total_ok = 0
    total_fail = 0

    # 1. Per-collection catalogue sidecars
    for key, folder in COLLECTION_FOLDER.items():
        src = os.path.join(snap, key)
        dest = f"{R2_REMOTE}/{folder}/metadata/"
        if not os.path.isdir(src):
            print(f"→ {key}: no local dir — skipping")
            continue
        count = sum(1 for _ in os.scandir(src) if _.name.endswith(".json"))
        print(f"→ {key}: {count} sidecars → {folder}/metadata/")
        ok, line = rclone(src, dest, dry_run, args.checksum)
        print(line)
        total_ok += 1 if ok else 0
        total_fail += 0 if ok else 1
        print()

    # 2. Cross-cutting: referenced items
    ref_src = os.path.join(snap, "_referenced")
    if os.path.isdir(ref_src):
        count = sum(1 for _ in os.scandir(ref_src) if _.name.endswith(".json"))
        print(f"→ referenced items: {count} → _wikibase/items/")
        ok, line = rclone(ref_src, f"{R2_REMOTE}/_wikibase/items/",
                          dry_run, args.checksum)
        print(line)
        total_ok += 1 if ok else 0
        total_fail += 0 if ok else 1
        print()

    # 3. Cross-cutting: properties
    prop_src = os.path.join(snap, "_properties")
    if os.path.isdir(prop_src):
        count = sum(1 for _ in os.scandir(prop_src) if _.name.endswith(".json"))
        print(f"→ properties: {count} → _wikibase/properties/")
        ok, line = rclone(prop_src, f"{R2_REMOTE}/_wikibase/properties/",
                          dry_run, args.checksum)
        print(line)
        total_ok += 1 if ok else 0
        total_fail += 0 if ok else 1
        print()

    # 4. Manifest
    manifest_src = os.path.join(snap, "_manifest.json")
    if os.path.isfile(manifest_src):
        print("→ manifest: _manifest.json → _wikibase/_manifest.json")
        ok, line = rclone(manifest_src, f"{R2_REMOTE}/_wikibase/_manifest.json",
                          dry_run, args.checksum)
        print(line)
        total_ok += 1 if ok else 0
        total_fail += 0 if ok else 1
        print()

    print(f"summary: {total_ok} rclone job(s) ok, {total_fail} failed.")
    if dry_run:
        print(f"Dry run. Re-run with --execute to actually upload.")
    sys.exit(1 if total_fail else 0)


if __name__ == "__main__":
    main()
