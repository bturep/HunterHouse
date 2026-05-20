#!/usr/bin/env python3
"""
CAA renumber: 4-way rotation 0025–0028 + 2-way swap 0029↔0032.

Why a two-pass via temp IDs?
  P2 is the public archive ID. Logically it must be unique, so we cannot
  set HH-CAA-0026 on one item while another item still holds HH-CAA-0026.
  Both operations here are cycles (28→25→26→27→28 and 29↔32), so a single-
  pass rename would always collide. The script first parks every affected
  item at a temp P2 value (HH-CAA-T<old>), then assigns the final values.

R2 is non-destructive:
  rclone copyto leaves the source untouched. We copy every old file to
  its final name BEFORE touching Wikibase, so during the migration window
  both URLs are live. Old files are deleted only after the verify step.

Filename derivation:
  Only the leading "HH-CAA-NNNN" prefix changes. The descriptive suffix
  (e.g. "_Scheme_II_Pencil_Studies_1of3_1985-01-01") is content-true and
  stays with the item.

Modes:
  --dry-run            print planned ops without touching Wikibase or R2
  --execute            do it (prompts YES first)
  --skip-r2            skip the R2 copies (e.g. if already done)
  --skip-wikibase      skip the Wikibase writes (e.g. if already done)
  --skip-cleanup       leave old R2 files in place (final delete pass)
  --verify-only        just re-query Wikibase + HEAD the URLs

Mapping TSV: ~/Documents/hh-wikibase-migration/data/snapshots/mapping_caa_25_32.tsv
"""

import argparse, csv, json, os, subprocess, sys, time
import urllib.request
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API     = "https://hunterhouse.wikibase.cloud/w/api.php"
SPARQL  = "https://hunterhouse.wikibase.cloud/query/sparql"
ENV     = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")
MAPPING = os.path.expanduser(
    "~/Documents/hh-wikibase-migration/data/snapshots/mapping_caa_25_32.tsv")

# R2 layout — four tiers per item, one filename pattern. Suffix per tier
# differs (master keeps .tif, the three jpg tiers add _thumb/_prev/_large).
R2_REMOTE = "hh-r2:hunter-house-archive/canadian-architecture-archive"
TIERS = [
    ("masters",  ".tif",       ""),         # master TIF
    ("thumbs",   ".jpg",       "_thumb"),
    ("previews", ".jpg",       "_prev"),
    ("large",    ".jpg",       "_large"),
]


# ── env / wikibase plumbing ──────────────────────────────────────────────

def load_env(path):
    env = {}
    with open(path) as f:
        for ln in f:
            ln = ln.strip()
            if ln and not ln.startswith("#") and "=" in ln:
                k, _, v = ln.partition("=")
                env[k.strip()] = v.strip()
    return env


def login(s, username, password):
    r = s.get(API, params={"action": "query", "meta": "tokens",
                           "type": "login", "format": "json"})
    token = r.json()["query"]["tokens"]["logintoken"]
    r = s.post(API, data={"action": "login", "lgname": username,
                          "lgpassword": password, "lgtoken": token,
                          "format": "json"})
    if r.json()["login"]["result"] != "Success":
        raise SystemExit(f"Login failed: {r.json()['login']}")
    print(f"  logged in as {r.json()['login']['lgusername']}")


def csrf(s):
    return s.get(API, params={"action": "query", "meta": "tokens",
                              "format": "json"}).json()["query"]["tokens"]["csrftoken"]


def get_claims(s, qid, prop):
    return s.get(API, params={"action": "wbgetclaims", "entity": qid,
                              "property": prop, "format": "json"}
                ).json().get("claims", {}).get(prop, [])


def add_string_claim(s, token, qid, prop, value, dry):
    if dry:
        print(f"    [DRY] wbcreateclaim {qid} {prop} = {value!r}")
        return True
    r = s.post(API, data={"action": "wbcreateclaim", "entity": qid,
                          "snaktype": "value", "property": prop,
                          "value": json.dumps(value), "token": token,
                          "format": "json"}).json()
    if "error" in r:
        print(f"    ERROR {qid} {prop}: {r['error'].get('info','?')}")
        return False
    return True


def set_string_claim(s, token, qid, prop, value, dry):
    claims = get_claims(s, qid, prop)
    if claims:
        cid = claims[0]["id"]
        if dry:
            print(f"    [DRY] wbsetclaimvalue {cid} ({prop}) = {value!r}")
            return True
        r = s.post(API, data={"action": "wbsetclaimvalue", "claim": cid,
                              "snaktype": "value",
                              "value": json.dumps(value),
                              "token": token, "format": "json"}).json()
        if "error" in r:
            print(f"    ERROR {qid} {prop}: {r['error'].get('info','?')}")
            return False
        return True
    return add_string_claim(s, token, qid, prop, value, dry)


# ── R2 plumbing ──────────────────────────────────────────────────────────

def rclone(args, dry):
    cmd = ["rclone"] + args
    if dry:
        print(f"    [DRY] $ {' '.join(cmd)}")
        return True
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"    ERROR rclone: {e.stderr.strip()}")
        return False


