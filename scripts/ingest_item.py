#!/usr/bin/env python3
"""
Ingest a single-image archive item: build the 3 R2 web tiers from the master
TIF, upload, and either CREATE a new Wikibase item or OVERWRITE an existing
QID (repurposing a stub slot).

Model mirrors scripts/ingest_publication.py but for a single sheet, not a
multi-page set:
  - master TIF byte-for-byte to R2 masters/
  - thumb / prev / large JPEGs (600 / 2000 / 3840 px) via sips
  - Wikibase item with the standard archive-item claims
  - vocab items (phase, areas) auto-resolved by exact label; missing ones
    created with the right instance-of (phases = Q2, areas = Q3)

Default: DRY RUN — builds locally, copies the large JPEG to ~/Desktop, prints
the full upload + Wikibase plan, opens the preview. --execute does the writes.

Per-item config sits in the CONFIG block below; edit and re-run for the next
single-image ingest.
"""

import json
import os
import shutil
import subprocess
import sys
import urllib.parse
import urllib.request

import requests

# ─────────────────────────── CONFIG (edit per item) ─────────────────────────
SOURCE        = "/Users/brandonpoole/Pictures/RichardHunterPortfolio19860013.tif"
ARCH_ID       = "HH-HHC-0112"
QID_OVERWRITE = "Q463"               # set to None to CREATE a fresh item instead

TITLE         = "Covenant Site Plan with Annotations"
DESCRIPTION   = "land survey; HHC; 2006"
YEAR          = 2006                 # P82 year precision (9)
SLUG          = "CovenantSitePlanWithAnnotations_2006"   # middle of file names

P1_VALUE      = "Q488"               # instance of → "Land survey" (item type)
P79_VALUE     = "Q180"               # source collection → HHC
P80_VALUE     = "Q201"               # creator → Richard Hunter
P92_VALUE     = "Q51"                # built status → built (Q51 built · Q52 partially · Q53 unbuilt · Q54 theoretical · None to omit)
P91_VALUE     = "Annotation on 8.5 x 11 site plan reproduction."   # medium (str; None to omit)

# Phase: created with instance-of Q2 ("architectural phase") if missing.
PHASE_LABEL   = "Covenant"
# Areas (P87): each created with instance-of Q3 if missing.
AREA_LABELS   = ["Site", "Covenant", "Kinhin Trail"]

# Tier recipes — match the rest of the archive
TIERS = {
    "_thumb.jpg": (600, 75),
    "_prev.jpg":  (2000, 82),
    "_large.jpg": (3840, 85),
}

# ─────────────────────────── R2 + URLs ──────────────────────────────────────
R2          = "hh-r2:hunter-house-archive"
COLL_DIR    = "hunter-house-collection"
PUBLIC_BASE = "https://archive.hunterhousefoundation.com"
MASTER_NAME = f"{ARCH_ID}_{SLUG}.tif"
URL_PREVIEW = f"{PUBLIC_BASE}/{COLL_DIR}/previews/{ARCH_ID}_{SLUG}_prev.jpg"
URL_MASTER  = f"{PUBLIC_BASE}/{COLL_DIR}/masters/{MASTER_NAME}"
R2_MASTERS  = f"{R2}/{COLL_DIR}/masters"
R2_THUMBS   = f"{R2}/{COLL_DIR}/thumbs"
R2_PREVIEWS = f"{R2}/{COLL_DIR}/previews"
R2_LARGE    = f"{R2}/{COLL_DIR}/large"

# ─────────────────────────── Wikibase ───────────────────────────────────────
API      = "https://hunterhouse.wikibase.cloud/w/api.php"
ENV_FILE = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")
CALENDAR = "http://www.wikidata.org/entity/Q1985727"
PHASE_INSTANCE_OF = "Q2"   # architectural phase
AREA_INSTANCE_OF  = "Q3"   # area / site element

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
    # `-m <sRGB.icc>`: bake sRGB into the output JPEG so the master's
    # kip2300-v6- scanner profile doesn't propagate (Chrome on wide-gamut
    # Mac displays renders it cyan). See CLAUDE.md cyan-cast entry.
    run(["sips", "-Z", str(max_px),
         "-m", "/System/Library/ColorSync/Profiles/sRGB Profile.icc",
         "-s", "format", "jpeg",
         "-s", "formatOptions", str(quality), src, "--out", dst],
        capture_output=True)


# ─────────────────────────── Wikibase write helpers ─────────────────────────
def wb_login(s, user, pw):
    t = s.get(API, params={"action": "query", "meta": "tokens",
                           "type": "login", "format": "json"}
              ).json()["query"]["tokens"]["logintoken"]
    r = s.post(API, data={"action": "login", "lgname": user, "lgpassword": pw,
                          "lgtoken": t, "format": "json"}).json()
    if r["login"]["result"] != "Success":
        raise SystemExit(f"Login failed: {r['login']['result']}")
    print(f"  logged in as {r['login']['lgusername']}")


