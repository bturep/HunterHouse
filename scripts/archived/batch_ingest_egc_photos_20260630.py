#!/usr/bin/env python3
"""
Batch ingest the EGC photograph set (Mary McNeill Knowles, 2023) + one late
Hunter stool drawing into R2 + Wikibase.

Model = batch_ingest_egc.py, but the manifest is embedded (no workbook) and it
handles TWO genres:

  • STUDIO / OBJECT photos  → depict a Gesinger furniture piece. Label = the
    piece; P62 = the piece's project phase (so the photo groups with its
    drawings under "In the graph"); P140 Gesinger (maker) + P141 Hunter
    (designer) + P145 Furniture.
  • INTERIOR / SPACE photos → document a room. Label = the room; P87 area only;
    P141 Hunter (designed the house); NO phase / NO P140 / NO P145 — they
    cross-reference Hunter's own HHC drawings of that room by subject/search.

Plus one DRAWING: Hunter's additional "Stool" sheet (2018-10-26), mirroring the
existing Stool drawing (Q527).

Photographer = Mary McNeill Knowles (Q586, minted 2026-06-30).
Dates: read per-photo from EXIF (DateTimeOriginal, day precision); photos whose
EXIF was stripped on re-export fall back to year-precision 2023 (the shoot year).

Dry-run by default (prints manifest + builds one preview tier to /tmp). Pass
--execute to write R2 + Wikibase. NOT idempotent on the archive items (no P2
dedupe) — run --execute once.
"""

import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wikibase import WikibaseSession  # noqa: E402

try:
    from PIL import Image, ExifTags
    _DTO = {v: k for k, v in ExifTags.TAGS.items()}["DateTimeOriginal"]
    _DTD = {v: k for k, v in ExifTags.TAGS.items()}["DateTimeDigitized"]
except Exception:
    Image = None

EXECUTE = "--execute" in sys.argv

# ─────────────────────────── R2 ─────────────────────────────────────────────
R2          = "hh-r2:hunter-house-archive"
COLL_DIR    = "eric-gesinger-collection"
PUBLIC_BASE = "https://archive.hunterhousefoundation.com"
R2_MASTERS  = f"{R2}/{COLL_DIR}/masters"
R2_THUMBS   = f"{R2}/{COLL_DIR}/thumbs"
R2_PREVIEWS = f"{R2}/{COLL_DIR}/previews"
R2_LARGE    = f"{R2}/{COLL_DIR}/large"
WORK        = "/tmp/hh_egc_photos_ingest"

# ─────────────────────────── QIDs ───────────────────────────────────────────
CALENDAR   = "http://www.wikidata.org/entity/Q1985727"
EGC        = "Q182"   # source collection
HUNTER     = "Q201"   # designer / draughtsman
GESINGER   = "Q209"   # maker
KNOWLES    = "Q586"   # photographer (minted 2026-06-30)
FURNITURE  = "Q535"   # category
PHOTO      = "Q89"    # instance of: photograph
DRAWING    = "Q88"    # instance of: drawing
AREA_DINING = "Q300"
AREA_LIVING = "Q299"
AREA_POWDER = "Q465"  # Powder Room, East Wing
PH_DINCHAIR = "Q495"  # Dining Room Table and Chairs
PH_STOOL    = "Q497"  # Stool project (was "Living Room Side Table")
PH_CHANNEL  = "Q494"  # Channel Chair and Ottoman