def r2_url(rel):
    return f"https://archive.hunterhousefoundation.com/canadian-architecture-archive/{rel}"


def head(url):
    try:
        req = urllib.request.Request(url, method="HEAD")
        with urllib.request.urlopen(req, timeout=10) as r:
            return r.status
    except Exception as e:
        return str(e)


# ── per-tier filename derivation ─────────────────────────────────────────

def discover_filenames(qid, old_id):
    """Look up the live P95/P96 URLs to discover the exact descriptor
    suffix used in the existing filenames. Returns dict per tier with
    (folder, filename) for the OLD file. Master comes from P95; the
    three jpg tiers all share the descriptor (same source filename
    stem)."""
    # P95 = master URL → tells us the descriptor for everything.
    q = f"""
    PREFIX wdt: <https://hunterhouse.wikibase.cloud/prop/direct/>
    SELECT ?master ?img WHERE {{
      <https://hunterhouse.wikibase.cloud/entity/{qid}> wdt:P95 ?master .
      OPTIONAL {{ <https://hunterhouse.wikibase.cloud/entity/{qid}> wdt:P96 ?img }}
    }}"""
    r = requests.post(SPARQL, data=q,
                      headers={"Content-Type": "application/sparql-query",
                               "Accept": "application/sparql-results+json"})
    r.raise_for_status()
    b = r.json()["results"]["bindings"]
    if not b:
        raise SystemExit(f"  {qid} has no P95 — cannot derive filenames")
    master = b[0]["master"]["value"]
    fname = master.rsplit("/", 1)[-1]          # HH-CAA-0028_Hunter_House_…1986-01-01.tif
    if not fname.startswith(old_id + "_"):
        raise SystemExit(f"  master filename {fname} does not start with {old_id}_")
    descriptor = fname[len(old_id)+1:-len(".tif")]  # the bit between ID and ext
    return descriptor


def files_for(old_id, descriptor):
    """List the four (folder, old_name, new_name) tuples for an item, given
    the descriptor and the target new_id. Caller passes new_id when needed."""
    out = []
    for folder, ext, suffix in TIERS:
        old_name = f"{old_id}_{descriptor}{suffix}{ext}"
        out.append((folder, old_name))
    return out


def derive_new(old_name, old_id, new_id):
    if not old_name.startswith(old_id + "_"):
        raise ValueError(f"{old_name} doesn't start with {old_id}_")
    return new_id + old_name[len(old_id):]


# ── ops ──────────────────────────────────────────────────────────────────

def temp_id(old_id):
    """HH-CAA-0028 → HH-CAA-T0028. Unique by construction; no real items
    use this prefix."""
    return old_id.replace("HH-CAA-", "HH-CAA-T")


def load_mapping():
    with open(MAPPING, newline="") as f:
        rows = [r for r in csv.DictReader(f, delimiter="\t")]
    # Validate cycles: every old_id appears exactly once as old, exactly once as new.
    olds = [r["old_id"] for r in rows]
    news = [r["new_id"] for r in rows]
    if sorted(olds) != sorted(news):
        raise SystemExit(f"Mapping is not a permutation:\n  olds={sorted(olds)}\n  news={sorted(news)}")
    return rows


def cmd_dry_or_execute(args, dry):
    rows = load_mapping()
    env = load_env(ENV)

    # ── discover descriptors first (read-only, safe) ────────────────────
    print("Discovering R2 filenames for each item…")
    for r in rows:
        r["descriptor"] = discover_filenames(r["qid"], r["old_id"])
        print(f"  {r['qid']}  {r['old_id']}  desc={r['descriptor']!r}")

    # ── R2: copy old → final names (non-destructive) ────────────────────
    if not args.skip_r2:
        print("\nR2 copy: old name → final name (originals untouched)")
        for r in rows:
            old_id, new_id = r["old_id"], r["new_id"]
            for folder, old_name in files_for(old_id, r["descriptor"]):
                new_name = derive_new(old_name, old_id, new_id)
                src = f"{R2_REMOTE}/{folder}/{old_name}"
                dst = f"{R2_REMOTE}/{folder}/{new_name}"
                print(f"  copy {folder}/{old_name}  →  {new_name}")
                if not rclone(["copyto", src, dst], dry):
                    raise SystemExit("R2 copy failed — aborting")

    # ── Wikibase ────────────────────────────────────────────────────────
    if not args.skip_wikibase:
        s = requests.Session()
        s.mount("https://", HTTPAdapter(max_retries=Retry(
            total=5, backoff_factor=1.5,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["GET", "POST"])))
        s.headers.update({"User-Agent": "HunterHouseBot/1.0"})
        print("\nWikibase: login")
        login(s, env["WIKIBASE_BOT_USER"], env["WIKIBASE_BOT_PASSWORD"])
        token = csrf(s)

        # P97: write current ID as additional legacy ID BEFORE we mutate P2.
        print("\nP97 (legacy ID) — additive write per item")
        for r in rows:
            print(f"  {r['qid']}  add P97 = {r['old_id']!r}")
            add_string_claim(s, token, r["qid"], "P97", r["old_id"], dry)
            if not dry: time.sleep(0.4)

        # P2 pass 1: park each item at temp ID.
        print("\nP2 pass 1 — park at temp IDs")
        for r in rows:
            t = temp_id(r["old_id"])
            print(f"  {r['qid']}  P2: {r['old_id']} → {t}")
            if not set_string_claim(s, token, r["qid"], "P2", t, dry):
                raise SystemExit("P2 park failed — aborting")
            if not dry: time.sleep(0.4)

        # P2 pass 2: assign final IDs.
        print("\nP2 pass 2 — assign final IDs")
        for r in rows:
            t = temp_id(r["old_id"])
            print(f"  {r['qid']}  P2: {t} → {r['new_id']}")
            if not set_string_claim(s, token, r["qid"], "P2", r["new_id"], dry):
                raise SystemExit("P2 final failed — aborting")
            if not dry: time.sleep(0.4)

        # P95 + P96: point to final filenames.
        print("\nP95/P96 — point at final R2 URLs")
        for r in rows:
            old_id, new_id = r["old_id"], r["new_id"]
            for folder, old_name in files_for(old_id, r["descriptor"]):
                new_name = derive_new(old_name, old_id, new_id)
                if folder == "masters":
                    url = r2_url(f"masters/{new_name}")
                    print(f"  {r['qid']}  P95 → {url}")
                    set_string_claim(s, token, r["qid"], "P95", url, dry)
                elif folder == "previews":
                    url = r2_url(f"previews/{new_name}")
                    print(f"  {r['qid']}  P96 → {url}")
                    set_string_claim(s, token, r["qid"], "P96", url, dry)
                # thumbs + large aren't tracked as their own claims; browse.html
                # derives their URLs from P96 by string-replace at render time.
            if not dry: time.sleep(0.4)


