#!/usr/bin/env python3
"""
Ingest the two Frances Hunter Collection SKETCHBOOKS (public), 2026-07-15.

New material type for the archive: a hand-bound sketchbook of drawings. Each
physical book = ONE catalogue item (Brandon's call), rendered as a multi-page
object — per-page masters + thumb/prev/large tiers from the cover + an access
PDF (P143) the in-stage reader flips through, exactly like the 4-page program
HH-FRH-DOC-03.

Attribution:
  • P80 creator = Q201 Richard Hunter — drew the drawings
The binding (Frances Hunter / Red Tower Bookworks) is recorded as PROSE only —
in the medium + notes strings, not a structured built-by field (Brandon's call
2026-07-15). Physical custody stays with Frances — the archive holds only these
scans — so P94 held-by points at Q202 (the person), NOT the collection, and the
notes say so plainly.

New item type «Sketchbook» minted bare on first run (Q88/Q89/Q583 pattern).
IDs: HH-FRH-SKB-01 (Arguments, the bigger book) / -02 (the small book), a new
2-digit FRH series alongside DOC-##/PHOTO-##.

Default: DRY RUN (plans + full-res Desktop previews). --execute to write.
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
SB   = f"{FH}/Letters/ASketchbooks"
API  = "https://hunterhouse.wikibase.cloud/w/api.php"
SPARQL = "https://hunterhouse.wikibase.cloud/query/sparql"
ENV_FILE = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")
CALENDAR = "http://www.wikidata.org/entity/Q1985727"
R2 = "hh-r2:hunter-house-archive"
PUBLIC_BASE = "https://archive.hunterhousefoundation.com"
ICC = "/System/Library/ColorSync/Profiles/sRGB Profile.icc"
INC = "https://rightsstatements.org/vocab/InC/1.0/"   # P146 In Copyright

COLL_DIR = {"FRH": "frances-hunter-collection"}
COLL_QID = {"FRH": "Q181"}
Q_RICHARD = "Q201"   # creator of the drawings
Q_FRANCES = "Q202"   # bound the books / physical custodian

TYPE_DESC = "item type: hand-bound sketchbook of drawings"

TIERS = {"_thumb.jpg": (600, 75), "_prev.jpg": (2000, 82), "_large.jpg": (3840, 85)}
PDF_PX, PDF_Q = 2000, 80

# ── the manifest ─────────────────────────────────────────────────────────────
# sources = pages IN READING ORDER (drives PDF page order + _pNN masters).
# date = (value, precision): 9 year, 10 month, 11 day; None = undated.
ITEMS = [
 dict(arch_id="HH-FRH-SKB-01", coll="FRH", itype="Sketchbook",
      title="sketchbook (Arguments)",
      slug="Arguments_2015-2022",
      date=("2015-09-00", 10),   # cover dated 2015 IX; drawings run to 1 Jul 2022
      sources=[f"{SB}/Sketchbook_Arguments001.tif",     # cover
               f"{SB}/Sketchbook_Arguments002.tif",     # lettering / calligraphy study
               f"{SB}/Sketchbook_Arguments003-2.tif"],  # colour-pencil grid (HI-RES master)
      medium="Coloured pencil, ink and graphite in a hand-bound sketchbook "
             "(bound by Frances Hunter, Red Tower Bookworks)",
      notes="Hand-bound sketchbook of Richard Hunter’s drawings, "
            "“Arguments” (2015 IX – 1 July 2022), bound by Frances "
            "Hunter, Red Tower Bookworks. Shown: cover, a lettering study, a "
            "colour-pencil grid. The book stays with Frances Hunter — the "
            "archive holds scans only. Its final page (not shown) holds "
            "Richard’s computer passwords and the note “Dr. Winter "
            "— TODAY · NOT TONIGHT, BUT WILL SEE ME TOMORROW.”"),
 dict(arch_id="HH-FRH-SKB-02", coll="FRH", itype="Sketchbook",
      title="sketchbook (untitled)",
      slug="Sketchbook_2022",
      date=("2022", 9),   # first drawing 6 Jul 2022; the maze (last) undated
      sources=[f"{SB}/Sketchbook2_Arguments001.tif",   # marbled cover
               f"{SB}/Sketchbook2_Arguments003.tif",   # crayon arches (earlier drawing)
               f"{SB}/Sketchbook2_Arguments002.tif"],  # ink maze — FINAL, last he ever made
      medium="Ink and crayon in a hand-bound, marbled-paper sketchbook "
             "(bound by Frances Hunter, Red Tower Bookworks)",
      notes="Hand-bound untitled sketchbook of Richard Hunter’s drawings, "
            "bound by Frances Hunter (Red Tower Bookworks). Fourteen drawings, "
            "the first dated 6 July 2022 (a second 8 September 2022); later "
            "ones undated. The ink “maze” shown last is the last "
            "drawing Richard Hunter ever made. Shown: a marbled cover and two "
            "drawings. The book stays with Frances Hunter — the archive "
            "holds scans only."),
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
    # sRGB baked (cyan-cast rule); NEVER upscale (EGC lesson).
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


def wb_find_label(s, label, etype="item"):
    r = s.get(API, params={"action": "wbsearchentities", "search": label,
                           "language": "en", "type": etype, "limit": 25,
                           "format": "json"}).json()
    for h in r.get("search", []):
        if (h.get("label") or "").strip().lower() == label.strip().lower():
            return h["id"]
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
    print(f"\n{'EXECUTE' if EXECUTE else 'DRY RUN'} — {len(ITEMS)} sketchbooks\n")

    s = requests.Session()
    s.headers.update({"User-Agent": "HunterHouseBot/1.0 (ingest_frh_sketchbooks)"})
    token = None
    if EXECUTE:
        env = load_env(ENV_FILE)
        wb_login(s, env["WIKIBASE_BOT_USER"], env["WIKIBASE_BOT_PASSWORD"])
        token = wb_csrf(s)

    # resolve / mint the «Sketchbook» item type once
    sk_type = wb_find_label(s, "Sketchbook")
    if sk_type:
        print(f"  type «Sketchbook» → {sk_type} (exists)")
    elif EXECUTE:
        sk_type = wb_new_item(s, token, "Sketchbook", TYPE_DESC, [])
        print(f"  type «Sketchbook» → {sk_type} (MINTED)")
    else:
        sk_type = "<mint:Sketchbook>"
        print("  type «Sketchbook» → would mint")

    for it in ITEMS:
        aid, coll, slug = it["arch_id"], it["coll"], it["slug"]
        cdir = COLL_DIR[coll]
        npages = len(it["sources"])
        print(f"\n── {aid}  «{it['title']}»  ({npages} pages) ──")

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

        # access PDF (all pages, reading order)
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
        print(f"  access PDF: {npages} pages, {os.path.getsize(pdf_path)/1e6:.1f} MB")

        master_names = [f"{aid}_p{i:02d}.tif" for i in range(1, npages + 1)]
        url_master = f"{PUBLIC_BASE}/{cdir}/masters/{master_names[0]}"
        url_prev = f"{PUBLIC_BASE}/{cdir}/previews/{aid}_{slug}_prev.jpg"
        url_pdf = f"{PUBLIC_BASE}/{cdir}/pdf/{aid}_{slug}.pdf"

        d = it["date"]
        print(f"  R2: {npages} masters + 3 tiers + pdf → {cdir}/")
        print(f"  WB: P1={sk_type} P2={aid} P79={COLL_QID[coll]} P94={Q_FRANCES} "
              f"P80={Q_RICHARD} P146=InC date={d[0]} (prec {d[1]})")

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
        run(["rclone", "copyto", pdf_path, f"{R2}/{cdir}/pdf/{aid}_{slug}.pdf",
             "--header-upload", "Content-Disposition: attachment"])
        print("  R2 uploads done")

        # Wikibase item
        claims = [claim("P1", "wikibase-item", sk_type),
                  claim("P2", "string", aid),
                  claim("P79", "wikibase-item", COLL_QID[coll]),
                  claim("P94", "wikibase-item", Q_FRANCES),   # physical custodian = Frances
                  claim("P80", "wikibase-item", Q_RICHARD),   # drawings
                  claim("P95", "url", url_master),
                  claim("P96", "url", url_prev),
                  claim("P143", "url", url_pdf),
                  claim("P146", "url", INC),
                  claim("P82", "time", d[0], d[1]),
                  claim("P91", "string", it["medium"]),
                  claim("P100", "string", it["notes"])]

        year = d[0].split("-")[0]
        desc = f"sketchbook; {coll}; {aid}; {year}"
        qid = wb_new_item(s, token, it["title"], desc, claims)
        print(f"  CREATED {qid}")

        # sidecar (fail-safe)
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from sync_one_metadata import sync_one
            ok = sync_one(aid, execute=True)
            print("  sidecar synced" if ok else "  ⚠ sidecar sync falsy — check manually")
        except Exception as e:
            print(f"  ⚠ sidecar sync failed (non-fatal): {e}")

    print("\ndone.")


if __name__ == "__main__":
    main()
