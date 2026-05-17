#!/usr/bin/env python3
"""
REVERT script for the HHC renumber migration.

Reads mapping_hhc_renumber.tsv and does the inverse:
  - Restores P2 from old_id (HH-HHC-0036 etc.)
  - Restores P96 from old_preview
  - Restores P95 from old_master
  - Removes the P97 entries added by renumber_hhc.py

Only run this if something went wrong with renumber_hhc.py.

Usage:
  python3 scripts/revert_hhc_renumber.py --dry-run
  python3 scripts/revert_hhc_renumber.py
"""

import csv, json, os, time, argparse
import requests

API     = "https://hunterhouse.wikibase.cloud/w/api.php"
ENV     = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")
MAPPING = os.path.expanduser(
    "~/Documents/hh-wikibase-migration/data/snapshots/mapping_hhc_renumber.tsv")


def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


def login(s, username, password):
    r = s.get(API, params={"action": "query", "meta": "tokens",
                            "type": "login", "format": "json"})
    token = r.json()["query"]["tokens"]["logintoken"]
    r = s.post(API, data={"action": "login", "lgname": username,
                           "lgpassword": password, "lgtoken": token,
                           "format": "json"})
    result = r.json()["login"]["result"]
    if result != "Success":
        raise SystemExit(f"Login failed: {result}")
    print(f"Logged in as {r.json()['login']['lgusername']}\n")


def csrf(s):
    r = s.get(API, params={"action": "query", "meta": "tokens", "format": "json"})
    return r.json()["query"]["tokens"]["csrftoken"]


def get_claims(s, qid, prop):
    r = s.get(API, params={"action": "wbgetclaims", "entity": qid,
                            "property": prop, "format": "json"})
    return r.json().get("claims", {}).get(prop, [])


def set_string_claim(s, token, qid, prop, value, dry_run):
    claims = get_claims(s, qid, prop)
    if claims:
        claim_id = claims[0]["id"]
        if dry_run:
            print(f"    [DRY] restore {prop} = {value!r}")
            return
        s.post(API, data={"action": "wbsetclaimvalue", "claim": claim_id,
                           "snaktype": "value", "value": json.dumps(value),
                           "token": token, "format": "json"})
    else:
        if dry_run:
            print(f"    [DRY] create {prop} = {value!r}")
            return
        s.post(API, data={"action": "wbcreateclaim", "entity": qid,
                           "snaktype": "value", "property": prop,
                           "value": json.dumps(value), "token": token,
                           "format": "json"})


def remove_p97_claim(s, token, qid, old_id, dry_run):
    """Remove the P97 entry that matches old_id (added by renumber_hhc.py)."""
    claims = get_claims(s, qid, "P97")
    for claim in claims:
        val = claim.get("mainsnak", {}).get("datavalue", {}).get("value", "")
        if val == old_id:
            if dry_run:
                print(f"    [DRY] remove P97 = {old_id!r}")
                return
            s.post(API, data={"action": "wbremoveclaims",
                               "claim": claim["id"], "token": token,
                               "format": "json"})
            return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    env = load_env(ENV)
    with open(MAPPING, newline="") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    if args.limit:
        rows = rows[:args.limit]

    print(f"{'DRY RUN — ' if args.dry_run else ''}REVERT: {len(rows)} HHC items\n")

    if not args.dry_run:
        confirm = input("This will REVERT the HHC renumber. Type YES to confirm: ")
        if confirm.strip() != "YES":
            raise SystemExit("Aborted.")

    s = requests.Session()
    s.headers.update({"User-Agent": "HunterHouseBot/1.0"})
    login(s, env["WIKIBASE_BOT_USER"], env["WIKIBASE_BOT_PASSWORD"])
    token = csrf(s)

    for i, row in enumerate(rows, 1):
        qid      = row["qid"]
        old_id   = row["old_id"]   # HH-HHC-0036 etc. — restore this
        old_prev = row["old_preview"]
        old_mast = row["old_master"]

        print(f"[{i:3d}/{len(rows)}] {qid}  → restore {old_id}")

        set_string_claim(s, token, qid, "P2", old_id, args.dry_run)
        if old_prev:
            set_string_claim(s, token, qid, "P96", old_prev, args.dry_run)
        if old_mast:
            set_string_claim(s, token, qid, "P95", old_mast, args.dry_run)
        remove_p97_claim(s, token, qid, old_id, args.dry_run)

        if not args.dry_run:
            time.sleep(0.3)

    print(f"\n{'DRY RUN complete' if args.dry_run else 'Revert done.'}")


if __name__ == "__main__":
    main()
