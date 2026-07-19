#!/usr/bin/env python3
"""
Batch-ingest the Frances Hunter Collection PHOTO batch (41 house-documentation
photographs), 2026-07-19. Continues the HH-FRH-PHOTO-## series (05..45),
CHRONOLOGICAL order (scan order was wrong — see the contact sheet).

Modelled on ingest_frh_public.py / batch_ingest_egc_photos.py:
  - master TIF byte-for-byte to R2 masters/ ; thumb/prev/large tiers
    (600/2000/3840, sRGB baked, NEVER upscaled)
  - one Wikibase item per photo (SPARQL P2 preflight → safe to re-run)
  - single-page objects (photographs) → no access PDF

Batch-specific decisions (Brandon, 2026-07-19):
  - P80 creator OMITTED — photographer unknown (assumed Ric, unconfirmed)
  - P146 rights = CNE (Copyright Not Evaluated) — cannot clear an unknown shooter
  - P94 held-by = Q187 Hunter House Foundation — the hardcopy prints are GIFTED
    to the Foundation (custody), distinct from the rest of FRH (Q181/Q202).
    Provenance stays P79 = Q181 Frances Hunter Collection.
  - verso text captured verbatim in P100; dates at year/month precision;
    3 undated frames get 1995 (year prec) + an explicit uncertainty note.
  - provisional titles ("Hunter House" / verso variant) — Brandon relabels
    area/subject in a later pass.

Default: DRY RUN (plans + Desktop previews). --execute to write.
"""
import glob
import json
import os
import re
import shutil
import subprocess
import sys

import requests

SRC_DIR = os.path.expanduser("~/Desktop/FRH PHOTOS")
API = "https://hunterhouse.wikibase.cloud/w/api.php"
SPARQL = "https://hunterhouse.wikibase.cloud/query/sparql"
ENV_FILE = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")
CALENDAR = "http://www.wikidata.org/entity/Q1985727"
R2 = "hh-r2:hunter-house-archive"
PUBLIC_BASE = "https://archive.hunterhousefoundation.com"
ICC = "/System/Library/ColorSync/Profiles/sRGB Profile.icc"

CDIR = "frances-hunter-collection"
COLL_QID = "Q181"          # P79 provenance — Frances Hunter Collection
HELD_BY = "Q187"           # P94 custody   — Hunter House Foundation (the gift)
PHOTO_TYPE = "Q89"         # P1 instance of — Photograph
CNE = "https://rightsstatements.org/vocab/CNE/1.0/"  # P146 rights

TIERS = {"_thumb.jpg": (600, 75), "_prev.jpg": (2000, 82), "_large.jpg": (3840, 85)}

UNCERTAIN_NOTE = ("Date uncertain — 1990s, after the 1992 photographs and before "
                  "the January 1998 series; 1995 assigned as a working estimate "
                  "pending confirmation.")

# ── chronological plan: (old Photo#, date_value, precision, verso, uncertain) ──
#    date_value: "YYYY" (prec 9) or "YYYY-MM" (prec 10)
PLAN = [
    (1,  "1977",    9,  None,            False),
    (2,  "1977",    9,  None,            False),
    (3,  "1986",    9,  "Wood Stove Added", False),
    (4,  "1988",    9,  "Kitchen #1",    False),
    (7,  "1990-10", 10, None,            False),
    (8,  "1990-10", 10, None,            False),
    (9,  "1990-10", 10, None,            False),
    (10, "1991-01", 10, None,            False),
    (11, "1991-01", 10, None,            False),
    (12, "1991-01", 10, None,            False),
    (13, "1991-01", 10, None,            False),
    (14, "1991-01", 10, None,            False),
    (15, "1991-01", 10, "Tree now missing", False),
    (18, "1991-02", 10, None,            False),
    (19, "1991-02", 10, None,            False),
    (16, "1991-03", 10, None,            False),
    (17, "1991-03", 10, None,            False),
    (20, "1991-06", 10, None,            False),
    (21, "1991-06", 10, None,            False),
    (23, "1991-09", 10, None,            False),
    (24, "1991-09", 10, None,            False),
    (25, "1991-09", 10, None,            False),
    (26, "1991-09", 10, None,            False),
    (27, "1991-09", 10, None,            False),
    (28, "1991-09", 10, None,            False),
    (29, "1991-09", 10, None,            False),
    (30, "1991-09", 10, None,            False),
    (31, "1991-09", 10, None,            False),
    (32, "1991-09", 10, None,            False),
    (33, "1991-09", 10, None,            False),
    (34, "1991-09", 10, None,            False),
    (35, "1991-09", 10, None,            False),
    (36, "1991-09", 10, None,            False),
    (22, "1992",    9,  None,            False),
    (5,  "1995",    9,  None,            True),
    (6,  "1995",    9,  None,            True),
    (41, "1995",    9,  None,            True),
    (37, "1998-01", 10, "RH in Atrium",  False),
    (38, "1998-01", 10, "Atrium Framing", False),
    (39, "1998-01", 10, None,            False),
    (40, "1998-01", 10, None,            False),
]

