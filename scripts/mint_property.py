#!/usr/bin/env python3
"""
Mint (or find) a single Wikibase property. Idempotent: if a property with the
exact label already exists it is reused, not duplicated.

Uses scripts/_wikibase.py for env loading + login + CSRF (migrated
2026-05-22 as part of ARCHITECTURE.md §11.2 LOW dedup pass). Credentials
load from ~/Documents/hh-wikibase-migration/.env.

Usage:
  python3 scripts/mint_property.py --label "display rotation" \
      --desc "…" --datatype string
"""

import argparse
import json

from _wikibase import WikibaseSession


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True)
    ap.add_argument("--desc", default="")
    ap.add_argument("--datatype", default="string",
                    help="string | url | wikibase-item | time | quantity | external-id …")
    args = ap.parse_args()

    # idempotency check first — read-only, no need to log in yet, so build the
    # session lazily (login_now=False keeps the boot fast on a find-and-skip).
    wb = WikibaseSession(user_agent="HunterHouseBot/1.0 (mint_property)",
                         login_now=False)
    hits = [h for h in wb.get("wbsearchentities",
                              search=args.label, language="en",
                              type="property", limit=10
                              ).get("search", [])
            if h.get("label", "").lower() == args.label.lower()]
    if hits:
        print(f"exists: {hits[0]['id']}  ({args.label})")
        return

    # New property: now we actually need credentials.
    wb.login()
    data = {"labels": {"en": {"language": "en", "value": args.label}},
            "datatype": args.datatype}
    if args.desc:
        data["descriptions"] = {"en": {"language": "en", "value": args.desc}}
    r = wb.post("wbeditentity", new="property", data=json.dumps(data))
    if "error" in r:
        raise SystemExit(f"create failed: {r['error']}")
    print(f"created: {r['entity']['id']}  ({args.label}, {args.datatype})")


if __name__ == "__main__":
    main()
