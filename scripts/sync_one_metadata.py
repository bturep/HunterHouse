#!/usr/bin/env python3
"""
Write one item's metadata sidecar to R2 — final piece of
ARCHITECTURE.md §11.1 HIGH. Called from each ingest script after a
successful Wikibase write, so every new item produces an R2 sidecar
without waiting for the next periodic backup_metadata.py run.

Read-only against Wikibase (uses public wbgetentities; no bot creds).
Writes only via rclone to the configured `hh-r2:hunter-house-archive`
remote.

Usage (CLI):
    python3 scripts/sync_one_metadata.py HH-HHC-0044
    python3 scripts/sync_one_metadata.py HH-HHC-0044 --execute   # actually write
    python3 scripts/sync_one_metadata.py HH-HHC-0044 --quiet     # only on error

Usage (from another script):
    from sync_one_metadata import sync_one
    sync_one("HH-HHC-0044", execute=True, quiet=True)            # fail-safe

The ingest scripts call this via subprocess (fail-safe) at the end of
each successful per-item ingest. A sidecar upload glitch should NEVER
break an otherwise-successful ingest — every call is wrapped in
try/except in the caller.

R2 path (matches scripts/sync_metadata_to_r2.py layout):
    {collection-folder}/metadata/{ARCH_ID}.json
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

try:
    import requests
except ImportError:
    sys.exit("Missing 'requests'.  pip3 install requests")


WIKIBASE = "https://hunterhouse.wikibase.cloud"
SPARQL   = f"{WIKIBASE}/query/sparql"
API      = f"{WIKIBASE}/w/api.php"
R2_REMOTE = "hh-r2:hunter-house-archive"

USER_AGENT = "HunterHouseSidecar/1.0 (sync_one_metadata; bturep)"

# Same mapping as scripts/sync_metadata_to_r2.py.
COLLECTION_FOLDER = {
    "HHC": "hunter-house-collection",
    "CAA": "canadian-architecture-archive",
    "EGC": "eric-gesinger-collection",
    "IVH": "ivan-hunter-collection",
}


def qid_for(arch_id):
    """SPARQL: archId → QID (str), or None if no item exists."""
    q = f"""
PREFIX wdt: <https://hunterhouse.wikibase.cloud/prop/direct/>
SELECT ?item WHERE {{
  ?item wdt:P2 "{arch_id}" .
}}
"""
    r = requests.get(SPARQL, params={"query": q, "format": "json"},
                     headers={"Accept": "application/sparql-results+json",
                              "User-Agent": USER_AGENT}, timeout=30)
    r.raise_for_status()
    rows = r.json()["results"]["bindings"]
    if not rows:
        return None
    return rows[0]["item"]["value"].rsplit("/", 1)[-1]


def fetch_entity(qid):
    """wbgetentities for one QID."""
    r = requests.get(API, params={"action": "wbgetentities", "ids": qid,
                                  "format": "json"},
                     headers={"User-Agent": USER_AGENT}, timeout=30)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"wbgetentities error: {data['error']}")
    ent = data.get("entities", {}).get(qid)
    if not ent or ent.get("missing"):
        raise RuntimeError(f"entity {qid} not found")
    return ent


def collection_of(arch_id):
    """HH-HHC-0044 → 'HHC'."""
    parts = arch_id.split("-")
    return parts[1] if len(parts) >= 3 else None


def r2_dest_for(arch_id):
    """Full rclone destination path for this item's sidecar, or None
    if we don't have a folder mapping for this collection."""
    coll = collection_of(arch_id)
    folder = COLLECTION_FOLDER.get(coll)
    if not folder:
        return None
    return f"{R2_REMOTE}/{folder}/metadata/{arch_id}.json"


def sync_one(arch_id, execute=False, quiet=False):
    """Programmatic entry point. Returns True on success.

    Fail-safe in spirit: callers should still wrap in try/except. This
    function does raise on real failures (network, missing entity,
    rclone non-zero) so callers can decide whether to ignore or log.
    """
    def say(msg):
        if not quiet:
            print(msg)

    dest = r2_dest_for(arch_id)
    if not dest:
        say(f"  ⚠ {arch_id}: no R2 folder mapping for collection prefix "
            f"{collection_of(arch_id)!r} — skipping")
        return False

    say(f"→ {arch_id}: resolving QID …")
    qid = qid_for(arch_id)
    if not qid:
        say(f"  ⚠ {arch_id}: no Wikibase item found via SPARQL (replication "
            f"lag? — try again in ~60s)")
        return False
    say(f"  QID = {qid}")

    say(f"→ wbgetentities …")
    ent = fetch_entity(qid)
    payload = json.dumps(ent, indent=2, ensure_ascii=False, sort_keys=True)
    say(f"  {len(payload):,} bytes")

    if not execute:
        say(f"  DRY-RUN — would copyto → {dest}")
        return True

    # Write to a tempfile so rclone has a real path to copy from.
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json",
                                     prefix=f"{arch_id}_", delete=False) as f:
        f.write(payload)
        tmp_path = f.name
    try:
        r = subprocess.run(
            ["rclone", "copyto", tmp_path, dest,
             "--stats", "0", "--progress=false"],
            capture_output=True, text=True, timeout=60,
        )
        if r.returncode != 0:
            say(f"  ✗ rclone failed (exit {r.returncode}):")
            say(f"    {(r.stdout + r.stderr).strip()}")
            return False
        say(f"  ✓ → {dest}")
        return True
    finally:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("arch_id", help="archive ID, e.g. HH-HHC-0044")
    ap.add_argument("--execute", action="store_true",
                    help="actually upload (default: dry-run)")
    ap.add_argument("--quiet", action="store_true",
                    help="suppress per-step prints (still prints on error)")
    args = ap.parse_args()
    try:
        ok = sync_one(args.arch_id, execute=args.execute, quiet=args.quiet)
    except Exception as e:
        print(f"  ✗ {args.arch_id}: {type(e).__name__}: {e}")
        sys.exit(2)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