EXECUTE = "--execute" in sys.argv


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


def src_map():
    """Photo number -> filepath (handles apostrophes/quotes in names)."""
    m = {}
    for f in glob.glob(os.path.join(SRC_DIR, "FRC_Photo*.tif")):
        g = re.search(r"Photo0*(\d+)", os.path.basename(f))
        if g:
            m[int(g.group(1))] = f
    return m


def dims(p):
    out = subprocess.run(["sips", "-g", "pixelWidth", "-g", "pixelHeight", p],
                         capture_output=True, text=True).stdout
    w = h = None
    for ln in out.splitlines():
        if "pixelWidth" in ln:
            w = int(ln.split()[-1])
        if "pixelHeight" in ln:
            h = int(ln.split()[-1])
    return w, h


def sips_jpeg(src, dst, max_px, quality):
    w, h = dims(src)
    args = ["sips", "-m", ICC, "-s", "format", "jpeg",
            "-s", "formatOptions", str(quality)]
    if max(w, h) > max_px:
        args += ["-Z", str(max_px)]
    run(args + [src, "--out", dst], capture_output=True)


# ── Wikibase helpers (ingest_frh_public.py pattern) ──────────────────────────
def wb_login(s, user, pw):
    t = s.get(API, params={"action": "query", "meta": "tokens", "type": "login",
                           "format": "json"}).json()["query"]["tokens"]["logintoken"]
    r = s.post(API, data={"action": "login", "lgname": user, "lgpassword": pw,
                          "lgtoken": t, "format": "json"}).json()
    if r["login"]["result"] != "Success":
        raise SystemExit(f"Login failed: {r['login']['result']}")
    print(f"  logged in as {r['login']['lgusername']}")


def wb_csrf(s):
    return s.get(API, params={"action": "query", "meta": "tokens",
                              "format": "json"}).json()["query"]["tokens"]["csrftoken"]


def sparql_qid_for_p2(s, arch_id):
    q = ('SELECT ?i WHERE { ?i <https://hunterhouse.wikibase.cloud/prop/direct/P2> "'
         + arch_id + '" }')
    r = s.post(SPARQL, data=q.encode(),
               headers={"Content-Type": "application/sparql-query",
                        "Accept": "application/sparql-results+json"}).json()
    b = r["results"]["bindings"]
    return b[0]["i"]["value"].split("/")[-1] if b else None


def wb_new_item(s, token, label, desc, claims):
    data = {"labels": {"en": {"language": "en", "value": label}},
            "descriptions": {"en": {"language": "en", "value": desc}},
            "claims": claims}
    r = s.post(API, data={"action": "wbeditentity", "new": "item",
                          "data": json.dumps(data), "token": token,
                          "format": "json"}).json()
    if "error" in r:
        raise SystemExit(f"wbeditentity failed: {r['error']}")
    return r["entity"]["id"]


def claim(pid, datatype, value, precision=9):
    if datatype == "wikibase-item":
        dv = {"value": {"entity-type": "item", "id": value}, "type": "wikibase-entityid"}
    elif datatype == "time":
        parts = value.split("-")
        iso = (f"+{parts[0]}-{parts[1] if len(parts) > 1 else '00'}-"
               f"{parts[2] if len(parts) > 2 else '00'}T00:00:00Z")
        dv = {"value": {"time": iso, "timezone": 0, "before": 0, "after": 0,
                        "precision": precision, "calendarmodel": CALENDAR},
              "type": "time"}
    else:
        dv = {"value": value, "type": "string"}
    return {"mainsnak": {"snaktype": "value", "property": pid, "datavalue": dv},
            "type": "statement", "rank": "normal"}


