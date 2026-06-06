#!/usr/bin/env python3
"""
Batch ingest the Eric Gesinger Collection (EGC) from EGC_intake.xlsx + the
source TIFs in the Downloads folder into R2 + Wikibase.

Model = scripts/ingest_item.py, but driven by the workbook so all 30 drawings
get ingested in one pass. Phases + missing drawing-type vocab are minted once
upfront (not per row).

Dry-run by default: prints the full per-row plan, the vocab to mint, and the
Q182 cleanup; does no writes. `--execute` performs:
  1. Q182 label/desc typo fix + EGC alias
  2. Mint missing drawing-type vocab (axonometric)
  3. Mint all 9 EGC phase items (P1=Q2)
  4. For each row: build 3 web tiers via sips (sRGB baked), upload master
     byte-for-byte + tiers to R2, create Wikibase item with claims.

Idempotent vocab resolve: phases matched by label + P1=Q2; drawing-types by
hard-coded QID map. Re-running --execute would create duplicate archive items
(items don't dedupe by P2 here) — only run --execute once.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import openpyxl
import requests

# ─────────────────────────── paths ──────────────────────────────────────────
WORKBOOK   = "/Users/brandonpoole/Projects/HunterHouse/EGC_intake.xlsx"
SCANS_ROOT = "/Users/brandonpoole/Downloads/237659_Brandon Poole_203 Goward Rd_Scans_14May26"
WORK       = "/tmp/hh_egc_ingest"

# ─────────────────────────── R2 ─────────────────────────────────────────────
R2          = "hh-r2:hunter-house-archive"
COLL_DIR    = "eric-gesinger-collection"
PUBLIC_BASE = "https://archive.hunterhousefoundation.com"
R2_MASTERS  = f"{R2}/{COLL_DIR}/masters"
R2_THUMBS   = f"{R2}/{COLL_DIR}/thumbs"
R2_PREVIEWS = f"{R2}/{COLL_DIR}/previews"
R2_LARGE    = f"{R2}/{COLL_DIR}/large"

# ─────────────────────────── Wikibase ───────────────────────────────────────
API      = "https://hunterhouse.wikibase.cloud/w/api.php"
ENV_FILE = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")
CALENDAR = "http://www.wikidata.org/entity/Q1985727"

SOURCE_COLLECTION_QID = "Q182"   # EGC source collection (label fix below)
CREATOR_QID           = "Q201"   # Richard Hunter
DRAWING_QID           = "Q88"    # P1 instance-of for drawings
PHASE_P1_QID          = "Q2"     # instance-of for phases

# Existing drawing-type vocab (hard-coded — drawing types don't carry P1 in
# this Wikibase, so we can't auto-resolve by P1 filter)
DRAWING_TYPE_MAP = {
    "plan":        "Q98",
    "elevation":   "Q99",
    "section":     "Q100",
    "detail":      "Q101",
    "axonometric": "Q493",  # minted 2026-05-20 (initial batch run)
}

# Tier recipes
TIERS = {
    "_thumb.jpg": (600, 75),
    "_prev.jpg":  (2000, 82),
    "_large.jpg": (3840, 85),
}

EXECUTE = "--execute" in sys.argv


# ─────────────────────────── helpers ────────────────────────────────────────
def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


def sips_jpeg(src, dst, max_px, quality):
    run(["sips", "-Z", str(max_px),
         "-m", "/System/Library/ColorSync/Profiles/sRGB Profile.icc",
         "-s", "format", "jpeg",
         "-s", "formatOptions", str(quality), src, "--out", dst],
        capture_output=True)


def slugify(title, date):
    s = re.sub(r"[^A-Za-z0-9 ]+", " ", title or "")
    s = "".join(w.capitalize() for w in s.split())
    if isinstance(date, datetime):
        return f"{s}_{date.year}"
    return f"{s}_nd"


def parse_drawtypes(s):
    if not s: return []
    return [p.strip().lower() for p in s.split(";") if p.strip()]


# ─────────────────────────── workbook + disk ────────────────────────────────
def build_folder_index():
    idx = {}
    for folder in Path(SCANS_ROOT).iterdir():
        if not folder.is_dir(): continue
        for f in folder.iterdir():
            if f.suffix.lower() == ".tif":
                idx[f.name] = str(f)
    return idx


def load_rows():
    folder_idx = build_folder_index()
    wb = openpyxl.load_workbook(WORKBOOK, data_only=True)
    ws = wb["Catalogue"]
    rows = []
    for r in ws.iter_rows(min_row=2, values_only=True):
        if not r[0]: continue
        rec = {
            "id":       r[0],
            "filename": r[1],
            "type":     r[2],
            "title":    r[3],
            "phase":    r[4],
            "set_pos":  r[5],
            "date":     r[6],
            "date_precision": r[7],
            "drawtypes": parse_drawtypes(r[11]),
            "source":   folder_idx.get(r[1]),
        }
        rec["slug"] = slugify(rec["title"], rec["date"])
        rec["master_name"] = f"{rec['id']}_{rec['slug']}.tif"
        rec["preview_url"] = f"{PUBLIC_BASE}/{COLL_DIR}/previews/{rec['id']}_{rec['slug']}_prev.jpg"
        rec["master_url"]  = f"{PUBLIC_BASE}/{COLL_DIR}/masters/{rec['master_name']}"
        rows.append(rec)
    return rows


# ─────────────────────────── Wikibase write helpers ─────────────────────────
def wb_login(s, user, pw):
    t = s.get(API, params={"action":"query","meta":"tokens","type":"login","format":"json"}
              ).json()["query"]["tokens"]["logintoken"]
    r = s.post(API, data={"action":"login","lgname":user,"lgpassword":pw,
                          "lgtoken":t,"format":"json"}).json()
    if r["login"]["result"] != "Success":
        raise SystemExit(f"Login failed: {r['login']['result']}")
    print(f"  logged in as {r['login']['lgusername']}")


def wb_csrf(s):
    return s.get(API, params={"action":"query","meta":"tokens","format":"json"}
                 ).json()["query"]["tokens"]["csrftoken"]


def wb_find_phase(s, label):
    """Find an item with en label == label AND P1 = Q2 (phase)."""
    r = s.get(API, params={"action":"wbsearchentities","search":label,
                           "language":"en","type":"item","limit":25,
                           "format":"json"}).json()
    candidates = [h["id"] for h in r.get("search",[])
                  if (h.get("label") or "").strip().lower() == label.strip().lower()]
    if not candidates: return None
    ents = s.get(API, params={"action":"wbgetentities","ids":"|".join(candidates),
                              "props":"claims","format":"json"}
                 ).json().get("entities",{})
    for q in candidates:
        for c in ents.get(q,{}).get("claims",{}).get("P1",[]):
            v = c.get("mainsnak",{}).get("datavalue",{}).get("value",{})
            if isinstance(v,dict) and v.get("id") == PHASE_P1_QID:
                return q
    return None


def wb_create_item(s, token, labels, descriptions, claims, aliases=None):
    data = {
        "labels":       {l:{"language":l,"value":v} for l,v in labels.items()},
        "descriptions": {l:{"language":l,"value":v} for l,v in descriptions.items()},
        "claims": claims,
    }
    if aliases:
        data["aliases"] = {l:[{"language":l,"value":a} for a in vs] for l,vs in aliases.items()}
    r = s.post(API, data={"action":"wbeditentity","new":"item",
                          "data":json.dumps(data),"token":token,
                          "format":"json"}).json()
    if "error" in r: raise SystemExit(f"item create failed: {r['error']}")
    return r["entity"]["id"]


def wb_edit_item(s, token, qid, labels=None, descriptions=None, aliases=None, claims=None):
    data = {}
    if labels:       data["labels"]       = {l:{"language":l,"value":v} for l,v in labels.items()}
    if descriptions: data["descriptions"] = {l:{"language":l,"value":v} for l,v in descriptions.items()}
    if aliases:      data["aliases"]      = {l:[{"language":l,"value":a} for a in vs] for l,vs in aliases.items()}
    if claims:       data["claims"]       = claims
    r = s.post(API, data={"action":"wbeditentity","id":qid,
                          "data":json.dumps(data),"token":token,
                          "format":"json"}).json()
    if "error" in r: raise SystemExit(f"item edit failed: {r['error']}")
    return r["entity"]["id"]


def claim(pid, datatype, value):
    if datatype == "wikibase-item":
        dv = {"value":{"entity-type":"item","id":value},"type":"wikibase-entityid"}
    elif datatype == "time-day":
        # value = datetime
        dv = {"value":{"time": value.strftime("+%Y-%m-%dT00:00:00Z"),
                       "timezone":0,"before":0,"after":0,"precision":11,
                       "calendarmodel":CALENDAR},"type":"time"}
    elif datatype == "time-year":
        dv = {"value":{"time": f"+{value}-00-00T00:00:00Z",
                       "timezone":0,"before":0,"after":0,"precision":9,
                       "calendarmodel":CALENDAR},"type":"time"}
    else:
        dv = {"value": value, "type":"string"}
    return {"mainsnak":{"snaktype":"value","property":pid,"datavalue":dv},
            "type":"statement","rank":"normal"}


# ─────────────────────────── per-row claim builder ──────────────────────────
def build_item_claims(row, phase_qid, drawtype_qid_map, total_in_phase):
    claims = [
        claim("P1",  "wikibase-item", DRAWING_QID),
        claim("P2",  "string",        row["id"]),
        claim("P62", "wikibase-item", phase_qid),
        claim("P79", "wikibase-item", SOURCE_COLLECTION_QID),
        claim("P80", "wikibase-item", CREATOR_QID),
        claim("P95", "url",           row["master_url"]),
        claim("P96", "url",           row["preview_url"]),
    ]
    # Date (P82) — only if dated; full day precision
    if isinstance(row["date"], datetime):
        claims.append(claim("P82", "time-day", row["date"]))
    # Set position (P86)
    if row["set_pos"]:
        sp = f"{int(row['set_pos']):02d} of {total_in_phase:02d}"
        claims.append(claim("P86", "string", sp))
    # Drawing types (P88)
    for dt in row["drawtypes"]:
        q = drawtype_qid_map.get(dt)
        if q: claims.append(claim("P88", "wikibase-item", q))
    return claims


def description_for(row):
    yr = row["date"].year if isinstance(row["date"], datetime) else "n.d."
    # Include ID for Wikibase (label, description) uniqueness — many items
    # share the same label+year (Owl Chair #1 × 3, Channel Chair × 3, etc.)
    return f"drawing; EGC; {row['id']}; {yr}"


def wb_find_by_p2(s, arch_id):
    """Return QID of an existing item with this P2 archive ID, else None."""
    r = s.get(API, params={"action":"wbsearchentities","search":arch_id,
                           "language":"en","type":"item","limit":10,
                           "format":"json"}).json()
    candidates = [h["id"] for h in r.get("search",[])]
    if not candidates: return None
    ents = s.get(API, params={"action":"wbgetentities","ids":"|".join(candidates),
                              "props":"claims","format":"json"}
                 ).json().get("entities",{})
    for q in candidates:
        for c in ents.get(q,{}).get("claims",{}).get("P2",[]):
            v = c.get("mainsnak",{}).get("datavalue",{}).get("value")
            if v == arch_id:
                return q
    return None


# ─────────────────────────── main ───────────────────────────────────────────
def main():
    rows = load_rows()
    print(f"\n{'EXECUTE' if EXECUTE else 'DRY RUN'} — EGC batch ingest ({len(rows)} items)\n")

    # ── pre-flight: all source files present?
    missing = [r for r in rows if not r["source"] or not os.path.isfile(r["source"])]
    if missing:
        print(f"!! {len(missing)} source TIFs MISSING:")
        for r in missing: print(f"   {r['id']}  filename={r['filename']!r}")
        raise SystemExit("Aborting — resolve missing sources first.")
    print(f"✓ all {len(rows)} source TIFs found on disk")

    # ── phase counts (for P86)
    from collections import Counter
    phase_counts = Counter(r["phase"] for r in rows)
    phases_to_mint = sorted(set(r["phase"] for r in rows))

    # ── drawing types in use
    used_drawtypes = set()
    for r in rows: used_drawtypes.update(r["drawtypes"])

    # ── per-row manifest
    print(f"\n── Per-item manifest ──")
    for r in rows:
        d = r["date"].strftime("%Y-%m-%d") if isinstance(r["date"], datetime) else "n.d."
        sp = f"{int(r['set_pos']):02d}/{phase_counts[r['phase']]:02d}" if r["set_pos"] else "  —"
        dtypes = ",".join(r["drawtypes"]) or "—"
        size_mb = os.path.getsize(r["source"]) / 1e6
        print(f"  {r['id']}  {sp}  {d}  «{r['phase']:<40s}»  «{r['title']:<45s}»  draw=[{dtypes}]  src={size_mb:.0f}MB")

    # ── vocab plan
    print(f"\n── Vocab mint plan ──")
    print(f"  Q182 cleanup: fix label/desc typo Gesinger→Gesinger + add 'EGC' alias")
    print(f"  Drawing types in use: {sorted(used_drawtypes)}")
    print(f"  Existing QIDs (reuse): " + ", ".join(f"{k}={DRAWING_TYPE_MAP[k]}" for k in sorted(used_drawtypes) if DRAWING_TYPE_MAP.get(k)))
    mint_dts = [dt for dt in used_drawtypes if not DRAWING_TYPE_MAP.get(dt)]
    print(f"  Drawing-type items to MINT: {mint_dts}")
    print(f"  Phase items to MINT (all 9 — none exist):")
    for p in phases_to_mint:
        n = phase_counts[p]
        print(f"    • «{p}»  ({n} items)")

    # ── R2 upload plan
    print(f"\n── R2 upload plan ──")
    n_masters = len(rows)
    n_tiers = len(rows) * 3
    print(f"  Folder: {R2}/{COLL_DIR}/{{masters,previews,thumbs,large}}")
    print(f"  Masters (byte-for-byte): {n_masters} TIFs")
    print(f"  Tiers (sips → sRGB JPEG): {n_tiers} JPEGs (thumb 600/75, prev 2000/82, large 3840/85)")
    total_mb = sum(os.path.getsize(r["source"]) for r in rows) / 1e6
    print(f"  Master upload total: ~{total_mb:.0f} MB")

    # ── claim shape preview (first row)
    print(f"\n── Claim shape (first row, illustrative) ──")
    sample = rows[0]
    print(f"  {sample['id']}  «{sample['title']}»")
    print(f"  label: {sample['title']!r}")
    print(f"  desc:  {description_for(sample)!r}")
    print(f"  P1=Q88 (drawing), P2={sample['id']}, P62=<phase QID>, P79=Q182, P80=Q201")
    if isinstance(sample['date'], datetime):
        print(f"  P82 = +{sample['date'].strftime('%Y-%m-%d')} precision /11 (day)")
    else:
        print(f"  P82 = (skipped — undated)")
    if sample['set_pos']:
        sp = f"{int(sample['set_pos']):02d} of {phase_counts[sample['phase']]:02d}"
        print(f"  P86 = {sp!r}")
    print(f"  P88 = {sample['drawtypes']} → multi-value")
    print(f"  P95 = {sample['master_url']}")
    print(f"  P96 = {sample['preview_url']}")

    # ── dry-run preview of first tier
    if not EXECUTE:
        print(f"\n── DRY RUN: building preview of first item ──")
        shutil.rmtree(WORK, ignore_errors=True)
        os.makedirs(WORK, exist_ok=True)
        first = rows[0]
        out = os.path.join(WORK, f"{first['id']}_{first['slug']}_large.jpg")
        sips_jpeg(first["source"], out, 3840, 85)
        desktop = os.path.expanduser(f"~/Desktop/EGC_PREVIEW_{first['id']}.jpg")
        shutil.copy(out, desktop)
        subprocess.run(["open", desktop], check=False)
        print(f"  Preview tier for {first['id']} on Desktop: {desktop}")
        print(f"\nDRY RUN complete. Re-run with --execute to write all R2 + Wikibase.")
        return

    # ── EXECUTE ─────────────────────────────────────────────────────────────
    print("\n══════════════════ EXECUTE ══════════════════\n")
    s = requests.Session()
    s.headers.update({"User-Agent":"HunterHouseBot/1.0 (batch_ingest_egc)"})
    env = load_env(ENV_FILE)
    wb_login(s, env["WIKIBASE_BOT_USER"], env["WIKIBASE_BOT_PASSWORD"])
    token = wb_csrf(s)

    # 1. Fix Q182
    print("\n[1/4] Q182 cleanup")
    wb_edit_item(s, token, SOURCE_COLLECTION_QID,
                 labels={"en":"Eric Gesinger Collection"},
                 descriptions={"en":"personal archival collection of Eric Gesinger"},
                 aliases={"en":["EGC","GES"]})
    print("  Q182 updated.")

    # 2. Mint drawing-type items missing from map (axonometric)
    print("\n[2/4] Mint missing drawing-type vocab")
    dt_qid_map = dict(DRAWING_TYPE_MAP)
    for dt in sorted(used_drawtypes):
        if dt_qid_map.get(dt): continue
        qid = wb_create_item(
            s, token,
            labels={"en":dt},
            descriptions={"en":f"drawing type: {dt} projection"},
            claims=[]
        )
        dt_qid_map[dt] = qid
        print(f"  drawing-type «{dt}» → {qid}  (CREATED)")

    # 3. Mint phase items (P1=Q2)
    print("\n[3/4] Mint phase items")
    phase_qid_map = {}
    for p in phases_to_mint:
        existing = wb_find_phase(s, p)
        if existing:
            phase_qid_map[p] = existing
            print(f"  phase «{p}» → {existing}  (reused)")
            continue
        qid = wb_create_item(
            s, token,
            labels={"en":p},
            descriptions={"en":f"phase: {p} (EGC)"},
            claims=[claim("P1","wikibase-item",PHASE_P1_QID)]
        )
        phase_qid_map[p] = qid
        print(f"  phase «{p}» → {qid}  (CREATED)")

    # 4. Per-row: tiers → R2 → Wikibase item
    print(f"\n[4/4] Per-item ingest ({len(rows)} items)")
    shutil.rmtree(WORK, ignore_errors=True)
    os.makedirs(WORK, exist_ok=True)
    results = []
    for i, r in enumerate(rows, 1):
        print(f"\n  ({i}/{len(rows)}) {r['id']}  «{r['title']}»")
        # Idempotency: if an item with this P2 already exists, skip the
        # Wikibase write but still ensure description matches the canonical
        # format and re-run the R2 upload (rclone skips identical).
        existing = wb_find_by_p2(s, r["id"])
        # tiers
        tier_files = {}
        for suffix,(px,quality) in TIERS.items():
            out = os.path.join(WORK, f"{r['id']}_{r['slug']}{suffix}")
            sips_jpeg(r["source"], out, px, quality)
            tier_files[suffix] = out
        # R2: master byte-for-byte
        run(["rclone","copyto", r["source"], f"{R2_MASTERS}/{r['master_name']}"])
        # tiers
        run(["rclone","copy", tier_files["_thumb.jpg"], R2_THUMBS + "/"])
        run(["rclone","copy", tier_files["_prev.jpg"],  R2_PREVIEWS + "/"])
        run(["rclone","copy", tier_files["_large.jpg"], R2_LARGE + "/"])
        # Wikibase item
        if existing:
            # Update description to canonical format (in case it was created
            # with an earlier format that collided on (label, description)).
            wb_edit_item(s, token, existing,
                         descriptions={"en": description_for(r)})
            qid = existing
            print(f"     R2 uploaded · Wikibase {qid}  (existed; desc updated)")
        else:
            claims = build_item_claims(r, phase_qid_map[r["phase"]], dt_qid_map,
                                       phase_counts[r["phase"]])
            qid = wb_create_item(
                s, token,
                labels={"en":r["title"]},
                descriptions={"en":description_for(r)},
                claims=claims
            )
            print(f"     R2 uploaded · Wikibase {qid}")
        results.append((r["id"], qid))
        # §11.1 HIGH part 2b — fail-safe metadata sidecar push to R2 for
        # every item we touched this batch (both the "created" and
        # "existed; desc updated" branches reach this line). A sidecar
        # glitch never breaks the batch.
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

    # Static permalink pages (best-effort, full rebuild). WDQS lags batch
    # creation, so freshly-created items may only appear on a re-run —
    # `python3 scripts/build_item_pages.py` is also the session-end step that
    # syncs ANY catalogue change (edits included).
    try:
        subprocess.run(
            ["python3", os.path.join(os.path.dirname(__file__), "build_item_pages.py")],
            timeout=300, check=False,
        )
    except Exception as _e:
        print(f"  ⚠ permalink page generation skipped (non-fatal): {_e}")

    print(f"\n══════════════════ DONE ══════════════════")
    for arch_id, qid in results:
        print(f"  {arch_id}  {qid}  https://hunterhouse.wikibase.cloud/wiki/Item:{qid}")


if __name__ == "__main__":
    main()