# ─────────────────────────── genres ─────────────────────────────────────────
GENRES = {
    "dining_interior": dict(
        label="Dining Room", area=AREA_DINING, phase=None, obj=False,
        note="Interior view of the East Wing dining room, Hunter Residence."),
    "dining_chair": dict(
        label="Dining Room Chair", area=AREA_DINING, phase=PH_DINCHAIR, obj=True,
        note="Studio photograph of Eric Gesinger's dining room chair, made to "
             "Richard Hunter's design for the Hunter Residence."),
    "stool": dict(
        label="Stool", area=AREA_LIVING, phase=PH_STOOL, obj=True,
        note="Studio photograph of Eric Gesinger's stool, made to Richard "
             "Hunter's design for the Hunter Residence."),
    "powder": dict(
        label="Powder Room", area=AREA_POWDER, phase=None, obj=False,
        note="Interior view of the powder room in the East Wing dining-room "
             "addition, Hunter Residence."),
    "channel": dict(
        label="Channel Chair, Living Room", area=AREA_LIVING, phase=PH_CHANNEL, obj=True,
        note="Interior view: Eric Gesinger's channel chair in the living room "
             "of the Hunter Residence."),
    "ottoman": dict(
        label="Channel Chair Ottoman, Living Room", area=AREA_LIVING, phase=PH_CHANNEL, obj=True,
        note="Interior view: Eric Gesinger's channel-chair ottoman in the "
             "living room of the Hunter Residence."),
}

PHOTO_DIR = "/Users/brandonpoole/Downloads/high resolution finished/Keep"
# (filename, genre) in ls order → arch IDs HH-EGC-0032 … 0059
PHOTOS = [
    ("01-GesingerInteriors dinig room.jpg",               "dining_interior"),
    ("04-GesingerInteriors_dinig room.jpg",               "dining_interior"),
    ("07-GesingerInteriors_dinig room.jpg",               "dining_interior"),
    ("13-GesingerInteriors_dinig room.jpg",               "dining_interior"),
    ("17-GesingerInteriors_dinig room.jpg",               "dining_interior"),
    ("18-GesingerStudio_Dining Room chair_dining room.jpg","dining_chair"),
    ("20-GesingerInteriors_dinig room.jpg",               "dining_interior"),
    ("21-GesingerInteriors_dinig room.jpg",               "dining_interior"),
    ("22-GesingerStudio_dining room chair.jpg",           "dining_chair"),
    ("23-GesingerStudio_Stool_kitchen.jpg",               "stool"),
    ("24-GesingerStudio_STOOL.jpg",                       "stool"),
    ("25-GesingerInteriors_dinig room.jpg",               "dining_interior"),
    ("26-GesingerInteriors_dinig room.jpg",               "dining_interior"),
    ("26-GesingerStudio_STOOL.jpg",                       "stool"),
    ("27-GesingerInteriors_bathroom.jpg",                 "powder"),
    ("27-GesingerStudioStool.jpg",                        "stool"),
    ("28-GesingerInteriors_bathroom.jpg",                 "powder"),
    ("28-GesingerStudio_Stool.jpg",                       "stool"),
    ("29-GesingerInteriors_dining room.jpg",              "dining_interior"),
    ("32-GesingerInteriors_channel chair.jpg",            "channel"),
    ("34-GesingerInteriors_channel chair_ Living room.jpg","channel"),
    ("41-GesingerInteriors_channel chair foot stool.jpg", "ottoman"),
    ("43-GesingerInteriors_channel chair.jpg",            "channel"),
    ("44-GesingerInteriors_channel chair.jpg",            "channel"),
    ("45-GesingerInteriors_channel chair.jpg",            "channel"),
    ("48-GesingerStudio_side.jpg",                        "stool"),
    ("49-GesingerStudio_didining room chair.jpg",         "dining_chair"),
    ("50-GesingerStudio_diing room chair.jpg",            "dining_chair"),
]

STOOL_DRAWING = dict(
    src="/Users/brandonpoole/Desktop/Frances Hunter Archive/Letters/EGC_additional, stool.tif",
    arch_id="HH-EGC-0031", label="Stool", date="2018-10-26",
)

TIERS = {"_thumb.jpg": (600, 75), "_prev.jpg": (2000, 82), "_large.jpg": (3840, 85)}


# ─────────────────────────── helpers ────────────────────────────────────────
def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True)


def sips_jpeg(src, dst, max_px, quality):
    # never upscale — clamp the tier to the source's native long side, so a
    # 1024×1536 web-preview master yields prev/large at native res, not blurred-up
    try:
        w, h = Image.open(src).size
        max_px = min(max_px, max(w, h))
    except Exception:
        pass
    run(["sips", "-Z", str(max_px),
         "-m", "/System/Library/ColorSync/Profiles/sRGB Profile.icc",
         "-s", "format", "jpeg", "-s", "formatOptions", str(quality),
         src, "--out", dst])


