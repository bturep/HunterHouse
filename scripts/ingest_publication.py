#!/usr/bin/env python3
"""
Ingest a multi-page publication into the Hunter House archive.

Built for the 1986 "Richard Hunter Architect — Portfolio" (10 TIF page scans,
~205 MB each) but the CONFIG block at the top is the only thing to change to
reuse it for the other publications still to come.

Model: one archive item, pages as an internal sequence.
  - Preservation masters : the 10 TIFs, byte-for-byte, never recompressed,
                           grouped in masters/<ID>/ + a SHA-256 fixity manifest
  - Cover web tiers      : thumb/prev/large from page 1 (so browse.html works
                           unchanged — P96 points at the _prev.jpg)
  - Access PDF           : all pages downsized into one readable PDF

Two-stage by design (the project's batch protocol = confirm before any write):
  python3 scripts/ingest_publication.py            # DRY RUN — builds the PDF
                                                   #   + tiers locally, prints
                                                   #   the full upload + Wikibase
                                                   #   plan, writes NOTHING remote
  python3 scripts/ingest_publication.py --execute  # uploads to R2, then creates
                                                   #   the Wikibase item (after
                                                   #   you've checked the PDF)

Credentials (bot user/pass) load from ~/Documents/hh-wikibase-migration/.env,
same as scripts/patch_dates.py. rclone + sips are used exactly as
scripts/regen_previews.py uses them (no new dependencies; Pillow assembles
the PDF and is already installed).
"""

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

import requests
from PIL import Image

# ─────────────────────────── CONFIG (edit per publication) ──────────────────
SOURCE_DIR  = "/Users/brandonpoole/Desktop/1986publication"
ARCH_ID     = "HH-HHC-0115"
LABEL       = "Richard Hunter Architect — Portfolio (1986, self-published)"
DESCRIPTION = "self-published portfolio; HHC; 1986"
YEAR        = 1986
SLUG        = "RichardHunterArchitect-Portfolio_1986"   # middle of derivative filenames

# Wikibase values (probed live before writing this script)
P1_VALUE  = "Q91"    # instance of  → "publication"
P79_VALUE = "Q180"   # source collection → HHC
P80_VALUE = "Q201"   # creator → Richard Hunter
# P62 (project phase) deliberately omitted — this publication has no phase.
# P142 (physical location) deliberately omitted — HHC holds the hardcopy;
#       the exact shelf path will be added later.

# Derivative recipes (cover tiers match the rest of the archive exactly)
TIERS = {                       # suffix : (max px on long edge, JPEG quality)
    "_thumb.jpg": (600, 75),
    "_prev.jpg":  (2000, 82),
    "_large.jpg": (3840, 85),
}
PDF_PX, PDF_Q = 2200, 80        # per-page size/quality inside the access PDF

# ─────────────────────────── R2 + public URLs ───────────────────────────────
R2          = "hh-r2:hunter-house-archive"
COLL_DIR    = "hunter-house-collection"
PUBLIC_BASE = "https://archive.hunterhousefoundation.com"

R2_MASTERS  = f"{R2}/{COLL_DIR}/masters/{ARCH_ID}"
R2_THUMBS   = f"{R2}/{COLL_DIR}/thumbs"
R2_PREVIEWS = f"{R2}/{COLL_DIR}/previews"
R2_LARGE    = f"{R2}/{COLL_DIR}/large"
R2_PDF      = f"{R2}/{COLL_DIR}/pdf"

URL_PREVIEW = f"{PUBLIC_BASE}/{COLL_DIR}/previews/{ARCH_ID}_{SLUG}_prev.jpg"
URL_PDF     = f"{PUBLIC_BASE}/{COLL_DIR}/pdf/{ARCH_ID}_{SLUG}.pdf"

# ─────────────────────────── Wikibase API ───────────────────────────────────
API      = "https://hunterhouse.wikibase.cloud/w/api.php"
ENV_FILE = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")
CALENDAR = "http://www.wikidata.org/entity/Q1985727"

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


