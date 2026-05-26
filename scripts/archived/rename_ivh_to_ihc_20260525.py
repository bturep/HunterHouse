#!/usr/bin/env python3
"""
Rename HH-IVH-* → HH-IHC-* across Wikibase + R2 (45 items, ingested earlier
the same day 2026-05-25). Brandon asked for the prefix code to be IHC, not
IVH; the collection name "Ivan Hunter Collection" and the R2 folder name
`ivan-hunter-collection` stay the same — only the 3-letter prefix in the
archive ID, the embedded filename prefix, and the description tag change.

Follows the documented Batch change protocol (CLAUDE.md), patterned closely
on scripts/renumber_caa.py. The IVH set is much simpler:
  - Single source collection (Q183).
  - Uniform label ("Hunter House") and date (2024-02-11).
  - Masters are .jpg (these are print-finals; no TIF masters upstream).
  - Slug+date suffix `HunterHouse_2024` is identical across all 45.

Order of operations:
  Stage 0 : Pre-flight (snapshot loaded, 45 items planned)
  Stage 1 : P97 append — record legacy HH-IVH-NNNN on each item
  Stage 2 : R2 server-side copy — old → new for masters/thumbs/previews/
            large/metadata (both exist briefly). 5 paths × 45 = 225 copies.
  Stage 3 : Wikibase P95 + P96 URL rewrite — point at new R2 paths
  Stage 4 : Wikibase P2 update — HH-IVH-NNNN → HH-IHC-NNNN
  Stage 5 : Wikibase description update — "photograph; IVH; HH-IVH-NNNN;
            2024" → "photograph; IHC; HH-IHC-NNNN; 2024"
  Stage 6 : Delete old R2 paths (only after stages 1-5 succeed)

Dry-run by default. --execute does the writes.
"""

import argparse
import glob
import json
import os
import subprocess
import sys

import requests

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from _wikibase import WikibaseSession  # noqa: E402

# ─── paths / endpoints ──────────────────────────────────────────────────────
API = "https://hunterhouse.wikibase.cloud/w/api.php"
SNAPSHOT_GLOB = "data/snapshots/ivh_pre_rename_*.json"

R2          = "hh-r2:hunter-house-archive"
COLL_DIR    = "ivan-hunter-collection"        # unchanged
PUBLIC_BASE = "https://archive.hunterhousefoundation.com"

OLD_PREFIX = "HH-IVH-"
NEW_PREFIX = "HH-IHC-"
SLUG_BASE  = "HunterHouse_2024"               # identical for all 45 items

TIERS = [
    ("masters",  ".jpg",       ""),
    ("thumbs",   "_thumb.jpg", "_thumb"),
    ("previews", "_prev.jpg",  "_prev"),
    ("large",    "_large.jpg", "_large"),
]


# ─── load snapshot ──────────────────────────────────────────────────────────
def latest_snapshot():
    paths = sorted(glob.glob(SNAPSHOT_GLOB))
    if not paths:
        raise SystemExit("No IVH snapshot found in data/snapshots/.")
    return paths[-1]


def build_mapping(rows):
    """Each row: {qid, archId, label, desc, itype, master, preview}.
    Returns sorted list of dicts with old/new IDs, URLs, descriptions."""
    out = []
    for r in sorted(rows, key=lambda x: x["archId"]):
        n = int(r["archId"].rsplit("-", 1)[-1])
        new_id = f"{NEW_PREFIX}{n:04d}"
        out.append({
            "qid":          r["qid"],
            "old":          r["archId"],
            "new":          new_id,
            "label":        r.get("label", ""),
            "old_desc":     r.get("desc", ""),
            "new_desc":     (r.get("desc", "")
                             .replace("; IVH; ", "; IHC; ")
                             .replace(r["archId"], new_id)),
            "old_master":   r.get("master"),
            "old_preview":  r.get("preview"),
            "new_master":   f"{PUBLIC_BASE}/{COLL_DIR}/masters/{new_id}_{SLUG_BASE}.jpg",
            "new_preview":  f"{PUBLIC_BASE}/{COLL_DIR}/previews/{new_id}_{SLUG_BASE}_prev.jpg",
        })
    return out


def r2_pairs(item):
    """Per-item list of (old_path, new_path) tuples covering all 4 image
    tiers + the metadata sidecar. Paths are relative to the bucket root."""
    pairs = []
    for tier, ext, suffix in TIERS:
        pairs.append((
            f"{COLL_DIR}/{tier}/{item['old']}_{SLUG_BASE}{suffix}.jpg",
            f"{COLL_DIR}/{tier}/{item['new']}_{SLUG_BASE}{suffix}.jpg",
        ))
    # Sidecar metadata JSON
    pairs.append((
        f"{COLL_DIR}/metadata/{item['old']}.json",
        f"{COLL_DIR}/metadata/{item['new']}.json",
    ))
    return pairs