def cmd_verify():
    rows = load_mapping()
    for r in rows:
        r["descriptor"] = discover_filenames(r["qid"], r["new_id"])  # AFTER renumber
    print("\nVerify — SPARQL re-query")
    qids = ",".join(f"wd:{r['qid']}" for r in rows)
    q = f"""
    PREFIX wd: <https://hunterhouse.wikibase.cloud/entity/>
    PREFIX wdt: <https://hunterhouse.wikibase.cloud/prop/direct/>
    SELECT ?item ?archId ?master ?img WHERE {{
      VALUES ?item {{ {qids} }}
      ?item wdt:P2 ?archId .
      OPTIONAL {{ ?item wdt:P95 ?master }}
      OPTIONAL {{ ?item wdt:P96 ?img }}
    }} ORDER BY ?archId
    """
    r = requests.post(SPARQL, data=q,
                      headers={"Content-Type": "application/sparql-query",
                               "Accept": "application/sparql-results+json"})
    for b in r.json()["results"]["bindings"]:
        qid = b["item"]["value"].split("/")[-1]
        print(f"  {qid}  P2={b['archId']['value']}")
        if "master" in b: print(f"        P95={b['master']['value']}")
        if "img"    in b: print(f"        P96={b['img']['value']}")

    print("\nVerify — R2 HEAD on each final-name file")
    for r in rows:
        new_id = r["new_id"]
        for folder, old_name in files_for(r["old_id"], r["descriptor"]):
            # discover_filenames is now keyed on new_id (after renumber),
            # so files_for(old_id, descriptor) returns filenames keyed on
            # old_id — derive the new-name to HEAD-check it lives.
            new_name = derive_new(old_name, r["old_id"], new_id)
            url = r2_url(f"{folder}/{new_name}")
            status = head(url)
            ok = "OK " if status == 200 else "FAIL"
            print(f"  [{ok}] {status}  {folder}/{new_name}")


def cmd_cleanup(dry):
    rows = load_mapping()
    for r in rows:
        r["descriptor"] = discover_filenames(r["qid"], r["new_id"])
    print("\nCleanup — delete OLD R2 files (originals)")
    for r in rows:
        for folder, old_name in files_for(r["old_id"], r["descriptor"]):
            path = f"{R2_REMOTE}/{folder}/{old_name}"
            print(f"  delete {folder}/{old_name}")
            rclone(["deletefile", path], dry)


def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run",     action="store_true")
    g.add_argument("--execute",     action="store_true")
    g.add_argument("--verify-only", action="store_true")
    g.add_argument("--cleanup",     action="store_true", help="Delete old R2 files (post-verify)")
    p.add_argument("--skip-r2",        action="store_true")
    p.add_argument("--skip-wikibase",  action="store_true")
    args = p.parse_args()

    if args.verify_only:
        cmd_verify()
        return
    if args.cleanup:
        cmd_cleanup(dry=False)
        return

    dry = args.dry_run
    if not dry:
        print("ABOUT TO MUTATE R2 + WIKIBASE.")
        confirm = input("Type YES to proceed: ")
        if confirm.strip() != "YES":
            raise SystemExit("Aborted.")
    cmd_dry_or_execute(args, dry)


if __name__ == "__main__":
    main()