def ordered_pages(src):
    """Return the TIFs in reading order: the un-numbered cover first, then the
    counter-suffixed sheets in numeric order.

    Robust + reusable: take the longest common prefix of every filename; what
    remains before ".tif" is that page's counter. The cover is the file whose
    counter is empty (e.g. "…1986.tif" vs "…19860001.tif")."""
    tifs = sorted(f for f in os.listdir(src) if f.lower().endswith(".tif"))
    if not tifs:
        return tifs
    prefix = os.path.commonprefix(tifs)

    def key(name):
        tail = name[len(prefix):].rsplit(".", 1)[0]   # counter chars, "" = cover
        return (0, -1) if tail == "" else (1, int(tail) if tail.isdigit() else 0)

    return sorted(tifs, key=key)


def sips_jpeg(src_tif, dst_jpg, max_px, quality):
    """Identical invocation to scripts/regen_previews.py. `-m <sRGB.icc>`
    matches the image into sRGB so the output JPEG carries sRGB (not the
    master's kip2300-v6- scanner profile, which causes a Chrome cyan cast)."""
    run(["sips", "-Z", str(max_px),
         "-m", "/System/Library/ColorSync/Profiles/sRGB Profile.icc",
         "-s", "format", "jpeg",
         "-s", "formatOptions", str(quality),
         src_tif, "--out", dst_jpg], capture_output=True)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


# ─────────────────────────── Wikibase write helpers ─────────────────────────
def wb_login(s, user, pw):
    t = s.get(API, params={"action": "query", "meta": "tokens",
                           "type": "login", "format": "json"}
              ).json()["query"]["tokens"]["logintoken"]
    r = s.post(API, data={"action": "login", "lgname": user,
                          "lgpassword": pw, "lgtoken": t, "format": "json"}
               ).json()
    if r["login"]["result"] != "Success":
        raise SystemExit(f"Login failed: {r['login']['result']}")
    print(f"  logged in as {r['login']['lgusername']}")


def wb_csrf(s):
    return s.get(API, params={"action": "query", "meta": "tokens",
                              "format": "json"}
                 ).json()["query"]["tokens"]["csrftoken"]


def wb_find(s, term, etype):
    r = s.get(API, params={"action": "wbsearchentities", "search": term,
                           "language": "en", "type": etype, "limit": 5,
                           "format": "json"}).json()
    return r.get("search", [])


def claim(pid, datatype, value):
    """Build one wbeditentity claim by datatype."""
    if datatype == "wikibase-item":
        dv = {"value": {"entity-type": "item", "id": value},
              "type": "wikibase-entityid"}
    elif datatype == "time":
        dv = {"value": {"time": f"+{value}-00-00T00:00:00Z", "timezone": 0,
                        "before": 0, "after": 0, "precision": 9,
                        "calendarmodel": CALENDAR}, "type": "time"}
    else:  # string and url both take a plain string value
        dv = {"value": value, "type": "string"}
    return {"mainsnak": {"snaktype": "value", "property": pid,
                         "datavalue": dv},
            "type": "statement", "rank": "normal"}


