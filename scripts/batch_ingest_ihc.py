#!/usr/bin/env python3
"""
Batch ingest the Ivan Hunter Collection (IHC) — 45 print-final photographs of
the Hunter Residence, photographed by Ivan Hunter on 2024-02-11.

Source: /Volumes/Verbatim/203Goward Rd Photos/203Goward_print_finals/
  Files named -1.jpg ... -45.jpg (leading hyphen, integer ordering).
  Already JPEGs — no TIF masters — so each JPG IS the preservation master.

Model = batch_ingest_egc.py, simplified:
  - No phases, no drawing-types, no workbook intake.
  - Brandon's instruction: "Photographed by Ivan Hunter on 2024-02-11, all
    depicting the Hunter House. Item type photograph. Everything else can
    remain blank."
  - Reference QIDs (all already in Wikibase, verified at draft time):
      Q183  Ivan Hunter Collection      (P79 source collection)
      Q203  Ivan Hunter                 (P80 creator)
      Q234  Hunter Residence            (P85 depicts)
      Q89   Photograph                  (P1 instance of)

Dry-run by default: prints the per-row plan and dumps the first item's
_large.jpg tier to Desktop for eyeball review. `--execute` performs:
  1. For each source JPG (sorted numerically):
       - Build 3 web tiers via sips (sRGB baked).
       - Upload master JPG byte-for-byte + tiers to R2.
       - Create Wikibase item with P1/P2/P79/P80/P82/P85/P95/P96.
       - Fail-safe sync_one_metadata.py sidecar push to R2.

Idempotency: items don't dedupe by P2 here — only run --execute once on a
clean R2 IHC folder + empty Wikibase IHC set. Re-runs would create duplicate
archive items.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wikibase import WikibaseSession  # noqa: E402
import requests  # noqa: E402  (SPARQL lookup for resume-skip; no creds needed)

# ─────────────────────────── paths ──────────────────────────────────────────
SRC_DIR = "/Volumes/Verbatim/203Goward Rd Photos/203Goward_print_finals"
WORK    = "/tmp/hh_ihc_ingest"

# ─────────────────────────── R2 ─────────────────────────────────────────────
R2          = "hh-r2:hunter-house-archive"
COLL_DIR    = "ivan-hunter-collection"
PUBLIC_BASE = "https://archive.hunterhousefoundation.com"
R2_MASTERS  = f"{R2}/{COLL_DIR}/masters"
R2_THUMBS   = f"{R2}/{COLL_DIR}/thumbs"
R2_PREVIEWS = f"{R2}/{COLL_DIR}/previews"
R2_LARGE    = f"{R2}/{COLL_DIR}/large"

# ─────────────────────────── Wikibase ───────────────────────────────────────
CALENDAR = "http://www.wikidata.org/entity/Q1985727"

SOURCE_COLLECTION_QID = "Q183"   # Ivan Hunter Collection
CREATOR_QID           = "Q203"   # Ivan Hunter
DEPICTS_QID           = "Q234"   # Hunter Residence
PHOTOGRAPH_QID        = "Q89"    # P1 instance-of for photographs

CAPTURE_DATE = datetime(2024, 2, 11)   # 2024-02-11, day precision
LABEL        = "Hunter House"
SLUG_BASE    = "HunterHouse_2024"

# Tier recipes (same as EGC / browse.html convention)
TIERS = {
    "_thumb.jpg": (600, 75),
    "_prev.jpg":  (2000, 82),
    "_large.jpg": (3840, 85),
}

EXECUTE = "--execute" in sys.argv


# ─────────────────────────── helpers ────────────────────────────────────────
def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def sips_jpeg(src, dst, max_px, quality):
    run(["sips", "-Z", str(max_px),
         "-m", "/System/Library/ColorSync/Profiles/sRGB Profile.icc",
         "-s", "format", "jpeg",
         "-s", "formatOptions", str(quality), src, "--out", dst],
        capture_output=True)


# ─────────────────────────── source scan ────────────────────────────────────
SRC_NAME_RE = re.compile(r"^-(\d+)\.jpg$", re.IGNORECASE)


def load_rows():
    """Scan SRC_DIR for `-N.jpg`, sort by N (numeric), map to HH-IHC-NNNN."""
    sources = []
    for f in Path(SRC_DIR).iterdir():
        m = SRC_NAME_RE.match(f.name)
        if not m:
            continue
        sources.append((int(m.group(1)), str(f)))
    sources.sort(key=lambda t: t[0])
    rows = []
    for i, (n, path) in enumerate(sources, start=1):
        arch_id = f"HH-IHC-{i:04d}"
        master_name = f"{arch_id}_{SLUG_BASE}.jpg"
        rows.append({
            "n":            n,
            "id":           arch_id,
            "source":       path,
            "master_name":  master_name,
            "preview_url":  f"{PUBLIC_BASE}/{COLL_DIR}/previews/{arch_id}_{SLUG_BASE}_prev.jpg",
            "master_url":   f"{PUBLIC_BASE}/{COLL_DIR}/masters/{master_name}",
        })
    return rows


# ─────────────────────────── Wikibase claim helpers ─────────────────────────
def claim(pid, datatype, value):
    if datatype == "wikibase-item":
        dv = {"value": {"entity-type": "item", "id": value},
              "type": "wikibase-entityid"}
    elif datatype == "time-day":
        dv = {"value": {"time": value.strftime("+%Y-%m-%dT00:00:00Z"),
                        "timezone": 0, "before": 0, "after": 0,
                        "precision": 11, "calendarmodel": CALENDAR},
              "type": "time"}
    else:
        dv = {"value": value, "type": "string"}
    return {"mainsnak": {"snaktype": "value", "property": pid, "datavalue": dv},
            "type": "statement", "rank": "normal"}


def build_item_claims(row):
    return [
        claim("P1",  "wikibase-item", PHOTOGRAPH_QID),
        claim("P2",  "string",        row["id"]),
        claim("P79", "wikibase-item", SOURCE_COLLECTION_QID),
        claim("P80", "wikibase-item", CREATOR_QID),
        claim("P82", "time-day",      CAPTURE_DATE),
        claim("P85", "wikibase-item", DEPICTS_QID),
        claim("P95", "url",           row["master_url"]),
        claim("P96", "url",           row["preview_url"]),
    ]


def description_for(row):
    # Include ID for Wikibase (label, description) uniqueness — all 45 share
    # the same label "Hunter House". Year suffix matches EGC pattern.
    return f"photograph; IHC; {row['id']}; 2024"


def wb_create_item(wb, labels, descriptions, claims):
    data = {
        "labels":       {l: {"language": l, "value": v} for l, v in labels.items()},
        "descriptions": {l: {"language": l, "value": v} for l, v in descriptions.items()},
        "claims": claims,
    }
    r = wb.post("wbeditentity", new="item", data=json.dumps(data))
    if "error" in r:
        raise SystemExit(f"item create failed: {r['error']}")
    return r["entity"]["id"]


_SPARQL_URL = "https://hunterhouse.wikibase.cloud/query/sparql"


def wb_find_by_p2(wb, arch_id):
    """Return QID of an existing item with this P2 archive ID, else None.

    Uses SPARQL — wbsearchentities only matches against labels/aliases,
    not statement string values, so for IHC (where every item shares the
    label "Hunter House") wbsearchentities returns nothing useful.
    Same pattern as scripts/sync_one_metadata.py::qid_for.
    """
    q = (
        "PREFIX wdt: <https://hunterhouse.wikibase.cloud/prop/direct/>\n"
        f'SELECT ?item WHERE {{ ?item wdt:P2 "{arch_id}" . }}\n'
    )
    r = requests.get(_SPARQL_URL, params={"query": q, "format": "json"},
                     headers={"Accept": "application/sparql-results+json",
                              "User-Agent": "HunterHouseBot/1.0 (batch_ingest_ihc)"},
                     timeout=30)
    r.raise_for_status()
    rows = r.json()["results"]["bindings"]
    if not rows:
        return None
    return rows[0]["item"]["value"].rsplit("/", 1)[-1]


# ─────────────────────────── main ───────────────────────────────────────────
def main():
    if not os.path.isdir(SRC_DIR):
        raise SystemExit(f"Source folder not mounted/found: {SRC_DIR}")

    rows = load_rows()
    if not rows:
        raise SystemExit(f"No -N.jpg files found in {SRC_DIR}")

    print(f"\n{'EXECUTE' if EXECUTE else 'DRY RUN'} — IHC batch ingest ({len(rows)} items)\n")

    # ── pre-flight
    expected = list(range(1, len(rows) + 1))
    found_ns = [r["n"] for r in rows]
    if found_ns != expected:
        gaps = sorted(set(expected) - set(found_ns))
        extras = sorted(set(found_ns) - set(expected))
        print(f"  ⚠  Source N sequence not contiguous 1..{len(rows)}")
        if gaps:   print(f"      missing N: {gaps}")
        if extras: print(f"      extra N:   {extras}")
        print("  (Mapping still proceeds in sorted-N order; review carefully.)\n")

    # ── per-row manifest
    print(f"── Per-item manifest ──")
    total_mb = 0
    for r in rows:
        size_mb = os.path.getsize(r["source"]) / 1e6
        total_mb += size_mb
        print(f"  {r['id']}  ← -{r['n']:>2d}.jpg  ({size_mb:5.1f} MB)  → {r['master_name']}")

    # ── R2 plan
    print(f"\n── R2 upload plan ──")
    print(f"  Folder:  {R2}/{COLL_DIR}/{{masters,previews,thumbs,large}}")
    print(f"  Masters (byte-for-byte): {len(rows)} JPGs (~{total_mb:.0f} MB)")
    print(f"  Tiers (sips → sRGB JPEG): {len(rows)*3} JPEGs"
          f"  (thumb 600/75, prev 2000/82, large 3840/85)")

    # ── claim shape (illustrative)
    print(f"\n── Wikibase claim shape (uniform across all 45) ──")
    sample = rows[0]
    print(f"  label:  {LABEL!r}")
    print(f"  desc:   {description_for(sample)!r}    (varies by HH-IHC-NNNN)")
    print(f"  P1  = {PHOTOGRAPH_QID}   (photograph)")
    print(f"  P2  = HH-IHC-NNNN")
    print(f"  P79 = {SOURCE_COLLECTION_QID}  (Ivan Hunter Collection)")
    print(f"  P80 = {CREATOR_QID}  (Ivan Hunter)")
    print(f"  P82 = +{CAPTURE_DATE.strftime('%Y-%m-%d')}  precision /11 (day)")
    print(f"  P85 = {DEPICTS_QID}  (Hunter Residence)")
    print(f"  P95 = {sample['master_url']}")
    print(f"  P96 = {sample['preview_url']}")
    print(f"  (no P62 phase, no P86 set-position, no P88 drawing-type, no notes)")

    # ── dry-run preview
    if not EXECUTE:
        print(f"\n── DRY RUN: building preview tier of first item ──")
        shutil.rmtree(WORK, ignore_errors=True)
        os.makedirs(WORK, exist_ok=True)
        first = rows[0]
        out = os.path.join(WORK, f"{first['id']}_{SLUG_BASE}_large.jpg")
        sips_jpeg(first["source"], out, 3840, 85)
        desktop = os.path.expanduser(f"~/Desktop/IHC_PREVIEW_{first['id']}.jpg")
        shutil.copy(out, desktop)
        subprocess.run(["open", desktop], check=False)
        print(f"  Preview tier on Desktop: {desktop}")
        print(f"\nDRY RUN complete. Re-run with --execute to write R2 + Wikibase.")
        return

    # ── EXECUTE ─────────────────────────────────────────────────────────────
    print("\n══════════════════ EXECUTE ══════════════════\n")
    wb = WikibaseSession(user_agent="HunterHouseBot/1.0 (batch_ingest_ihc)")
    print(f"  logged in to Wikibase")

    shutil.rmtree(WORK, ignore_errors=True)
    os.makedirs(WORK, exist_ok=True)
    results = []
    for i, r in enumerate(rows, 1):
        print(f"\n  ({i}/{len(rows)}) {r['id']}")
        # Resume idempotency: if a Wikibase item with this P2 already exists
        # from a previous run, skip both R2 (rclone is also idempotent on its
        # own, but skipping here saves the sips work) and the Wikibase write.
        existing = wb_find_by_p2(wb, r["id"])
        if existing:
            print(f"     SKIP — already in Wikibase as {existing}")
            results.append((r["id"], existing))
            continue
        # Build tiers
        tier_files = {}
        for suffix, (px, quality) in TIERS.items():
            out = os.path.join(WORK, f"{r['id']}_{SLUG_BASE}{suffix}")
            sips_jpeg(r["source"], out, px, quality)
            tier_files[suffix] = out
        # R2: master byte-for-byte, then tiers. rclone copy/copyto skip if
        # the dest exists with matching size+modtime, so partial R2 state
        # from an aborted run is also handled.
        run(["rclone", "copyto", r["source"], f"{R2_MASTERS}/{r['master_name']}"])
        run(["rclone", "copy", tier_files["_thumb.jpg"], R2_THUMBS  + "/"])
        run(["rclone", "copy", tier_files["_prev.jpg"],  R2_PREVIEWS + "/"])
        run(["rclone", "copy", tier_files["_large.jpg"], R2_LARGE   + "/"])
        # Wikibase item
        qid = wb_create_item(
            wb,
            labels={"en": LABEL},
            descriptions={"en": description_for(r)},
            claims=build_item_claims(r),
        )
        print(f"     R2 uploaded · Wikibase {qid}")
        results.append((r["id"], qid))
        # Fail-safe sidecar push (matches batch_ingest_egc pattern)
        try:
            subprocess.run(
                ["python3", os.path.join(os.path.dirname(__file__),
                                         "sync_one_metadata.py"),
                 r["id"], "--execute", "--quiet"],
                timeout=60, check=False,
            )
        except Exception as _e:
            print(f"     ⚠ sidecar sync skipped (non-fatal): {_e}")

    shutil.rmtree(WORK, ignore_errors=True)

    print(f"\n══════════════════ DONE ══════════════════")
    for arch_id, qid in results:
        print(f"  {arch_id}  {qid}  https://hunterhouse.wikibase.cloud/wiki/Item:{qid}")


if __name__ == "__main__":
    main()