def wb_csrf(s):
    return s.get(API, params={"action": "query", "meta": "tokens",
                              "format": "json"}
                 ).json()["query"]["tokens"]["csrftoken"]


def wb_find_exact(s, label, instance_of_qid, etype="item"):
    """Return QID of an entity whose en label matches `label` exactly AND has
    P1 = instance_of_qid, else None. The P1 filter is essential — labels can
    collide across kinds (e.g. an area and a phase both labelled 'Covenant'),
    and earlier this function returned the first match by label only, which
    silently put an area QID into a P62 (phase) slot."""
    r = s.get(API, params={"action": "wbsearchentities", "search": label,
                           "language": "en", "type": etype, "limit": 25,
                           "format": "json"}).json()
    candidates = [h["id"] for h in r.get("search", [])
                  if (h.get("label") or "").strip().lower() == label.strip().lower()]
    if not candidates:
        return None
    ents = s.get(API, params={"action": "wbgetentities", "ids": "|".join(candidates),
                              "props": "claims", "format": "json"}
                 ).json().get("entities", {})
    for q in candidates:
        for c in ents.get(q, {}).get("claims", {}).get("P1", []):
            v = c.get("mainsnak", {}).get("datavalue", {}).get("value", {})
            if isinstance(v, dict) and v.get("id") == instance_of_qid:
                return q
    return None


def wb_create_vocab_item(s, token, label, instance_of_qid, desc):
    """Create a tiny vocab item with label + instance-of + description."""
    data = {
        "labels":       {"en": {"language": "en", "value": label}},
        "descriptions": {"en": {"language": "en", "value": desc}},
        "claims": [claim("P1", "wikibase-item", instance_of_qid)],
    }
    r = s.post(API, data={"action": "wbeditentity", "new": "item",
                          "data": json.dumps(data), "token": token,
                          "format": "json"}).json()
    if "error" in r:
        raise SystemExit(f"vocab create failed: {r['error']}")
    return r["entity"]["id"]


def resolve_or_create(s, token, label, instance_of_qid, desc):
    """Look up an item by exact label AND matching instance-of, else create
    a new one. Returns (qid, created?)."""
    qid = wb_find_exact(s, label, instance_of_qid, "item")
    if qid:
        return qid, False
    qid = wb_create_vocab_item(s, token, label, instance_of_qid, desc)
    return qid, True


def claim(pid, datatype, value):
    """Build one wbeditentity claim by datatype."""
    if datatype == "wikibase-item":
        dv = {"value": {"entity-type": "item", "id": value},
              "type": "wikibase-entityid"}
    elif datatype == "time":
        dv = {"value": {"time": f"+{value}-00-00T00:00:00Z", "timezone": 0,
                        "before": 0, "after": 0, "precision": 9,
                        "calendarmodel": CALENDAR}, "type": "time"}
    else:  # string / url take a plain string value
        dv = {"value": value, "type": "string"}
    return {"mainsnak": {"snaktype": "value", "property": pid, "datavalue": dv},
            "type": "statement", "rank": "normal"}


