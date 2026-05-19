#!/usr/bin/env python3
"""
Mint (or find) a single Wikibase property. Idempotent: if a property with the
exact label already exists it is reused, not duplicated.

Reuses the proven login/CSRF flow from scripts/patch_dates.py and the
wbeditentity-new pattern from scripts/ingest_publication.py. Credentials load
from ~/Documents/hh-wikibase-migration/.env.

Usage:
  python3 scripts/mint_property.py --label "display rotation" \
      --desc "…" --datatype string
"""

import argparse
import json
import os

import requests

API = "https://hunterhouse.wikibase.cloud/w/api.php"
ENV_FILE = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")


def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--desc", default="")
    ap.add_argument("--datatype", default="string",
                    help="string | url | wikibase-item | time | quantity | external-id …")
    args = ap.parse_args()

    env = load_env(ENV_FILE)
    s = requests.Session()
    s.headers.update({"User-Agent": "HunterHouseBot/1.0 (mint_property)"})

    # idempotency — exact-label match wins, no duplicate property
    hits = [h for h in s.get(API, params={
        "action": "wbsearchentities", "search": args.label, "language": "en",
        "type": "property", "limit": 10, "format": "json"}).json().get("search", [])
        if h.get("label", "").lower() == args.label.lower()]
    if hits:
        print(f"exists: {hits[0]['id']}  ({args.label})")
        return

    # login + csrf
    t = s.get(API, params={"action": "query", "meta": "tokens",
                           "type": "login", "format": "json"}
              ).json()["query"]["tokens"]["logintoken"]
    r = s.post(API, data={"action": "login", "lgname": env["WIKIBASE_BOT_USER"],
                          "lgpassword": env["WIKIBASE_BOT_PASSWORD"],
                          "lgtoken": t, "format": "json"}).json()
    if r["login"]["result"] != "Success":
        raise SystemExit(f"login failed: {r['login']['result']}")
    token = s.get(API, params={"action": "query", "meta": "tokens",
                               "format": "json"}).json()["query"]["tokens"]["csrftoken"]

    data = {"labels": {"en": {"language": "en", "value": args.label}},
            "datatype": args.datatype}
    if args.desc:
        data["descriptions"] = {"en": {"language": "en", "value": args.desc}}
    r = s.post(API, data={"action": "wbeditentity", "new": "property",
                          "data": json.dumps(data), "token": token,
                          "format": "json"}).json()
    if "error" in r:
        raise SystemExit(f"create failed: {r['error']}")
    print(f"created: {r['entity']['id']}  ({args.label}, {args.datatype})")


if __name__ == "__main__":
    main()
