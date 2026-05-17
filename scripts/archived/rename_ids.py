#!/usr/bin/env python3
"""
ID rename migration: HH-A-XXXX → HH-HHC-XXXX / HH-CAA-XXXX

Reads mapping from:
  ~/Documents/hh-wikibase-migration/data/snapshots/mapping_id_rename.tsv

For each item:
  1. Writes old P2 value to P97 (legacy identifier) — Wikibase undo anchor
  2. Updates P2 to new ID
  3. Updates P96 (preview URL) if present
  4. Updates P95 (master URL) if present

Usage:
  python3 scripts/rename_ids.py --dry-run   # preview only, no changes
  python3 scripts/rename_ids.py             # live run

Run from HunterHouse repo root.
"""

import csv, json, os, sys, time, argparse
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API     = "https://hunterhouse.wikibase.cloud/w/api.php"
ENV     = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")
MAPPING = os.path.expanduser(
    "~/Documents/hh-wikibase-migration/data/snapshots/mapping_id_rename.tsv")

# ── credentials ──────────────────────────────────────────────────────────────

def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env

# ── API helpers ───────────────────────────────────────────────────────────────

def login(s, username, password):
    r = s.get(API, params={"action":"query","meta":"tokens","type":"login","format":"json"})
    token = r.json()["query"]["tokens"]["logintoken"]
    r = s.post(API, data={"action":"login","lgname":username,
                           "lgpassword":password,"lgtoken":token,"format":"json"})
    result = r.json()["login"]["result"]
    if result != "Success":
        raise SystemExit(f"Login failed: {result}")
    print(f"Logged in as {r.json()['login']['lgusername']}\n")

def csrf(s):
    r = s.get(API, params={"action":"query","meta":"tokens","format":"json"})
    return r.json()["query"]["tokens"]["csrftoken"]

def get_claims(s, qid, prop):
    r = s.get(API, params={"action":"wbgetclaims","entity":qid,
                            "property":prop,"format":"json"})
    return r.json().get("claims", {}).get(prop, [])

def add_string_claim(s, token, qid, prop, value, dry_run):
    if dry_run:
        print(f"    [DRY] wbcreateclaim {qid} {prop} = {value!r}")
        return True, "dry-run"
    r = s.post(API, data={
        "action":"wbcreateclaim","entity":qid,"snaktype":"value",
        "property":prop,"value":json.dumps(value),
        "token":token,"format":"json"
    })
    d = r.json()
    if "error" in d:
        return False, d["error"].get("info", str(d["error"]))
    return True, "ok"

def set_string_claim(s, token, qid, prop, value, dry_run):
    """Set a string claim, replacing any existing value."""
    claims = get_claims(s, qid, prop)
    if claims:
        claim_id = claims[0]["id"]
        if dry_run:
            print(f"    [DRY] wbsetclaimvalue {claim_id} = {value!r}")
            return True, "dry-run"
        r = s.post(API, data={
            "action":"wbsetclaimvalue","claim":claim_id,"snaktype":"value",
            "value":json.dumps(value),"token":token,"format":"json"
        })
        d = r.json()
        if "error" in d:
            return False, d["error"].get("info", str(d["error"]))
        return True, "ok"
    else:
        return add_string_claim(s, token, qid, prop, value, dry_run)

def set_url_claim(s, token, qid, prop, url, dry_run):
    """Set a URL claim, replacing any existing value."""
    claims = get_claims(s, qid, prop)
    value = {"value": url, "type": "string"}
    if claims:
        claim_id = claims[0]["id"]
        if dry_run:
            print(f"    [DRY] wbsetclaimvalue {claim_id} (URL) = {url!r}")
            return True, "dry-run"
        r = s.post(API, data={
            "action":"wbsetclaimvalue","claim":claim_id,"snaktype":"value",
            "value":json.dumps(url),"token":token,"format":"json"
        })
        d = r.json()
        if "error" in d:
            return False, d["error"].get("info", str(d["error"]))
        return True, "ok"
    else:
        if dry_run:
            print(f"    [DRY] wbcreateclaim {qid} {prop} (URL) = {url!r}")
            return True, "dry-run"
        r = s.post(API, data={
            "action":"wbcreateclaim","entity":qid,"snaktype":"value",
            "property":prop,"value":json.dumps(url),
            "token":token,"format":"json"
        })
        d = r.json()
        if "error" in d:
            return False, d["error"].get("info", str(d["error"]))
        return True, "ok"

# ── main ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without writing to Wikibase")
    parser.add_argument("--limit", type=int, default=None,
                        help="Only process first N items (for testing)")
    args = parser.parse_args()

    env = load_env(ENV)
    bot_user = env["WIKIBASE_BOT_USER"]
    bot_pass = env["WIKIBASE_BOT_PASSWORD"]

    with open(MAPPING, newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))

    if args.limit:
        rows = rows[:args.limit]

    print(f"{'DRY RUN — ' if args.dry_run else ''}Processing {len(rows)} items\n")

    if not args.dry_run:
        confirm = input(f"About to write to Wikibase. Type YES to confirm: ")
        if confirm.strip() != "YES":
            raise SystemExit("Aborted.")

    s = requests.Session()
    retries = Retry(total=5, backoff_factor=1.5,
                    status_forcelist=[500, 502, 503, 504],
                    allowed_methods=["GET", "POST"])
    s.mount("https://", HTTPAdapter(max_retries=retries))
    s.headers.update({"User-Agent": "HunterHouseBot/1.0"})
    login(s, bot_user, bot_pass)
    token = csrf(s)

    errors = []
    skipped = 0
    for i, row in enumerate(rows, 1):
        qid        = row["qid"]
        old_id     = row["old_id"]
        new_id     = row["new_id"]
        old_prev   = row["old_preview"]
        new_prev   = row["new_preview"]
        old_master = row["old_master"]
        new_master = row["new_master"]

        # Skip items already renamed (resume after partial run)
        current_claims = get_claims(s, qid, "P2")
        if current_claims:
            current_p2 = current_claims[0].get("mainsnak",{}).get("datavalue",{}).get("value","")
            if current_p2 == new_id:
                print(f"[{i:3d}/{len(rows)}] {qid}  SKIP (already {new_id})")
                skipped += 1
                continue

        print(f"[{i:3d}/{len(rows)}] {qid}  {old_id} → {new_id}")

        # Step 1: Write old ID to P97 (legacy identifier) — undo anchor
        ok, msg = add_string_claim(s, token, qid, "P97", old_id, args.dry_run)
        if not ok:
            print(f"    WARN P97: {msg}")

        # Step 2: Update P2 (archive ID) to new value
        ok, msg = set_string_claim(s, token, qid, "P2", new_id, args.dry_run)
        if not ok:
            print(f"    ERROR P2: {msg}")
            errors.append((qid, "P2", msg))
            continue

        # Step 3: Update P96 (preview URL)
        if new_prev:
            ok, msg = set_url_claim(s, token, qid, "P96", new_prev, args.dry_run)
            if not ok:
                print(f"    WARN P96: {msg}")

        # Step 4: Update P95 (master URL)
        if new_master:
            ok, msg = set_url_claim(s, token, qid, "P95", new_master, args.dry_run)
            if not ok:
                print(f"    WARN P95: {msg}")

        if not args.dry_run:
            time.sleep(0.5)  # be polite to the API

    print(f"\n{'DRY RUN complete' if args.dry_run else 'Done'}. "
          f"Errors: {len(errors)}  Skipped (already done): {skipped}")
    if errors:
        for e in errors:
            print(f"  {e}")

if __name__ == "__main__":
    main()