def slugify(title, year):
    s = re.sub(r"[^A-Za-z0-9 ]+", " ", title or "")
    s = "".join(w.capitalize() for w in s.split())
    return f"{s}_{year}"


def exif_date(path):
    """Return 'YYYY-MM-DD' from EXIF, else None."""
    if Image is None:
        return None
    try:
        ex = Image.open(path)._getexif() or {}
    except Exception:
        return None
    v = ex.get(_DTO) or ex.get(_DTD)
    if not v:
        return None
    return v[:10].replace(":", "-")


def claim(pid, dtype, value):
    if dtype == "item":
        dv = {"value": {"entity-type": "item", "id": value}, "type": "wikibase-entityid"}
    elif dtype == "day":
        dv = {"value": {"time": f"+{value}T00:00:00Z", "timezone": 0, "before": 0,
                        "after": 0, "precision": 11, "calendarmodel": CALENDAR}, "type": "time"}
    elif dtype == "year":
        dv = {"value": {"time": f"+{value}-00-00T00:00:00Z", "timezone": 0, "before": 0,
                        "after": 0, "precision": 9, "calendarmodel": CALENDAR}, "type": "time"}
    else:
        dv = {"value": value, "type": "string"}
    return {"mainsnak": {"snaktype": "value", "property": pid, "datavalue": dv},
            "type": "statement", "rank": "normal"}


def build_manifest():
    items = []
    # 1. the stool drawing → HH-EGC-0031
    d = STOOL_DRAWING
    yr = d["date"][:4]
    slug = slugify(d["label"], yr)
    items.append(dict(
        kind="drawing", genre="(stool drawing)", src=d["src"], arch_id=d["arch_id"],
        label=d["label"], area=AREA_LIVING, phase=PH_STOOL, obj=True,
        date=d["date"], date_prec="day",
        note="Richard Hunter's drawing of the stool later made by Eric Gesinger.",
        master_name=f"{d['arch_id']}_{slug}.tif", slug=slug))
    # 2. the 28 photos → HH-EGC-0032 … 0059
    for i, (fn, genre) in enumerate(PHOTOS):
        arch = f"HH-EGC-{32 + i:04d}"
        g = GENRES[genre]
        src = os.path.join(PHOTO_DIR, fn)
        dt = exif_date(src)
        if dt:
            date, prec = dt, "day"
        else:
            date, prec = "2023", "year"
        slug = slugify(g["label"], "2023")
        items.append(dict(
            kind="photo", genre=genre, src=src, arch_id=arch, label=g["label"],
            area=g["area"], phase=g["phase"], obj=g["obj"], date=date, date_prec=prec,
            note=g["note"], master_name=f"{arch}_{slug}.jpg", slug=slug, srcfn=fn))
    return items


def build_claims(it):
    is_photo = it["kind"] == "photo"
    master_url = f"{PUBLIC_BASE}/{COLL_DIR}/masters/{it['master_name']}"
    prev_url = f"{PUBLIC_BASE}/{COLL_DIR}/previews/{it['arch_id']}_{it['slug']}_prev.jpg"
    cl = [
        claim("P1", "item", PHOTO if is_photo else DRAWING),
        claim("P2", "string", it["arch_id"]),
        claim("P79", "item", EGC),
        claim("P80", "item", KNOWLES if is_photo else HUNTER),
        claim("P95", "url", master_url),
        claim("P96", "url", prev_url),
        claim("P82", it["date_prec"], it["date"]),
    ]
    if it["phase"]:
        cl.append(claim("P62", "item", it["phase"]))
    if it["area"]:
        cl.append(claim("P87", "item", it["area"]))
    # designer / maker attribution on the depicted furniture
    if it["obj"]:
        cl.append(claim("P141", "item", HUNTER))     # designed by
        cl.append(claim("P140", "item", GESINGER))   # made by
        cl.append(claim("P145", "item", FURNITURE))  # category
    elif is_photo:
        cl.append(claim("P141", "item", HUNTER))     # interior: Hunter designed the space
    if it.get("note"):
        cl.append(claim("P100", "string", it["note"]))
    return cl, master_url, prev_url