# ─────────────────────────── main ───────────────────────────────────────────
def main():
    if not os.path.isfile(SOURCE):
        raise SystemExit(f"Source not found: {SOURCE}")
    src_mb = os.path.getsize(SOURCE) / 1e6
    print(f"\n{'EXECUTE' if EXECUTE else 'DRY RUN'} — {ARCH_ID}  «{TITLE}»\n")
    print(f"Source: {SOURCE}  ({src_mb:.0f} MB)")
    print(f"Target QID: {'OVERWRITE ' + QID_OVERWRITE if QID_OVERWRITE else '(new)'}")

    # 1. Build the 3 web tiers locally
    work = "/tmp/hh_item_" + ARCH_ID
    shutil.rmtree(work, ignore_errors=True)
    os.makedirs(work, exist_ok=True)
    print("\nBuilding tiers …")
    tier_files = {}
    for suffix, (px, q) in TIERS.items():
        out = os.path.join(work, f"{ARCH_ID}_{SLUG}{suffix}")
        sips_jpeg(SOURCE, out, px, q)
        tier_files[suffix] = out
        print(f"  {os.path.basename(out)}  ({os.path.getsize(out)//1024} KB)")

    # 2. R2 upload plan
    print("\n── R2 upload plan ──")
    print(f"  {os.path.basename(SOURCE)}  →  {R2_MASTERS}/{MASTER_NAME}   (master, byte-for-byte)")
    for suffix, dest in [("_thumb.jpg", R2_THUMBS), ("_prev.jpg", R2_PREVIEWS), ("_large.jpg", R2_LARGE)]:
        print(f"  {ARCH_ID}_{SLUG}{suffix}  →  {dest}/")

    # 3. Wikibase plan
    print("\n── Wikibase plan ──")
    if QID_OVERWRITE:
        print(f"  Overwrite {QID_OVERWRITE} (wbeditentity clear:1) — wipe existing claims/labels, set new")
    else:
        print(f"  Create new item")
    print(f"  label:   {TITLE!r}")
    print(f"  descr:   {DESCRIPTION!r}")
    print(f"  P1:      {P1_VALUE}  (item type)")
    print(f"  P2:      {ARCH_ID}")
    print(f"  P79:     {P79_VALUE}  (HHC)")
    print(f"  P80:     {P80_VALUE}  (creator)")
    print(f"  P82:     +{YEAR}-00-00 (year precision)")
    print(f"  P62:     <phase '{PHASE_LABEL}' — create with P1={PHASE_INSTANCE_OF} if missing>")
    print(f"  P87:     <areas {AREA_LABELS} — create missing with P1={AREA_INSTANCE_OF}>")
    if P92_VALUE:  print(f"  P92:     {P92_VALUE}  (built status)")
    if P91_VALUE:  print(f"  P91:     {P91_VALUE!r}  (medium)")
    print(f"  P96:     {URL_PREVIEW}")
    print(f"  P95:     {URL_MASTER}")

    # DRY RUN: preview the large tier to Desktop and stop.
    if not EXECUTE:
        desktop = os.path.expanduser(f"~/Desktop/{ARCH_ID}_{SLUG}_PREVIEW.jpg")
        shutil.copyfile(tier_files["_large.jpg"], desktop)
        print(f"\nDRY RUN complete. Preview on your Desktop (opening now):\n  {desktop}")
        subprocess.run(["open", desktop], check=False)
        print("\nCheck orientation/quality, then re-run with --execute.")
        return

    # ── EXECUTE ─────────────────────────────────────────────────────────────
    s = requests.Session()
    s.headers.update({"User-Agent": "HunterHouseBot/1.0 (ingest_item)"})
    env = load_env(ENV_FILE)
    wb_login(s, env["WIKIBASE_BOT_USER"], env["WIKIBASE_BOT_PASSWORD"])
    token = wb_csrf(s)

    # Resolve / create phase
    phase_qid, phase_created = resolve_or_create(
        s, token, PHASE_LABEL, PHASE_INSTANCE_OF,
        f"phase: {PHASE_LABEL.lower()}-related design and documentation"
    )
    print(f"  phase  «{PHASE_LABEL}»  → {phase_qid}  ({'CREATED' if phase_created else 'reused'})")

    # Resolve / create areas
    area_qids = []
    for lbl in AREA_LABELS:
        q, created = resolve_or_create(
            s, token, lbl, AREA_INSTANCE_OF,
            f"area: {lbl.lower()} (Hunter Residence)"
        )
        area_qids.append(q)
        print(f"  area   «{lbl}»  → {q}  ({'CREATED' if created else 'reused'})")

    # Upload R2 — master byte-for-byte, then tiers
    print("\nUploading to R2 …")
    run(["rclone", "copyto", SOURCE, f"{R2_MASTERS}/{MASTER_NAME}", "--progress"])
    run(["rclone", "copy", tier_files["_thumb.jpg"], R2_THUMBS + "/"])
    run(["rclone", "copy", tier_files["_prev.jpg"],  R2_PREVIEWS + "/"])
    run(["rclone", "copy", tier_files["_large.jpg"], R2_LARGE + "/"])
    print("  all objects uploaded.")

    # Build claims
    claims = [
        claim("P1",  "wikibase-item", P1_VALUE),
        claim("P2",  "string",        ARCH_ID),
        claim("P62", "wikibase-item", phase_qid),
        claim("P79", "wikibase-item", P79_VALUE),
        claim("P80", "wikibase-item", P80_VALUE),
        claim("P82", "time",          YEAR),
        claim("P95", "url",           URL_MASTER),
        claim("P96", "url",           URL_PREVIEW),
    ]
    for aq in area_qids:
        claims.append(claim("P87", "wikibase-item", aq))
    if P92_VALUE:
        claims.append(claim("P92", "wikibase-item", P92_VALUE))
    if P91_VALUE:
        claims.append(claim("P91", "string", P91_VALUE))

    data = {
        "labels":       {"en": {"language": "en", "value": TITLE}},
        "descriptions": {"en": {"language": "en", "value": DESCRIPTION}},
        "claims": claims,
    }

    if QID_OVERWRITE:
        # Wipe Q463 entirely, then apply new data
        params = {"action": "wbeditentity", "id": QID_OVERWRITE,
                  "clear": 1, "data": json.dumps(data),
                  "token": token, "format": "json"}
    else:
        params = {"action": "wbeditentity", "new": "item",
                  "data": json.dumps(data), "token": token, "format": "json"}

    r = s.post(API, data=params).json()
    if "error" in r:
        raise SystemExit(f"item write failed: {r['error']}")
    qid = r["entity"]["id"]
    print(f"\n  {'overwrote' if QID_OVERWRITE else 'created'} item {qid}  ({ARCH_ID})")
    print(f"  https://hunterhouse.wikibase.cloud/wiki/Item:{qid}")
    print(f"  {URL_PREVIEW}")

    shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
