#!/usr/bin/env python3
"""
Ingest the Keep/ batch of the Frances Hunter Collection — 2026-07-19, Brandon's
dispositions: the covenant newspaper clipping + 5 PDFs, all from Frances; one
(Sacred Profanities) gated, handled separately. This script does the 6 PUBLIC
items → HH-FRH-0051..0056 (the generic series; no type in the ID).

Pattern per ingest_frh_public (now archived): masters byte-for-byte (the jpg /
the PDFs ARE the masters — no larger scans exist, Brandon confirmed), tiers
from page 1 (sRGB, never upscaled), multi-page → per-page _pNN tiers (the
browse pager; add ids to PUBLIC_PAGES in browse+next!) + P143 access PDF.
Item types resolved by exact label, minted bare if absent (Clipping/Essay/Card).

Default: DRY RUN (plans + Desktop previews). --execute to write.
"""
import json
import os
import shutil
import subprocess
import sys

import requests

FH = os.path.expanduser("~/Desktop/Frances Hunter Archive")
API = "https://hunterhouse.wikibase.cloud/w/api.php"
SPARQL = "https://hunterhouse.wikibase.cloud/query/sparql"
ENV_FILE = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")
CALENDAR = "http://www.wikidata.org/entity/Q1985727"
R2 = "hh-r2:hunter-house-archive"
PUBLIC_BASE = "https://archive.hunterhousefoundation.com"
ICC = "/System/Library/ColorSync/Profiles/sRGB Profile.icc"
CDIR = "frances-hunter-collection"
COLL_QID = "Q181"
INC = "https://rightsstatements.org/vocab/InC/1.0/"
CNE = "https://rightsstatements.org/vocab/CNE/1.0/"

TIERS = {"_thumb.jpg": ("thumbs", 600, 75), "_prev.jpg": ("previews", 2000, 82),
         "_large.jpg": ("large", 3840, 85)}

TYPE_DESCS = {
    "Clipping": "item type: newspaper or magazine clipping",
    "Essay":    "item type: essay or article typescript",
    "Card":     "item type: printed card",
}

