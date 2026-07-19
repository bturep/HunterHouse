#!/usr/bin/env python3
"""
Renumber the 50 PUBLIC Frances Hunter Collection objects from the type-embedded
series (HH-FRH-DOC-##/PHOTO-##/SKB-##) to a generic flat number HH-FRH-#### —
2026-07-19, Brandon's call (match every other collection's plain scheme; the
type is metadata, not the ID).

Order (Brandon): Rick Working on Square leads → 0001; then DOC-01/02/03, the
Music-for-Solo-Performer photo (so it follows the School of Music program),
the two No-More-Mondays, the 41 house photos 05..45, then the 2 sketchbooks.

Per item, safely (old→new namespaces are DISJOINT — no collision risk):
  1. write P97 legacy = old ID
  2. R2: copy every {oldID}* object to {newID}* (server-side), verify, delete old
  3. Wikibase P2 → new ID; P95/P96/P143 URLs swapped old→new
Gated letters (HH-FRH-CORR / the 73 R2 records) are OUT OF SCOPE (Brandon).

DRY RUN default (prints the full plan). --execute to write.
Post-run (separate, by hand): build_item_pages, snapshot, PUBLIC_PAGES keys,
delete stale archive/*.html, Main_Page/docs.
"""
import json
import os
import subprocess
import sys
import urllib.request

import requests

API = "https://hunterhouse.wikibase.cloud/w/api.php"
SPARQL = "https://hunterhouse.wikibase.cloud/query/sparql"
ENV_FILE = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")
R2 = "hh-r2:hunter-house-archive"
CDIR = "frances-hunter-collection"
PUBLIC_BASE = "https://archive.hunterhousefoundation.com"

# ── the order → new IDs ──────────────────────────────────────────────────────
ORDER = (["HH-FRH-PHOTO-03",                                   # Rick w/ Square → 0001
          "HH-FRH-DOC-01", "HH-FRH-DOC-02", "HH-FRH-DOC-03",  # 0002-0004
          "HH-FRH-PHOTO-04",                                   # Music for Solo Performer → 0005 (follows 0004)
          "HH-FRH-PHOTO-01", "HH-FRH-PHOTO-02"]                # No More Mondays
         + [f"HH-FRH-PHOTO-{n:02d}" for n in range(5, 46)]     # house photos 05..45
         + ["HH-FRH-SKB-01", "HH-FRH-SKB-02"])
NEW = {old: f"HH-FRH-{i:04d}" for i, old in enumerate(ORDER, 1)}

EXECUTE = "--execute" in sys.argv


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def load_env():
    env = {}
    for line in open(ENV_FILE):
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip()
    return env


def sparql(q):
    req = urllib.request.Request(SPARQL, data=q.encode(),
                                 headers={"Content-Type": "application/sparql-query",
                                          "Accept": "application/sparql-results+json"})
    return json.load(urllib.request.urlopen(req))["results"]["bindings"]


def qid_for(old):
    r = sparql('SELECT ?i WHERE { ?i <https://hunterhouse.wikibase.cloud/prop/direct/P2> "'
               + old + '" }')
    return r[0]["i"]["value"].split("/")[-1] if r else None


def r2_objects(old):
    """All R2 object paths (collection-relative) whose basename starts with old."""
    out = run(["rclone", "lsf", f"{R2}/{CDIR}/", "-R"]).stdout.splitlines()
    return [p for p in out if os.path.basename(p).startswith(old)]


def wb_login(s, env):
    t = s.get(API, params={"action": "query", "meta": "tokens", "type": "login",
                           "format": "json"}).json()["query"]["tokens"]["logintoken"]
    r = s.post(API, data={"action": "login", "lgname": env["WIKIBASE_BOT_USER"],
                          "lgpassword": env["WIKIBASE_BOT_PASSWORD"], "lgtoken": t,
                          "format": "json"}).json()
    if r["login"]["result"] != "Success":
        raise SystemExit("login failed")


