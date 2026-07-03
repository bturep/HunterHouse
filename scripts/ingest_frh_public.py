#!/usr/bin/env python3
"""
Ingest the verified PUBLIC objects of the Frances Hunter Collection (plus one
HHC item), 2026-07-02. Embedded manifest — the batch_ingest_* pattern:

  - master TIF(s) byte-for-byte to R2 masters/
  - thumb/prev/large tiers (600/2000/3840, sRGB, NEVER upscaled)
  - multi-page items additionally get per-page masters + an access PDF (P143)
  - Wikibase item per object (SPARQL P2 preflight → safe to re-run)
  - vocab item types (Invitation / Flyer / Program) resolved by exact label,
    minted bare (like Q88/Q89/Q583) if absent
  - R2 sidecar via sync_one_metadata (fail-safe)

IDs per Brandon 2026-07-02: HH-FRH-DOC-## (documents/ephemera) and
HH-FRH-PHOTO-## (photographs), chronological within each series;
the covenant reference plan takes the next HHC number (HH-HHC-0116).

Default: DRY RUN (plans + Desktop previews). --execute to write.
"""
import json
import os
import shutil
import subprocess
import sys

import requests

try:
    from PIL import Image
except ImportError:
    Image = None

FH   = os.path.expanduser("~/Desktop/Frances Hunter Archive")
API  = "https://hunterhouse.wikibase.cloud/w/api.php"
SPARQL = "https://hunterhouse.wikibase.cloud/query/sparql"
ENV_FILE = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")
CALENDAR = "http://www.wikidata.org/entity/Q1985727"
R2 = "hh-r2:hunter-house-archive"
PUBLIC_BASE = "https://archive.hunterhousefoundation.com"
ICC = "/System/Library/ColorSync/Profiles/sRGB Profile.icc"

COLL_DIR = {"FRH": "frances-hunter-collection", "HHC": "hunter-house-collection"}
COLL_QID = {"FRH": "Q181", "HHC": "Q180"}

# item types: resolved by exact label; minted bare if absent (desc below)
TYPE_DESCS = {
    "Invitation": "item type: invitation or announcement for a private event",
    "Flyer":      "item type: hand-made or printed flyer for a public event",
    "Program":    "item type: printed program for a performance or event",
}

TIERS = {"_thumb.jpg": (600, 75), "_prev.jpg": (2000, 82), "_large.jpg": (3840, 85)}
PDF_PX, PDF_Q = 2000, 80