def build(old_num, date_value, precision, verso, uncertain, new_id):
    aid = f"HH-FRH-PHOTO-{new_id:02d}"
    title = f"Hunter House — {verso}" if verso else "Hunter House"
    base = re.sub(r"[^A-Za-z0-9]", "", verso.title()) if verso else "HunterHouse"
    datecompact = ("c1995" if uncertain else date_value)
    slug = f"{base}_{datecompact}"
    notes = []
    if verso:
        notes.append(f'Verso: "{verso}".')
    notes.append("Photographer unknown.")
    if uncertain:
        notes.append(UNCERTAIN_NOTE)
    return dict(arch_id=aid, title=title, slug=slug, date=(date_value, precision),
                notes=" ".join(notes), old_num=old_num)


def main():
    smap = src_map()
    items = []
    for i, (old, dv, prec, verso, unc) in enumerate(PLAN):
        if old not in smap:
            raise SystemExit(f"source missing for Photo{old:03d}")
        it = build(old, dv, prec, verso, unc, 5 + i)
        it["source"] = smap[old]
        items.append(it)

    print(f"\n{'EXECUTE' if EXECUTE else 'DRY RUN'} — {len(items)} FRH photos "
          f"(HH-FRH-PHOTO-05 … -{4 + len(items):02d})\n")

    s = requests.Session()
    s.headers.update({"User-Agent": "HunterHouseBot/1.0 (batch_ingest_frh_photos)"})
    token = None
    if EXECUTE:
        env = load_env(ENV_FILE)
        wb_login(s, env["WIKIBASE_BOT_USER"], env["WIKIBASE_BOT_PASSWORD"])
        token = wb_csrf(s)

    for it in items:
        aid, slug = it["arch_id"], it["slug"]
        d = it["date"]
        print(f"── {aid}  «{it['title']}»  {d[0]} (prec {d[1]})  [was Photo{it['old_num']:03d}]")

        existing = sparql_qid_for_p2(s, aid)
        if existing:
            print(f"   SKIP — already exists as {existing}")
            continue

        work = f"/tmp/hh_frhph_{aid}"
        shutil.rmtree(work, ignore_errors=True)
        os.makedirs(work)

        tier_files = {}
        for suffix, (px, q) in TIERS.items():
            out = os.path.join(work, f"{aid}_{slug}{suffix}")
            sips_jpeg(it["source"], out, px, q)
            tier_files[suffix] = out

        master_name = f"{aid}_{slug}.tif"
        url_master = f"{PUBLIC_BASE}/{CDIR}/masters/{master_name}"
        url_prev = f"{PUBLIC_BASE}/{CDIR}/previews/{aid}_{slug}_prev.jpg"

        if not EXECUTE:
            desk = os.path.expanduser(f"~/Desktop/{aid}_PREVIEW.jpg")
            shutil.copyfile(tier_files["_large.jpg"], desk)
            print(f"   plan: master {master_name} + 3 tiers → {CDIR}/  |  "
                  f"P94={HELD_BY} P146=CNE  |  notes: {it['notes'][:70]}…")
            continue

        # R2 uploads (checked)
        run(["rclone", "copyto", it["source"], f"{R2}/{CDIR}/masters/{master_name}"])
        for suffix, sub in [("_thumb.jpg", "thumbs"), ("_prev.jpg", "previews"),
                            ("_large.jpg", "large")]:
            run(["rclone", "copyto", tier_files[suffix],
                 f"{R2}/{CDIR}/{sub}/{aid}_{slug}{suffix}"])
        print("   R2 uploads done")

        claims = [claim("P1", "wikibase-item", PHOTO_TYPE),
                  claim("P2", "string", aid),
                  claim("P79", "wikibase-item", COLL_QID),
                  claim("P94", "wikibase-item", HELD_BY),
                  claim("P95", "url", url_master),
                  claim("P96", "url", url_prev),
                  claim("P82", "time", d[0], d[1]),
                  claim("P91", "string", "Photographic print"),
                  claim("P100", "string", it["notes"]),
                  claim("P146", "url", CNE)]
        year = d[0].split("-")[0]
        desc = f"photograph; FRH; {aid}; {year}"
        qid = wb_new_item(s, token, it["title"], desc, claims)
        print(f"   CREATED {qid}")

        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from sync_one_metadata import sync_one
            ok = sync_one(aid, execute=True)
            print("   sidecar synced" if ok else "   ⚠ sidecar sync falsy — check")
        except Exception as e:
            print(f"   ⚠ sidecar sync failed (non-fatal): {e}")

    print("\ndone.")


if __name__ == "__main__":
    main()