def csrf(s):
    return s.get(API, params={"action": "query", "meta": "tokens",
                              "format": "json"}).json()["query"]["tokens"]["csrftoken"]


def main():
    print(f"{'EXECUTE' if EXECUTE else 'DRY RUN'} — renumber {len(NEW)} FRH public objects\n")
    s = requests.Session()
    s.headers.update({"User-Agent": "HunterHouseBot/1.0 (renumber-frh)"})
    tok = None
    if EXECUTE:
        env = load_env()
        wb_login(s, env)
        tok = csrf(s)

    total_r2 = 0
    for old, new in NEW.items():
        qid = qid_for(old)
        if not qid:
            print(f"  ⚠ {old}: no QID (already renumbered?) — SKIP")
            continue
        objs = r2_objects(old)
        total_r2 += len(objs)
        print(f"── {old} → {new}  ({qid})  {len(objs)} R2 objects")

        if not EXECUTE:
            for p in objs[:3]:
                print(f"     {os.path.basename(p)}  →  {os.path.basename(p).replace(old, new, 1)}")
            if len(objs) > 3:
                print(f"     … +{len(objs)-3} more")
            continue

        # 1. R2 copy → verify each (read-after-write consistent) → delete.
        #    p is CDIR-relative (e.g. "large/x.jpg" or "x.json"); keep the CDIR.
        newpaths = []
        for p in objs:
            d = os.path.dirname(p)
            newp = (d + "/" if d else "") + os.path.basename(p).replace(old, new, 1)
            run(["rclone", "copyto", f"{R2}/{CDIR}/{p}", f"{R2}/{CDIR}/{newp}"])
            newpaths.append(newp)
        for newp in newpaths:                      # per-object existence (not bulk list — list lags)
            if not run(["rclone", "lsf", f"{R2}/{CDIR}/{newp}"]).stdout.strip():
                raise SystemExit(f"  ✗ {new}: copy missing {newp} — ABORT before delete")
        for p in objs:
            run(["rclone", "deletefile", f"{R2}/{CDIR}/{p}"])
        print(f"     R2: {len(objs)} renamed + verified")

        # 2. Wikibase: P97 legacy, P2, and URL claims
        ent = s.get(API, params={"action": "wbgetentities", "ids": qid,
                                 "props": "claims", "format": "json"}).json()["entities"][qid]["claims"]
        # P97 legacy (add, skip if already there)
        if not any(c["mainsnak"].get("datavalue", {}).get("value") == old
                   for c in ent.get("P97", [])):
            s.post(API, data={"action": "wbcreateclaim", "entity": qid, "property": "P97",
                              "snaktype": "value", "value": json.dumps(old), "token": tok,
                              "format": "json"})
        # P2 → new
        g = ent["P2"][0]["id"]
        s.post(API, data={"action": "wbsetclaimvalue", "claim": g, "snaktype": "value",
                          "value": json.dumps(new), "token": tok, "format": "json"})
        # P95/P96/P143 URL swaps
        for pid in ("P95", "P96", "P143"):
            for c in ent.get(pid, []):
                url = c["mainsnak"]["datavalue"]["value"]
                if old in url:
                    s.post(API, data={"action": "wbsetclaimvalue", "claim": c["id"],
                                      "snaktype": "value", "value": json.dumps(url.replace(old, new)),
                                      "token": tok, "format": "json"})
        # description refresh (carries the old ID)
        print(f"     WB: P2→{new}, P97={old}, URLs swapped")

    print(f"\n{'DRY RUN — ' if not EXECUTE else ''}total R2 objects to rename: {total_r2}")
    if not EXECUTE:
        print("\nrun with --execute to apply. THEN by hand:")
        print("  • browse/next PUBLIC_PAGES keys: DOC-03→0004, SKB-01→0049, SKB-02→0050")
        print("  • build_item_pages.py ; delete stale archive/HH-FRH-{DOC,PHOTO,SKB}-*.html")
        print("  • build_catalogue_snapshot.py --execute ; Main_Page/docs ; next-ID → HH-FRH-0051")


if __name__ == "__main__":
    main()