# ─────────────────────────── main ───────────────────────────────────────────
def main():
    if not os.path.isdir(SOURCE_DIR):
        raise SystemExit(f"Source folder not found: {SOURCE_DIR}")

    pages = ordered_pages(SOURCE_DIR)
    print(f"\n{'EXECUTE' if EXECUTE else 'DRY RUN'} — {ARCH_ID}  «{LABEL}»\n")
    print(f"Pages found: {len(pages)}")
    for i, f in enumerate(pages, 1):
        size_mb = os.path.getsize(os.path.join(SOURCE_DIR, f)) / 1e6
        print(f"  p{i:02d}  {f}  ({size_mb:.0f} MB)")
    if len(pages) != 10:
        print(f"\n  ⚠  expected 10 pages, found {len(pages)} — check the folder.")

    work = tempfile.mkdtemp(prefix="hh_pub_")
    cover_tif = os.path.join(SOURCE_DIR, pages[0])

    # 1. cover web tiers (so browse.html shows the publication unchanged)
    print("\nBuilding cover tiers …")
    tier_files = {}
    for suffix, (px, q) in TIERS.items():
        out = os.path.join(work, f"{ARCH_ID}_{SLUG}{suffix}")
        sips_jpeg(cover_tif, out, px, q)
        tier_files[suffix] = out
        print(f"  {os.path.basename(out)}  ({os.path.getsize(out)//1024} KB)")

    # 2. per-page JPEGs → one access PDF (Pillow, already installed)
    print(f"\nBuilding access PDF ({PDF_PX}px/page, q{PDF_Q}) …")
    page_jpgs = []
    for i, f in enumerate(pages, 1):
        pj = os.path.join(work, f"page_{i:02d}.jpg")
        sips_jpeg(os.path.join(SOURCE_DIR, f), pj, PDF_PX, PDF_Q)
        page_jpgs.append(pj)
    imgs = [Image.open(p).convert("RGB") for p in page_jpgs]
    pdf_path = os.path.join(work, f"{ARCH_ID}_{SLUG}.pdf")
    imgs[0].save(pdf_path, "PDF", save_all=True, append_images=imgs[1:],
                 resolution=150.0, quality=PDF_Q)
    print(f"  {os.path.basename(pdf_path)}  ({os.path.getsize(pdf_path)/1e6:.1f} MB)")

    # 3. SHA-256 fixity manifest over the preservation masters
    print("\nComputing SHA-256 fixity manifest …")
    manifest = os.path.join(work, f"{ARCH_ID}_SHA256.txt")
    with open(manifest, "w") as mf:
        for i, f in enumerate(pages, 1):
            digest = sha256(os.path.join(SOURCE_DIR, f))
            mf.write(f"{digest}  {ARCH_ID}_p{i:02d}.tif\n")
            print(f"  p{i:02d}  {digest[:16]}…")

    # 4. the plan
    print("\n── R2 upload plan ──")
    for i, f in enumerate(pages, 1):
        print(f"  {f}  →  {R2_MASTERS}/{ARCH_ID}_p{i:02d}.tif   (master, byte-for-byte)")
    print(f"  {os.path.basename(manifest)}  →  {R2_MASTERS}/")
    print(f"  {ARCH_ID}_{SLUG}_thumb.jpg  →  {R2_THUMBS}/")
    print(f"  {ARCH_ID}_{SLUG}_prev.jpg   →  {R2_PREVIEWS}/")
    print(f"  {ARCH_ID}_{SLUG}_large.jpg  →  {R2_LARGE}/")
    print(f"  {ARCH_ID}_{SLUG}.pdf        →  {R2_PDF}/")

    print("\n── Wikibase plan ──")
    print(f"  reuse {P1_VALUE} for P1 (publication); P79={P79_VALUE} (HHC), "
          f"P80={P80_VALUE} (R. Hunter), P82={YEAR}")
    print(f"  P96  = {URL_PREVIEW}")
    print(f"  new property “access copy” (url) ← {URL_PDF}")

    if not EXECUTE:
        # Preview goes straight to the Desktop and opens itself — no folder hunt.
        desktop_pdf = os.path.expanduser(
            f"~/Desktop/{ARCH_ID}_{SLUG}_PREVIEW.pdf")
        shutil.copyfile(pdf_path, desktop_pdf)
        shutil.rmtree(work, ignore_errors=True)   # temp scratch not needed on dry run
        print(f"\nDRY RUN complete. Preview on your Desktop (opening now):\n"
              f"  {desktop_pdf}")
        subprocess.run(["open", desktop_pdf], check=False)
        print("\nCheck page order/legibility, then say the word and I'll "
              "re-run with --execute (upload to R2 + create the item).")
        return

    # ── EXECUTE: upload, then Wikibase ──────────────────────────────────────
    s = requests.Session()
    s.headers.update({"User-Agent": "HunterHouseBot/1.0 (publication ingest)"})

    print("\nPre-flight: confirming the archive ID is free …")
    if wb_find(s, ARCH_ID, "item"):
        shutil.rmtree(work, ignore_errors=True)
        raise SystemExit(f"  ✗ something already matches {ARCH_ID} — aborting, "
                         f"nothing uploaded.")

    print("\nUploading masters (byte-for-byte) …")
    for i, f in enumerate(pages, 1):
        src = os.path.join(SOURCE_DIR, f)
        dst = f"{R2_MASTERS}/{ARCH_ID}_p{i:02d}.tif"
        print(f"  p{i:02d} ↑", flush=True)
        run(["rclone", "copyto", src, dst, "--progress"])
    run(["rclone", "copy", manifest, R2_MASTERS + "/"])
    run(["rclone", "copy", tier_files["_thumb.jpg"], R2_THUMBS + "/"])
    run(["rclone", "copy", tier_files["_prev.jpg"],  R2_PREVIEWS + "/"])
    run(["rclone", "copy", tier_files["_large.jpg"], R2_LARGE + "/"])
    # Force the public URL to download (not preview inline). PDF.js still
    # renders fine — it reads the bytes via XHR regardless of disposition.
    run(["rclone", "copy", pdf_path, R2_PDF + "/",
         "--header-upload",
         f'Content-Disposition: attachment; filename="{os.path.basename(pdf_path)}"'])
    print("  all objects uploaded.")

    print("\nWikibase …")
    env = load_env(ENV_FILE)
    wb_login(s, env["WIKIBASE_BOT_USER"], env["WIKIBASE_BOT_PASSWORD"])
    token = wb_csrf(s)

    # ensure the "access copy" property (reuse if it already exists)
    hits = [h for h in wb_find(s, "access copy", "property")
            if h.get("label", "").lower() == "access copy"]
    if hits:
        access_pid = hits[0]["id"]
        print(f"  reusing property {access_pid} (access copy)")
    else:
        pdata = {"labels": {"en": {"language": "en", "value": "access copy"}},
                 "descriptions": {"en": {"language": "en", "value":
                    "URL of an access derivative (e.g. a multi-page PDF) of "
                    "this item; preservation masters are held separately"}},
                 "datatype": "url"}
        r = s.post(API, data={"action": "wbeditentity", "new": "property",
                              "data": json.dumps(pdata), "token": token,
                              "format": "json"}).json()
        if "error" in r:
            raise SystemExit(f"  ✗ property create failed: {r['error']}")
        access_pid = r["entity"]["id"]
        print(f"  created property {access_pid} (access copy, url)")

    data = {
        "labels":       {"en": {"language": "en", "value": LABEL}},
        "descriptions": {"en": {"language": "en", "value": DESCRIPTION}},
        "claims": [
            claim("P1",  "wikibase-item", P1_VALUE),
            claim("P2",  "string",        ARCH_ID),
            claim("P79", "wikibase-item", P79_VALUE),
            claim("P80", "wikibase-item", P80_VALUE),
            claim("P82", "time",          YEAR),
            claim("P96", "url",           URL_PREVIEW),
            claim(access_pid, "url",      URL_PDF),
        ],
    }
    r = s.post(API, data={"action": "wbeditentity", "new": "item",
                          "data": json.dumps(data), "token": token,
                          "format": "json"}).json()
    if "error" in r:
        raise SystemExit(f"  ✗ item create failed: {r['error']}")
    qid = r["entity"]["id"]
    print(f"  created item {qid}  ({ARCH_ID})")
    print(f"\nDone.\n  https://hunterhouse.wikibase.cloud/wiki/Item:{qid}")
    print(f"  {URL_PDF}")

    # §11.1 HIGH part 2b — fail-safe sidecar push to R2 (see ingest_item.py
    # for rationale).
    try:
        subprocess.run(
            ["python3", os.path.join(os.path.dirname(__file__),
                                     "sync_one_metadata.py"),
             ARCH_ID, "--execute", "--quiet"],
            timeout=60, check=False,
        )
    except Exception as _e:
        print(f"  ⚠ sidecar sync skipped (non-fatal): {_e}")

    # Static permalink page (best-effort; WDQS lag → re-run build_item_pages.py).
    try:
        subprocess.run(
            ["python3", os.path.join(os.path.dirname(__file__),
                                     "build_item_pages.py"), "--one", ARCH_ID],
            timeout=120, check=False,
        )
    except Exception as _e:
        print(f"  ⚠ permalink page generation skipped (non-fatal): {_e}")

    shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
