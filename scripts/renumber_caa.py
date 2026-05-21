#!/usr/bin/env python3
"""
Renumber CAA: drawings first, photographs last.

Reads the SPARQL snapshot in data/snapshots/caa_pre_renumber_*.json, sorts
drawings (P1=Q88) by current numeric (preserving their relative order),
then photographs (P1=Q89) by current numeric, and assigns new HH-CAA-NNNN
IDs sequentially starting at 0001.

Per the documented Batch change protocol:
  1. P97 legacy ID is APPENDED with the old HH-CAA-NNNN before P2 changes
     (each item already carries its HH-A-NNNN P97 from the 2026-05-14
     migration; this adds the next layer.)
  2. P2 updated via wbsetclaim (replace existing claim).
  3. R2 files for all 4 tiers (masters / previews / thumbs / large) are
     server-side copied to the new HH-CAA-NNNN prefix (slug + date stay).
  4. P95 + P96 URLs rewritten to point at the new R2 paths.
  5. After ALL items succeed, old R2 paths are purged.

Dry-run is default: prints full mapping. --execute does the writes.
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys

import requests

API = "https://hunterhouse.wikibase.cloud/w/api.php"
ENV = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")
SNAPSHOT_GLOB = "data/snapshots/caa_pre_renumber_*.json"

R2          = "hh-r2:hunter-house-archive"
COLL_DIR    = "canadian-architecture-archive"
PUBLIC_BASE = "https://archive.hunterhousefoundation.com"
TIERS = ["masters", "previews", "thumbs", "large"]


def load_env(path):
    env = {}
    for line in open(path):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def latest_snapshot():
    paths = sorted(glob.glob(SNAPSHOT_GLOB))
    if not paths:
        raise SystemExit("No CAA snapshot found in data/snapshots/. Run the snapshot step first.")
    return paths[-1]


def derive_filename(url, old_prefix):
    """Given a URL like .../previews/HH-CAA-0007_Slug_Date_prev.jpg, return
    the bare filename — used to compute the corresponding masters / thumbs /
    large names by suffix substitution."""
    if not url: return None
    name = url.rsplit("/", 1)[-1]
    if not name.startswith(old_prefix + "_"):
        return None
    return name


def build_mapping(rows):
    """rows: list of {qid, archId, itype, ...}. Returns ordered list of
    (i, old, new, type) tuples where new = HH-CAA-{i+1:04d}, drawings
    first in current-id order, then photographs in current-id order."""
    def numeric(r): return int(r["archId"].rsplit("-", 1)[-1])
    drawings = sorted([r for r in rows if r["itype"] == "Q88"], key=numeric)
    photos   = sorted([r for r in rows if r["itype"] == "Q89"], key=numeric)
    other    = [r for r in rows if r["itype"] not in ("Q88", "Q89")]
    if other:
        raise SystemExit(f"Unexpected item types in CAA: {[r['archId'] for r in other]}")
    ordered = drawings + photos
    mapping = []
    for i, r in enumerate(ordered, start=1):
        new = f"HH-CAA-{i:04d}"
        mapping.append({
            "qid":        r["qid"],
            "old":        r["archId"],
            "new":        new,
            "type":       r["itype"],
            "typeLabel":  r["itypeLabel"],
            "label":      r["label"],
            "master":     r["master"],
            "preview":    r["preview"],
            "unchanged":  (r["archId"] == new),
        })
    return mapping


def r2_rename_plan(mapping):
    """For each item, compute the per-tier old → new R2 paths. The slug+date
    suffix is read from the existing preview URL; if the URL is missing we
    skip (admin will see a warning in the dry-run)."""
    plans = []
    for m in mapping:
        if m["unchanged"]:
            plans.append({"item": m, "tiers": [], "ok": True, "note": "no rename needed"})
            continue
        # Pull the slug+date from the master URL (extension differs across
        # tiers — masters are .tif, web tiers are .jpg).
        if not m["master"]:
            plans.append({"item": m, "tiers": [], "ok": False, "note": "missing P95 master URL"})
            continue
        old_name = m["master"].rsplit("/", 1)[-1]   # HH-CAA-NNNN_Slug_Date.tif
        if not old_name.startswith(m["old"] + "_"):
            plans.append({"item": m, "tiers": [], "ok": False, "note": f"master URL prefix mismatch: {old_name}"})
            continue
        suffix_tif = old_name[len(m["old"]) + 1:]   # Slug_Date.tif
        # Derive base = Slug_Date (no extension, no tier suffix)
        # For web tiers, the filename is HH-CAA-NNNN_Slug_Date_<tier>.jpg
        # so we strip the .tif from the master suffix and rebuild for each tier.
        base = suffix_tif.rsplit(".", 1)[0]   # Slug_Date
        tiers = []
        # Masters: .tif, no tier marker
        tiers.append({
            "tier": "masters",
            "old": f"{COLL_DIR}/masters/{m['old']}_{base}.tif",
            "new": f"{COLL_DIR}/masters/{m['new']}_{base}.tif",
        })
        for t, suffix in [("previews", "_prev"), ("thumbs", "_thumb"), ("large", "_large")]:
            tiers.append({
                "tier": t,
                "old": f"{COLL_DIR}/{t}/{m['old']}_{base}{suffix}.jpg",
                "new": f"{COLL_DIR}/{t}/{m['new']}_{base}{suffix}.jpg",
            })
        # New URLs
        m["new_master_url"]  = f"{PUBLIC_BASE}/{COLL_DIR}/masters/{m['new']}_{base}.tif"
        m["new_preview_url"] = f"{PUBLIC_BASE}/{COLL_DIR}/previews/{m['new']}_{base}_prev.jpg"
        plans.append({"item": m, "tiers": tiers, "ok": True, "note": ""})
    return plans


# ─────────────────────────── Wikibase helpers ───────────────────────────────
def wb_login(s, env):
    t = s.get(API, params={"action":"query","meta":"tokens","type":"login","format":"json"}).json()["query"]["tokens"]["logintoken"]
    r = s.post(API, data={"action":"login","lgname":env["WIKIBASE_BOT_USER"],"lgpassword":env["WIKIBASE_BOT_PASSWORD"],"lgtoken":t,"format":"json"}).json()
    if r["login"]["result"] != "Success":
        raise SystemExit(f"Login failed: {r['login']['result']}")
def wb_csrf(s):
    return s.get(API, params={"action":"query","meta":"tokens","format":"json"}).json()["query"]["tokens"]["csrftoken"]

def append_p97(s, csrf, qid, old_archid):
    """Add a P97 legacy ID claim. P97 is string, multi-value: each migration
    appends rather than replaces, so the chain HH-A-NNNN → HH-CAA-NNNN (old)
    → HH-CAA-NNNN (new) is preserved across renumbers."""
    # Idempotency: skip if a P97 claim with this exact value already exists.
    ent = s.get(API, params={"action":"wbgetentities","ids":qid,"props":"claims","format":"json"}).json()["entities"][qid]
    for c in ent.get("claims",{}).get("P97",[]):
        v = c["mainsnak"].get("datavalue",{}).get("value")
        if v == old_archid:
            return False
    r = s.post(API, data={
        "action":"wbcreateclaim","entity":qid,"snaktype":"value",
        "property":"P97","value":json.dumps(old_archid),
        "token":csrf,"format":"json"
    }).json()
    if "error" in r: raise SystemExit(f"P97 append failed for {qid}: {r['error']}")
    return True

def set_p2(s, csrf, qid, new_archid):
    """Replace the P2 archive ID. P2 is single-valued — use wbsetclaim
    against the existing claim id, or create + remove if none exists."""
    ent = s.get(API, params={"action":"wbgetentities","ids":qid,"props":"claims","format":"json"}).json()["entities"][qid]
    existing = ent.get("claims",{}).get("P2",[])
    if existing:
        claim = existing[0]
        claim["mainsnak"]["datavalue"]["value"] = new_archid
        r = s.post(API, data={"action":"wbsetclaim","claim":json.dumps(claim),"token":csrf,"format":"json"}).json()
        if "error" in r: raise SystemExit(f"P2 set failed for {qid}: {r['error']}")
    else:
        r = s.post(API, data={"action":"wbcreateclaim","entity":qid,"snaktype":"value","property":"P2","value":json.dumps(new_archid),"token":csrf,"format":"json"}).json()
        if "error" in r: raise SystemExit(f"P2 create failed for {qid}: {r['error']}")

def set_url_claim(s, csrf, qid, pid, new_url):
    """Replace a single-valued URL claim (P95 master / P96 preview)."""
    ent = s.get(API, params={"action":"wbgetentities","ids":qid,"props":"claims","format":"json"}).json()["entities"][qid]
    existing = ent.get("claims",{}).get(pid,[])
    if existing:
        claim = existing[0]
        claim["mainsnak"]["datavalue"]["value"] = new_url
        r = s.post(API, data={"action":"wbsetclaim","claim":json.dumps(claim),"token":csrf,"format":"json"}).json()
    else:
        r = s.post(API, data={"action":"wbcreateclaim","entity":qid,"snaktype":"value","property":pid,"value":json.dumps(new_url),"token":csrf,"format":"json"}).json()
    if "error" in r: raise SystemExit(f"{pid} write failed for {qid}: {r['error']}")


# ─────────────────────────── main ───────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true", help="Actually perform writes; otherwise dry-run.")
    args = ap.parse_args()

    snap_path = latest_snapshot()
    rows = json.load(open(snap_path))
    mapping = build_mapping(rows)
    plans = r2_rename_plan(mapping)

    print(f"\n{'EXECUTE' if args.execute else 'DRY RUN'} — CAA renumber\n")
    print(f"Snapshot: {snap_path}")
    print(f"Items:    {len(mapping)}\n")

    print(f"{'OLD':<14} → {'NEW':<14}  {'Type':<11}  Title")
    print("-" * 90)
    for m in mapping:
        arrow = "→" if not m["unchanged"] else "="
        print(f"{m['old']:<14} {arrow} {m['new']:<14}  {m['typeLabel']:<11}  «{m['label']}»")

    changed = [m for m in mapping if not m["unchanged"]]
    skipped = [m for m in mapping if m["unchanged"]]
    print(f"\nWill renumber: {len(changed)}  ·  Already in target slot: {len(skipped)}")

    # R2 rename plan
    bad = [p for p in plans if not p["ok"]]
    if bad:
        print("\n⚠  Plan problems:")
        for p in bad:
            print(f"  {p['item']['old']}: {p['note']}")
        raise SystemExit("Aborting — resolve plan problems first.")

    n_tiers = sum(len(p["tiers"]) for p in plans)
    print(f"\nR2 server-side copies: {n_tiers} (4 per renumbered item)")

    if not args.execute:
        print("\nFirst 3 R2 rename pairs (illustrative):")
        for p in plans[:3]:
            for t in p["tiers"]:
                print(f"  {t['tier']}/  {t['old'].rsplit('/',1)[-1]}  →  {t['new'].rsplit('/',1)[-1]}")
        print("\nDRY RUN complete. Re-run with --execute to perform writes.")
        return

    # ── EXECUTE ─────────────────────────────────────────────────────────────
    env = load_env(ENV)
    s = requests.Session(); s.headers.update({"User-Agent":"HH/caa-renumber"})
    wb_login(s, env)
    csrf = wb_csrf(s)
    print("  logged in as bot.")

    # Stage 1: P97 append (record the legacy HH-CAA-NNNN before changing P2)
    print("\n[1/5] Appending P97 legacy IDs…")
    for m in mapping:
        if m["unchanged"]: continue
        added = append_p97(s, csrf, m["qid"], m["old"])
        print(f"  {m['qid']} ({m['old']}): P97 += {m['old']}  {'(appended)' if added else '(already present)'}")

    # Stage 2: R2 server-side copy (old → new, both still exist)
    print(f"\n[2/5] R2 server-side copy ({n_tiers} files)…")
    for p in plans:
        if not p["tiers"]: continue
        for t in p["tiers"]:
            old_src = f"{R2}/{t['old']}"
            new_dst = f"{R2}/{t['new']}"
            subprocess.run(["rclone", "copyto", old_src, new_dst], check=True)
        print(f"  {p['item']['old']} → {p['item']['new']}  ({len(p['tiers'])} tiers copied)")

    # Stage 3: P95/P96 URL rewrite
    print("\n[3/5] Rewriting P95 + P96 URLs…")
    for m in mapping:
        if m["unchanged"]: continue
        set_url_claim(s, csrf, m["qid"], "P95", m["new_master_url"])
        set_url_claim(s, csrf, m["qid"], "P96", m["new_preview_url"])
        print(f"  {m['qid']}: P95 + P96 → new")

    # Stage 4: P2 update (now that the new R2 paths and URLs are live)
    print("\n[4/5] Updating P2 (HH archive ID)…")
    for m in mapping:
        if m["unchanged"]: continue
        set_p2(s, csrf, m["qid"], m["new"])
        print(f"  {m['qid']}: P2 → {m['new']}")

    # Stage 5: Delete old R2 files
    print(f"\n[5/5] Deleting old R2 files…")
    for p in plans:
        if not p["tiers"]: continue
        for t in p["tiers"]:
            old_src = f"{R2}/{t['old']}"
            subprocess.run(["rclone", "deletefile", old_src], check=True)
        print(f"  {p['item']['old']}: {len(p['tiers'])} old files deleted")

    print("\n══════════════════ DONE ══════════════════")
    print(f"  Renumbered {len(changed)} CAA items: drawings → HH-CAA-0001..{sum(1 for m in mapping if m['type']=='Q88'):04d}; photos → trailing slots.")


if __name__ == "__main__":
    main()