# date=(value, precision) 9/10/11; None = undated (note explains)
ITEMS = [
 dict(arch_id="HH-FRH-0051", itype="Clipping", src=f"{FH}/Jun24_2026/Hunter Newspaper.jpg",
      title="“Forever Natural” — Times Colonist Covenant Feature",
      slug="ForeverNaturalTimesColonist_2006-10-23", date=("2006-10-23", 11),
      rights=INC, creator=None,
      medium="Newspaper front page, Times Colonist (Victoria, BC)",
      notes="Front page, Monday 23 October 2006: “Forever Natural” by Kim Westad reports the "
            "Hunters' conservation covenant on 3.8 acres of their Prospect Lake property — the "
            "first volunteered covenant in the Capital Region. Photograph of Richard Hunter on a "
            "mossy rock by Bruce Stotesbury. See HH-HHC-0112 and HH-HHC-0083."),
 dict(arch_id="HH-FRH-0052", itype="Card", src=f"{FH}/Keep/EricMendelsohn_card.pdf",
      title="Performing Arts Centre for Eric Mendelsohn — Memorial Card",
      slug="MendelsohnMemorialCard", date=None,
      rights=INC, creator="Q201",
      medium="Printed card reproducing Hunter's memorial design drawing",
      notes="Card reproducing Richard Hunter's Performing Arts Centre for Eric Mendelsohn "
            "(1887–1953), “In Memoriam and to commemorate the Eric Mendelsohn Exhibition, "
            "Museum of Modern Art, New York, 1969.” Undated print commemorating the 1969 "
            "exhibition."),
 dict(arch_id="HH-FRH-0053", itype="Essay", src=f"{FH}/Keep/Architecture in the 80s019.pdf",
      title="Architecture in the Eighties: Moving Forward Backward",
      slug="ArchitectureInTheEighties_1985", date=("1985", 9),
      rights=INC, creator="Q201",
      medium="Typescript essay, 4 pages",
      notes="Richard Hunter's 1985 essay on postmodern architecture — “slick, glassy and still "
            "pampered by suitors, mainstream modern architecture idled into menopause before "
            "anyone knew it was pregnant.” A wry critique of the era of Graves and Johnson."),
 dict(arch_id="HH-FRH-0054", itype="Publication", src=f"{FH}/Keep/VicZenCentre037 copy.pdf",
      title="Victoria Zen Centre History Excerpt",
      slug="VictoriaZenCentreHistory", date=None,
      rights=CNE, creator=None,
      medium="Photocopied page from a Zen community history (p. 61)",
      notes="History of the Victoria Zen Centre mentioning “Kendo Ric Hunter's house”: the 1985 "
            "weekend retreat in the forest at 203 Goward Rd — an outdoor platform, work periods "
            "building the ten-minute kinhin train, sesshin practice. Published after 1991 "
            "(content reaches that year); exact date unknown."),
 dict(arch_id="HH-FRH-0055", itype="Essay", src=f"{FH}/Keep/Ric_article-for Structurist.pdf",
      title="A Manchester Dialogue — On the Early Sketches of Eric Mendelsohn",
      slug="AManchesterDialogue_2005", date=("2005", 9),
      rights=INC, creator="Q201",
      medium="Article draft with tracked changes, 10 pages; for The Structurist",
      notes="Draft article by Richard Hunter and Ita Heinze-Greenberg in dialogue on Erich "
            "Mendelsohn's early sketches — “the only born revolutionary of his generation.” "
            "Prepared for The Structurist; working draft with editorial revisions, 2005."),
 dict(arch_id="HH-FRH-0056", itype="Letter", src=f"{FH}/Keep/Re_ prospector article.pdf",
      title="Prospector Article — Email Exchange",
      slug="ProspectorArticleEmail_2006-02-13", date=("2006-02-13", 11),
      rights=INC, creator="Q201",
      medium="Printed email exchange, 3 pages",
      notes="Richard and Frances Hunter exchange a draft article, 13 February 2006: “A "
            "conservation first in the Prospect Lake/Tod Creek Watershed” — the 1969 purchase, "
            "Emily Sartain, saving the meadow and the Garry Oak, the land “to be saved in "
            "perpetuity.” The covenant's origin story in Ric's own prose. See HH-FRH-0051."),
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
    w, h = dims(src)
    args = ["sips", "-m", ICC, "-s", "format", "jpeg",
            "-s", "formatOptions", str(quality)]
    if max(w, h) > max_px:
        args += ["-Z", str(max_px)]
    run(args + [src, "--out", dst], capture_output=True)


def pdf_pages(path):
    import re
    d = open(path, "rb").read()
    c = re.findall(rb"/Count\s+(\d+)", d)
    return max(int(x) for x in c) if c else 1


def pdf_page_jpg(pdf, page, out_base, dpi=300):
    """Render one PDF page to JPEG; returns the produced path."""
    run(["pdftoppm", "-jpeg", "-r", str(dpi), "-f", str(page), "-l", str(page),
         pdf, out_base], capture_output=True)
    for cand in (f"{out_base}-{page}.jpg", f"{out_base}-{page:02d}.jpg", f"{out_base}-{page:03d}.jpg"):
        if os.path.exists(cand):
            return cand
    raise SystemExit(f"pdftoppm produced no page {page} for {pdf}")


# ── Wikibase helpers ─────────────────────────────────────────────────────────
def wb_login(s, user, pw):
    t = s.get(API, params={"action": "query", "meta": "tokens", "type": "login",
                           "format": "json"}).json()["query"]["tokens"]["logintoken"]
    r = s.post(API, data={"action": "login", "lgname": user, "lgpassword": pw,
                          "lgtoken": t, "format": "json"}).json()
    if r["login"]["result"] != "Success":
        raise SystemExit("login failed")
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


def wb_find_label(s, label):
    r = s.get(API, params={"action": "wbsearchentities", "search": label,
                           "language": "en", "type": "item", "limit": 25,
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
        iso = (f"+{parts[0]}-{parts[1] if len(parts) > 1 else '00'}-"
               f"{parts[2] if len(parts) > 2 else '00'}T00:00:00Z")
        dv = {"value": {"time": iso, "timezone": 0, "before": 0, "after": 0,
                        "precision": precision, "calendarmodel": CALENDAR},
              "type": "time"}
    else:
        dv = {"value": value, "type": "string"}
    return {"mainsnak": {"snaktype": "value", "property": pid, "datavalue": dv},
            "type": "statement", "rank": "normal"}


def main():
    for it in ITEMS:
        if not os.path.isfile(it["src"]):
            raise SystemExit(f"source missing: {it['src']}")
        if len(it["notes"]) > 400:
            raise SystemExit(f"{it['arch_id']}: note {len(it['notes'])} chars > 400 cap")

    print(f"\n{'EXECUTE' if EXECUTE else 'DRY RUN'} — {len(ITEMS)} Keep/ items\n")
    s = requests.Session()
    s.headers.update({"User-Agent": "HunterHouseBot/1.0 (batch_ingest_frh_keep)"})
    token = None
    if EXECUTE:
        env = load_env(ENV_FILE)
        wb_login(s, env["WIKIBASE_BOT_USER"], env["WIKIBASE_BOT_PASSWORD"])
        token = wb_csrf(s)

    # item types (existing + mint-if-absent)
    types = {"Publication": "Q91", "Letter": "Q583"}
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
        aid, slug = it["arch_id"], it["slug"]
        is_pdf = it["src"].lower().endswith(".pdf")
        npages = pdf_pages(it["src"]) if is_pdf else 1
        print(f"\n── {aid}  «{it['title']}»  ({npages} page{'s' if npages > 1 else ''})")

        if sparql_qid_for_p2(s, aid):
            print(f"   SKIP — {aid} exists")
            continue

        work = f"/tmp/hh_keep_{aid}"
        shutil.rmtree(work, ignore_errors=True)
        os.makedirs(work)

        # page images (PDF → render; image → itself)
        page_imgs = {}
        if is_pdf:
            for i in range(1, npages + 1):
                page_imgs[i] = pdf_page_jpg(it["src"], i, os.path.join(work, "pg"))
        else:
            page_imgs[1] = it["src"]

        # cover tiers (P96) from page 1
        tier_files = {}
        for suffix, (sub, px, q) in TIERS.items():
            out = os.path.join(work, f"{aid}_{slug}{suffix}")
            sips_jpeg(page_imgs[1], out, px, q)
            tier_files[suffix] = out
        # per-page tiers for the pager (multi-page only)
        if npages > 1:
            for i in range(1, npages + 1):
                for suffix, (sub, px, q) in TIERS.items():
                    out = os.path.join(work, f"{aid}_{slug}_p{i:02d}{suffix}")
                    sips_jpeg(page_imgs[i], out, px, q)

        master_ext = ".pdf" if is_pdf else ".jpg"
        master_name = f"{aid}_{slug}{master_ext}"
        url_master = f"{PUBLIC_BASE}/{CDIR}/masters/{master_name}"
        url_prev = f"{PUBLIC_BASE}/{CDIR}/previews/{aid}_{slug}_prev.jpg"
        url_pdf = f"{PUBLIC_BASE}/{CDIR}/pdf/{aid}_{slug}.pdf" if is_pdf else None

        if not EXECUTE:
            desk = os.path.expanduser(f"~/Desktop/{aid}_PREVIEW.jpg")
            shutil.copyfile(tier_files["_prev.jpg"], desk)
            print(f"   plan: master {master_name} + tiers ({npages}p) → {CDIR}/ · "
                  f"type={types[it['itype']]} rights={'InC' if it['rights']==INC else 'CNE'} "
                  f"date={it['date'][0] if it['date'] else '—'}")
            continue

        # R2 uploads (checked)
        run(["rclone", "copyto", it["src"], f"{R2}/{CDIR}/masters/{master_name}"])
        for suffix, (sub, px, q) in TIERS.items():
            run(["rclone", "copyto", tier_files[suffix],
                 f"{R2}/{CDIR}/{sub}/{aid}_{slug}{suffix}"])
        if npages > 1:
            for i in range(1, npages + 1):
                for suffix, (sub, px, q) in TIERS.items():
                    run(["rclone", "copyto",
                         os.path.join(work, f"{aid}_{slug}_p{i:02d}{suffix}"),
                         f"{R2}/{CDIR}/{sub}/{aid}_{slug}_p{i:02d}{suffix}"])
        if is_pdf:
            run(["rclone", "copyto", it["src"], f"{R2}/{CDIR}/pdf/{aid}_{slug}.pdf",
                 "--header-upload", "Content-Disposition: attachment"])
        print(f"   R2: master + {3 + (npages * 3 if npages > 1 else 0)} tiers"
              + (" + pdf" if is_pdf else "") + " uploaded")

        claims = [claim("P1", "wikibase-item", types[it["itype"]]),
                  claim("P2", "string", aid),
                  claim("P79", "wikibase-item", COLL_QID),
                  claim("P94", "wikibase-item", COLL_QID),
                  claim("P95", "url", url_master),
                  claim("P96", "url", url_prev),
                  claim("P91", "string", it["medium"]),
                  claim("P100", "string", it["notes"]),
                  claim("P146", "url", it["rights"])]
        if it["date"]:
            claims.append(claim("P82", "time", it["date"][0], it["date"][1]))
        if it.get("creator"):
            claims.append(claim("P80", "wikibase-item", it["creator"]))
        if url_pdf:
            claims.append(claim("P143", "url", url_pdf))
        year = it["date"][0].split("-")[0] if it["date"] else "undated"
        desc = f"{it['itype'].lower()}; FRH; {aid}; {year}"
        qid = wb_new_item(s, token, it["title"], desc, claims)
        print(f"   CREATED {qid}")

        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from sync_one_metadata import sync_one
            ok = sync_one(aid, execute=True)
            print("   sidecar synced" if ok else "   ⚠ sidecar falsy — check")
        except Exception as e:
            print(f"   ⚠ sidecar failed (non-fatal): {e}")

    print("\ndone. POST: PUBLIC_PAGES += {0053:4, 0055:10, 0056:3} in browse+next; "
          "pages/sitemap/snapshot; counts.")


if __name__ == "__main__":
    main()