# ─── Wikibase helpers (mirrors renumber_caa.py with WikibaseSession) ───────
def append_p97(wb, qid, old_archid):
    """Add P97 legacy ID claim, idempotent (skips if already present)."""
    ent = wb.get("wbgetentities", ids=qid, props="claims")["entities"][qid]
    for c in ent.get("claims", {}).get("P97", []):
        v = c["mainsnak"].get("datavalue", {}).get("value")
        if v == old_archid:
            return False
    r = wb.post("wbcreateclaim", entity=qid, snaktype="value",
                property="P97", value=json.dumps(old_archid))
    if "error" in r:
        raise SystemExit(f"P97 append failed for {qid}: {r['error']}")
    return True


def set_string_claim(wb, qid, pid, new_value):
    """Replace a single-valued string/URL claim via wbsetclaim."""
    ent = wb.get("wbgetentities", ids=qid, props="claims")["entities"][qid]
    existing = ent.get("claims", {}).get(pid, [])
    if existing:
        claim = existing[0]
        claim["mainsnak"]["datavalue"]["value"] = new_value
        r = wb.post("wbsetclaim", claim=json.dumps(claim))
    else:
        r = wb.post("wbcreateclaim", entity=qid, snaktype="value",
                    property=pid, value=json.dumps(new_value))
    if "error" in r:
        raise SystemExit(f"{pid} write failed for {qid}: {r['error']}")


def set_description(wb, qid, new_desc):
    r = wb.post("wbsetdescription", id=qid, language="en", value=new_desc)
    if "error" in r:
        raise SystemExit(f"description update failed for {qid}: {r['error']}")


# ─── main ───────────────────────────────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true",
                    help="Actually perform writes; otherwise dry-run.")
    ap.add_argument("--delete-old", action="store_true",
                    help="Also delete the old IVH-named R2 paths (stage 6). "
                         "Default leaves them in place so a sanity verify can "
                         "see both states.")
    args = ap.parse_args()

    snap_path = latest_snapshot()
    rows = json.load(open(snap_path))
    mapping = build_mapping(rows)

    print(f"\n{'EXECUTE' if args.execute else 'DRY RUN'} — IVH → IHC rename\n")
    print(f"Snapshot: {snap_path}")
    print(f"Items:    {len(mapping)}\n")

    # Print mapping table
    print(f"{'OLD':<14} → {'NEW':<14}  QID    Desc-after")
    print("-" * 96)
    for m in mapping:
        print(f"{m['old']:<14} → {m['new']:<14}  {m['qid']:<6} {m['new_desc']!r}")

    n_r2_moves = sum(len(r2_pairs(m)) for m in mapping)
    print(f"\nR2 server-side moves: {n_r2_moves}  "
          f"(4 image tiers + 1 sidecar per item × {len(mapping)} items)")

    if not args.execute:
        print(f"\nFirst item's R2 pairs (illustrative):")
        for old, new in r2_pairs(mapping[0]):
            print(f"  {old.rsplit('/',1)[-1]:<55} → {new.rsplit('/',1)[-1]}")
        print(f"\nDRY RUN. Re-run with --execute to perform writes.")
        return

    # ── EXECUTE ─────────────────────────────────────────────────────────────
    wb = WikibaseSession(user_agent="HunterHouseBot/1.0 (rename_ivh_to_ihc)")
    print("  logged in as bot.")

    print(f"\n[1/{6 if args.delete_old else 5}] Append P97 legacy IDs …")
    for m in mapping:
        added = append_p97(wb, m["qid"], m["old"])
        print(f"  {m['qid']} ({m['old']}): P97 += {m['old']}  "
              f"{'(appended)' if added else '(already present)'}")

    print(f"\n[2/{6 if args.delete_old else 5}] R2 server-side copy (old → new) …")
    for m in mapping:
        for old, new in r2_pairs(m):
            subprocess.run(["rclone", "copyto", f"{R2}/{old}", f"{R2}/{new}"],
                           check=True)
        print(f"  {m['old']} → {m['new']}  ({len(r2_pairs(m))} files)")

    print(f"\n[3/{6 if args.delete_old else 5}] Wikibase P95 + P96 URL rewrite …")
    for m in mapping:
        set_string_claim(wb, m["qid"], "P95", m["new_master"])
        set_string_claim(wb, m["qid"], "P96", m["new_preview"])
        print(f"  {m['qid']}: P95 + P96 → /{m['new']}_{SLUG_BASE}*")

    print(f"\n[4/{6 if args.delete_old else 5}] Wikibase P2 update …")
    for m in mapping:
        set_string_claim(wb, m["qid"], "P2", m["new"])
        print(f"  {m['qid']}: P2 → {m['new']}")

    print(f"\n[5/{6 if args.delete_old else 5}] Wikibase description update …")
    for m in mapping:
        set_description(wb, m["qid"], m["new_desc"])
        print(f"  {m['qid']}: desc → {m['new_desc']!r}")

    if args.delete_old:
        print(f"\n[6/6] Delete old R2 paths …")
        for m in mapping:
            for old, _ in r2_pairs(m):
                subprocess.run(["rclone", "deletefile", f"{R2}/{old}"],
                               check=True)
            print(f"  {m['old']} purged ({len(r2_pairs(m))} files)")
    else:
        print(f"\n(Skipped stage 6 — old R2 paths still in place. "
              f"Re-run with --delete-old once verify passes.)")

    print(f"\n══════════════════ DONE ══════════════════")


if __name__ == "__main__":
    main()