# ── the manifest ─────────────────────────────────────────────────────────────
# date = (value, precision): 9 year, 10 month, 11 day; None = undated
ITEMS = [
 dict(arch_id="HH-FRH-DOC-01", coll="FRH", itype="Flyer",
      title="Sasaki Roshi Two Talks Flyer",
      slug="SasakiRoshiTwoTalksFlyer_1975-06",
      date=("1975-06-00", 10),
      sources=[f"{FH}/May25_2026/FH_2026-05-2507.tif"],
      medium="Hand-lettered ink on rice paper with sumi enso",
      notes="Two talks by Joshu Sasaki Roshi: 10 June 1975, 7 pm, at 203 Goward "
            "Rd; 11 June 1975, 8 pm, University of Victoria. $10."),
 dict(arch_id="HH-FRH-DOC-02", coll="FRH", itype="Invitation",
      title="Directors' High Tea Invitation",
      slug="DirectorsHighTeaInvitation_1976-07-11",
      date=("1976-07-11", 11),
      sources=[f"{FH}/May25_2026/FH_2026-05-2504.tif"],
      medium="Hand-drawn map with coloured highlights",
      notes="Invitation-map: the route from Prospect Lake to 203 Goward Road "
            "drawn by hand, destination route in red. “You are invited to a "
            "Directors' High Tea — four until seven, Sunday 11 July 1976. "
            "Husbands, wives, lovers also welcome. RSVP. Ric & Frances Hunter, "
            "203 Goward Road, Victoria.”"),
 dict(arch_id="HH-FRH-DOC-03", coll="FRH", itype="Program",
      title="UVic Sonic Lab Concert Program",
      slug="UVicSonicLabConcertProgram_1986-11-14",
      date=("1986-11-14", 11),
      sources=[f"{FH}/May25_2026/FH_2026-05-25{n}.tif" for n in ("11", "12", "13", "14")],
      medium="Printed program, School of Music, University of Victoria",
      notes="UVic Sonic Lab, John Celona director — Recital Hall, Friday 14 "
            "November 1986. Opens with Alvin Lucier's “Music for Solo "
            "Performer” (1965), performed by Rick Hunter (alpha waves) with "
            "Will Bauer (electronics). Page 2 carries the performer bio: "
            "“Rick Hunter is an architect living in Victoria. He has studied "
            "Zen Buddhism for many years.” See HH-FRH-PHOTO-04."),
 dict(arch_id="HH-FRH-PHOTO-01", coll="FRH", itype="Photograph",
      title="No More Mondays with Figures",
      slug="NoMoreMondaysWithFigures_c1970s",
      date=None,
      sources=[f"{FH}/Jun24_2026/No More Mondays/FH_2026-06-2422 [No More Mondays].tif"],
      medium="Colour photographic print",
      notes="“No More Mondays” — the part-chair / part-room structure, a "
            "precursor to the Choom at 203 Goward Rd. White geometric panels; a "
            "child stands atop, a woman carries an infant at right. Undated, "
            "c. 1970s."),
 dict(arch_id="HH-FRH-PHOTO-02", coll="FRH", itype="Photograph",
      title="No More Mondays on the Moss",
      slug="NoMoreMondaysOnTheMoss_c1970s",
      date=None,
      sources=[f"{FH}/Jun24_2026/No More Mondays/FH_2026-06-2424.tif"],
      medium="Colour photographic print",
      notes="“No More Mondays” alone on the mossy outcrop, backlit through "
            "the firs. Undated, c. 1970s. See HH-FRH-PHOTO-01."),
 dict(arch_id="HH-FRH-PHOTO-03", coll="FRH", itype="Photograph",
      title="Rick Working on Square",
      slug="RickWorkingOnSquare_1978-08",
      date=("1978-08-00", 10),
      sources=[f"{FH}/Jun24_2026/Choom/FH_2026-06-2427 [\"Rick working on Square, ,Aug 1978] - Ric's Mother.tif"],
      medium="Colour photographic print",
      notes="Verso note: “Rick working on Square, Aug 1978.” Richard Hunter "
            "building the Square / Choom deck structure in the woods at 203 "
            "Goward Rd. Photograph by his mother."),
 dict(arch_id="HH-FRH-PHOTO-04", coll="FRH", itype="Photograph",
      title="Music for Solo Performer",
      slug="MusicForSoloPerformer_1986-11-14",
      date=("1986-11-14", 11),
      sources=[f"{FH}/May25_2026/FH_2026-05-2510.tif"],
      medium="Gelatin silver print",
      notes="Richard Hunter performing Alvin Lucier's “Music for Solo "
            "Performer” (1965) — seated, alpha-wave electrodes, before the "
            "bass drum — UVic Recital Hall, 14 November 1986. See "
            "HH-FRH-DOC-03 for the program."),
 dict(arch_id="HH-HHC-0116", coll="HHC", itype="Land survey",
      title="Covenant Reference Plan",
      slug="CovenantReferencePlan_2001-12",
      date=("2001-12-00", 10),
      sources=[f"{FH}/Letters/FH_Letters_2026-06-26141.tif"],
      medium="Survey reference plan reproduction (Richard J. Wey & Associates "
             "Land Surveying, Sidney BC)",
      notes="Reference Plan of Covenant over Part of Lot 2, Sections 88 and 89, "
            "Lake District, Plan 29201, pursuant to Section 99(1)(e) L.T.A. "
            "Prepared by Richard J. Wey & Associates, December 2001. Companion "
            "to HH-HHC-0112 (annotated covenant site plan) and HH-HHC-0083 "
            "(2018 full site survey).",
      phase="Covenant", areas=["Site", "Covenant"]),
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
    # sRGB baked (cyan-cast rule); NEVER upscale (EGC lesson) — only -Z when
    # the source's max edge exceeds the tier size.
    w, h = dims(src)
    args = ["sips", "-m", ICC, "-s", "format", "jpeg",
            "-s", "formatOptions", str(quality)]
    if max(w, h) > max_px:
        args += ["-Z", str(max_px)]
    run(args + [src, "--out", dst], capture_output=True)


# ── Wikibase helpers (ingest_item.py pattern) ────────────────────────────────
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


def wb_find_label(s, label, etype="item"):
    r = s.get(API, params={"action": "wbsearchentities", "search": label,
                           "language": "en", "type": etype, "limit": 25,
                           "format": "json"}).json()
    for h in r.get("search", []):
        if (h.get("label") or "").strip().lower() == label.strip().lower():
            return h["id"]
    return None


def wb_find_typed(s, label, instance_of):
    """Exact label AND P1=instance_of (for phases/areas)."""
    r = s.get(API, params={"action": "wbsearchentities", "search": label,
                           "language": "en", "type": "item", "limit": 25,
                           "format": "json"}).json()
    cands = [h["id"] for h in r.get("search", [])
             if (h.get("label") or "").strip().lower() == label.strip().lower()]
    if not cands:
        return None
    ents = s.get(API, params={"action": "wbgetentities", "ids": "|".join(cands),
                              "props": "claims", "format": "json"}).json().get("entities", {})
    for q in cands:
        for c in ents.get(q, {}).get("claims", {}).get("P1", []):
            v = c.get("mainsnak", {}).get("datavalue", {}).get("value", {})
            if isinstance(v, dict) and v.get("id") == instance_of:
                return q
    return None


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
        iso = f"+{parts[0]}-{parts[1] if len(parts) > 1 else '00'}-{parts[2] if len(parts) > 2 else '00'}T00:00:00Z"
        dv = {"value": {"time": iso, "timezone": 0, "before": 0, "after": 0,
                        "precision": precision, "calendarmodel": CALENDAR},
              "type": "time"}
    else:
        dv = {"value": value, "type": "string"}
    return {"mainsnak": {"snaktype": "value", "property": pid, "datavalue": dv},
            "type": "statement", "rank": "normal"}


def main():
    for it in ITEMS:
        for p in it["sources"]:
            if not os.path.isfile(p):
                raise SystemExit(f"source missing: {p}")
    print(f"\n{'EXECUTE' if EXECUTE else 'DRY RUN'} — {len(ITEMS)} items\n")

    s = requests.Session()
    s.headers.update({"User-Agent": "HunterHouseBot/1.0 (ingest_frh_public)"})
    token = None
    if EXECUTE:
        env = load_env(ENV_FILE)
        wb_login(s, env["WIKIBASE_BOT_USER"], env["WIKIBASE_BOT_PASSWORD"])
        token = wb_csrf(s)

    # resolve / mint item types once
    types = {"Photograph": "Q89", "Land survey": "Q488"}
    for t, desc in TYPE_DESCS.items():
        q = wb_find_label(s, t)
        if q:
            types[t] = q
            print(f"  type «{t}» → {q} (exists)")
        elif EXECUTE:
            types[t] = wb_new_item(s, token, t, desc, [])
            print(f"  type «{t}» → {types[t]} (MINTED)")
        else:
            types[t] = f"<mint:{t}>"
            print(f"  type «{t}» → would mint")

    for it in ITEMS:
        aid, coll, slug = it["arch_id"], it["coll"], it["slug"]
        cdir = COLL_DIR[coll]
        multi = len(it["sources"]) > 1
        print(f"\n── {aid}  «{it['title']}»  ({len(it['sources'])} page{'s' if multi else ''}) ──")

        # resume guard
        existing = sparql_qid_for_p2(s, aid)
        if existing:
            print(f"  SKIP — {aid} already exists as {existing}")
            continue

        work = f"/tmp/hh_frh_{aid}"
        shutil.rmtree(work, ignore_errors=True)
        os.makedirs(work)

        # tiers from page 1 (cover)
        cover = it["sources"][0]
        tier_files = {}
        for suffix, (px, q) in TIERS.items():
            out = os.path.join(work, f"{aid}_{slug}{suffix}")
            sips_jpeg(cover, out, px, q)
            tier_files[suffix] = out

        # multi-page: access PDF
        pdf_path = None
        if multi:
            if Image is None:
                raise SystemExit("Pillow needed for the access PDF")
            pjs = []
            for i, src in enumerate(it["sources"], 1):
                pj = os.path.join(work, f"page_{i:02d}.jpg")
                sips_jpeg(src, pj, PDF_PX, PDF_Q)
                pjs.append(pj)
            imgs = [Image.open(p).convert("RGB") for p in pjs]
            pdf_path = os.path.join(work, f"{aid}_{slug}.pdf")
            imgs[0].save(pdf_path, "PDF", save_all=True, append_images=imgs[1:],
                         resolution=150.0, quality=PDF_Q)
            print(f"  access PDF: {os.path.getsize(pdf_path)/1e6:.1f} MB")

        # master names
        if multi:
            master_names = [f"{aid}_p{i:02d}.tif" for i in range(1, len(it["sources"]) + 1)]
        else:
            master_names = [f"{aid}_{slug}.tif"]

        url_master = f"{PUBLIC_BASE}/{cdir}/masters/{master_names[0]}"
        url_prev = f"{PUBLIC_BASE}/{cdir}/previews/{aid}_{slug}_prev.jpg"
        url_pdf = f"{PUBLIC_BASE}/{cdir}/pdf/{aid}_{slug}.pdf" if multi else None

        print(f"  R2: {len(master_names)} master(s) + 3 tiers" + (" + pdf" if multi else "") + f" → {cdir}/")
        d = it["date"]
        print(f"  WB: P1={types[it['itype']]} P2={aid} P79={COLL_QID[coll]} "
              f"date={'—' if not d else d[0] + ' (prec ' + str(d[1]) + ')'}")

        if not EXECUTE:
            desk = os.path.expanduser(f"~/Desktop/{aid}_PREVIEW.jpg")
            shutil.copyfile(tier_files["_large.jpg"], desk)
            continue

        # R2 uploads (rclone copyto, checked)
        for i, src in enumerate(it["sources"]):
            run(["rclone", "copyto", src, f"{R2}/{cdir}/masters/{master_names[i]}"])
        for suffix, sub in [("_thumb.jpg", "thumbs"), ("_prev.jpg", "previews"),
                            ("_large.jpg", "large")]:
            run(["rclone", "copyto", tier_files[suffix],
                 f"{R2}/{cdir}/{sub}/{aid}_{slug}{suffix}"])
        if pdf_path:
            run(["rclone", "copyto", pdf_path, f"{R2}/{cdir}/pdf/{aid}_{slug}.pdf",
                 "--header-upload", "Content-Disposition: attachment"])
        print("  R2 uploads done")

        # Wikibase item
        claims = [claim("P1", "wikibase-item", types[it["itype"]]),
                  claim("P2", "string", aid),
                  claim("P79", "wikibase-item", COLL_QID[coll]),
                  claim("P94", "wikibase-item", COLL_QID[coll]),
                  claim("P95", "url", url_master),
                  claim("P96", "url", url_prev)]
        if d:
            claims.append(claim("P82", "time", d[0], d[1]))
        if it.get("medium"):
            claims.append(claim("P91", "string", it["medium"]))
        if it.get("notes"):
            claims.append(claim("P100", "string", it["notes"]))
        if url_pdf:
            claims.append(claim("P143", "url", url_pdf))
        if it.get("phase"):
            pq = wb_find_typed(s, it["phase"], "Q2")
            if pq:
                claims.append(claim("P62", "wikibase-item", pq))
                print(f"  phase «{it['phase']}» → {pq}")
            else:
                print(f"  ⚠ phase «{it['phase']}» not found — omitted")
        for a in it.get("areas", []):
            aq = wb_find_typed(s, a, "Q3")
            if aq:
                claims.append(claim("P87", "wikibase-item", aq))
            else:
                print(f"  ⚠ area «{a}» not found — omitted")

        year = (d[0].split("-")[0] if d else "undated")
        desc = f"{it['itype'].lower()}; {coll}; {aid}; {year}"
        qid = wb_new_item(s, token, it["title"], desc, claims)
        print(f"  CREATED {qid}")

        # sidecar (fail-safe)
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from sync_one_metadata import sync_one
            ok = sync_one(aid, execute=True)
            print("  sidecar synced" if ok else "  ⚠ sidecar sync returned falsy — check manually")
        except Exception as e:
            print(f"  ⚠ sidecar sync failed (non-fatal): {e}")

    print("\ndone.")


if __name__ == "__main__":
    main()