def description_for(it):
    yr = it["date"][:4]
    kind = "photograph" if it["kind"] == "photo" else "drawing"
    return f"{kind}; EGC; {it['arch_id']}; {yr}"


# ─────────────────────────── main ───────────────────────────────────────────
def main():
    items = build_manifest()
    print(f"\n{'EXECUTE' if EXECUTE else 'DRY RUN'} — EGC photo batch ({len(items)} items)\n")

    missing = [it for it in items if not os.path.isfile(it["src"])]
    if missing:
        for it in missing:
            print(f"  !! MISSING {it['arch_id']}  {it['src']}")
        raise SystemExit("Aborting — resolve missing sources.")
    print(f"✓ all {len(items)} source files present\n")

    from collections import Counter
    gc = Counter(it["genre"] for it in items)
    print("── Manifest ──")
    for it in items:
        obj = "OBJ" if it["obj"] else "spc"
        ph = it["phase"] or "—"
        mb = os.path.getsize(it["src"]) / 1e6
        print(f"  {it['arch_id']}  {it['kind']:7} {obj}  P82={it['date']:<10}({it['date_prec'][:3]})  "
              f"area={it['area']} phase={ph:5}  «{it['label']:<28}»  {mb:4.0f}MB  {it.get('srcfn','')[:34]}")
    print("\n── Genre counts ──")
    for g, n in sorted(gc.items()):
        print(f"  {g:16} {n}")
    print(f"\n  Photographer P80 = {KNOWLES} (Knowles) on photos; Hunter on the drawing.")
    print(f"  Object shots: +P140 Gesinger +P141 Hunter +P145 Furniture +P62 phase")
    print(f"  Interiors:    +P141 Hunter only (cross-ref HHC room drawings by subject)")

    total_mb = sum(os.path.getsize(it["src"]) for it in items) / 1e6
    print(f"\n── R2: {len(items)} masters + {len(items)*3} tiers (~{total_mb:.0f}MB masters) ──")

    # sample claim
    s0 = items[1]  # first photo
    cl, mu, pu = build_claims(s0)
    print(f"\n── Sample claims ({s0['arch_id']} «{s0['label']}») ──")
    print(f"  label={s0['label']!r}  desc={description_for(s0)!r}")
    for c in cl:
        p = c["mainsnak"]["property"]; dv = c["mainsnak"]["datavalue"]["value"]
        v = dv.get("id") if isinstance(dv, dict) and "id" in dv else (
            dv.get("time") if isinstance(dv, dict) and "time" in dv else dv)
        print(f"    {p} = {v}")

    if not EXECUTE:
        print("\n── DRY RUN: building one preview tier ──")
        shutil.rmtree(WORK, ignore_errors=True); os.makedirs(WORK, exist_ok=True)
        smp = items[1]
        out = os.path.join(WORK, f"{smp['arch_id']}_prev.jpg")
        sips_jpeg(smp["src"], out, 2000, 82)
        print(f"  {smp['arch_id']} preview → {out}")
        print("\nDRY RUN complete. Re-run with --execute to write R2 + Wikibase.")
        return

    # ── EXECUTE ──────────────────────────────────────────────────────────────
    print("\n══════════════ EXECUTE ══════════════\n")
    wb = WikibaseSession(user_agent="HunterHouseBot/1.0 (batch_ingest_egc_photos)")

    # Resumability: skip any archive item already created (a prior partial run).
    # R2 uploads are idempotent (rclone skips identical); Wikibase creates are not.
    import requests as _rq
    existing_ids = set()
    try:
        q = 'SELECT ?id WHERE { ?i <https://hunterhouse.wikibase.cloud/prop/direct/P2> ?id . FILTER(STRSTARTS(?id,"HH-EGC-")) }'
        r = _rq.post("https://hunterhouse.wikibase.cloud/query/sparql",
                     data=q.encode(), headers={"Content-Type": "application/sparql-query",
                     "Accept": "application/sparql-results+json"}, timeout=60)
        existing_ids = {b["id"]["value"] for b in r.json()["results"]["bindings"]}
        print(f"  {len(existing_ids)} EGC items already in graph (will skip their create)")
    except Exception as e:
        print(f"  ⚠ preflight SPARQL failed ({e}); proceeding without dedup guard")

    # Pre-step: bring the existing Stool drawing (Q527) into a 2-sheet set +
    # tag it living room, so the two stool drawings read consistently.
    print("[pre] Q527 (existing Stool drawing): P86 → '01 of 02', +P87 living room")
    q527 = wb.get("wbgetentities", ids="Q527", props="claims")["entities"]["Q527"]["claims"]
    has_p87 = any(c["mainsnak"].get("datavalue", {}).get("value", {}).get("id") == AREA_LIVING
                  for c in q527.get("P87", []))
    edit = {"claims": []}
    # update P86 "01 of 01" → "01 of 02"
    for c in q527.get("P86", []):
        if c["mainsnak"].get("datavalue", {}).get("value") == "01 of 01":
            edit["claims"].append({"id": c["id"], "mainsnak": {"snaktype": "value",
                "property": "P86", "datavalue": {"value": "01 of 02", "type": "string"}},
                "type": "statement", "rank": "normal"})
    if not has_p87:
        edit["claims"].append(claim("P87", "item", AREA_LIVING))
    if edit["claims"]:
        wb.post("wbeditentity", id="Q527", data=json.dumps(edit))
        print("  Q527 updated.")

    print(f"\n[ingest] {len(items)} items")
    shutil.rmtree(WORK, ignore_errors=True); os.makedirs(WORK, exist_ok=True)
    results = []
    for i, it in enumerate(items, 1):
        print(f"\n  ({i}/{len(items)}) {it['arch_id']}  «{it['label']}»  [{it['genre']}]")
        # tiers
        tiers = {}
        for suffix, (px, q) in TIERS.items():
            out = os.path.join(WORK, f"{it['arch_id']}_{it['slug']}{suffix}")
            sips_jpeg(it["src"], out, px, q)
            tiers[suffix] = out
        # R2: master byte-for-byte + 3 tiers
        run(["rclone", "copyto", it["src"], f"{R2_MASTERS}/{it['master_name']}"])
        run(["rclone", "copy", tiers["_thumb.jpg"], R2_THUMBS + "/"])
        run(["rclone", "copy", tiers["_prev.jpg"],  R2_PREVIEWS + "/"])
        run(["rclone", "copy", tiers["_large.jpg"], R2_LARGE + "/"])
        # Wikibase item (skip if a prior run already created it)
        if it["arch_id"] in existing_ids:
            print(f"     R2 ✓ · Wikibase SKIP (already exists)")
            continue
        cl, mu, pu = build_claims(it)
        # stool drawing needs P86 "02 of 02"
        if it["arch_id"] == "HH-EGC-0031":
            cl.append(claim("P86", "string", "02 of 02"))
        data = {"labels": {"en": {"language": "en", "value": it["label"]}},
                "descriptions": {"en": {"language": "en", "value": description_for(it)}},
                "claims": cl}
        r = wb.post("wbeditentity", new="item", data=json.dumps(data))
        if "error" in r:
            raise SystemExit(f"create failed for {it['arch_id']}: {r['error']}")
        qid = r["entity"]["id"]
        existing_ids.add(it["arch_id"])
        results.append((it["arch_id"], qid))
        print(f"     R2 ✓ · Wikibase {qid}")
        # fail-safe metadata sidecar
        try:
            subprocess.run(["python3", os.path.join(os.path.dirname(__file__),
                            "sync_one_metadata.py"), it["arch_id"], "--execute", "--quiet"],
                           timeout=60, check=False)
        except Exception as e:
            print(f"     ⚠ sidecar skipped: {e}")

    shutil.rmtree(WORK, ignore_errors=True)
    print("\n══════════════ DONE ══════════════")
    for arch, qid in results:
        print(f"  {arch}  {qid}")
    print("\nNext: build_item_pages.py + build_catalogue_snapshot.py --execute "
          "(WDQS lags ~1min, so re-run pages if any 404).")


if __name__ == "__main__":
    main()
