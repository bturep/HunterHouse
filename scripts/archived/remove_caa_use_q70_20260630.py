#!/usr/bin/env python3
"""
Remove the misapplied P89 (use) → Q70 (design development) claim from CAA
drawings.

Background. An early ingest pass on the CAA drawings (HH-CAA-0002 …
HH-CAA-0025) wrote P89 = Q70. Q70 is a project-phase value ("design
development"), not a use value — wrong property + wrong meaning. Brandon
asked to drop all of them.

Behaviour:
  • Dry-run by default. --execute to actually write.
  • SPARQL-fetches every CAA item that currently carries P89 → Q70.
  • Per item, fetches the entity's P89 statements, finds the one whose
    mainsnak datavalue is Q70, and removes only that statement (any
    OTHER P89 values on the same item are left untouched).
  • wbremoveclaims by statement ID — atomic and safe.

Exit codes: 0 on clean run, 1 if any per-item failure occurred.
"""
import argparse
import json
import sys
import time
from urllib.parse import quote

import requests

# Allow running from anywhere — add scripts/ to sys.path for the shared helper.
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wikibase import WikibaseSession   # noqa: E402

SPARQL_ENDPOINT = "https://hunterhouse.wikibase.cloud/query/sparql"
QID_TARGET      = "Q70"
PID_USE         = "P89"
PID_ARCHID      = "P2"
CAA_PREFIX      = "HH-CAA-"


def fetch_affected():
    """Return list of (qid, archId) for every CAA item with P89 → Q70."""
    query = (
        'PREFIX wd:  <https://hunterhouse.wikibase.cloud/entity/>\n'
        'PREFIX wdt: <https://hunterhouse.wikibase.cloud/prop/direct/>\n'
        f'SELECT ?item ?archId WHERE {{\n'
        f'  ?item wdt:{PID_USE} wd:{QID_TARGET} ;\n'
        f'        wdt:{PID_ARCHID} ?archId .\n'
        f'  FILTER(STRSTARTS(?archId, "{CAA_PREFIX}"))\n'
        f'}} ORDER BY ?archId'
    )
    r = requests.post(
        SPARQL_ENDPOINT, data=query,
        headers={"Content-Type": "application/sparql-query",
                 "Accept": "application/sparql-results+json"},
        timeout=30,
    )
    r.raise_for_status()
    out = []
    for b in r.json()["results"]["bindings"]:
        qid = b["item"]["value"].rsplit("/", 1)[1]
        out.append((qid, b["archId"]["value"]))
    return out


def find_p89_q70_statement(wb, qid):
    """Return the statement ID for P89 → Q70 on `qid`, or None."""
    res = wb.get("wbgetentities", ids=qid, props="claims")
    claims = res["entities"][qid].get("claims", {}).get(PID_USE, [])
    for c in claims:
        ms = c.get("mainsnak", {})
        if ms.get("snaktype") != "value":
            continue
        dv = ms.get("datavalue", {}).get("value", {})
        if dv.get("id") == QID_TARGET:
            return c["id"]
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--execute", action="store_true",
                    help="Actually remove the claims (default is dry-run).")
    args = ap.parse_args()

    items = fetch_affected()
    print(f"SPARQL → {len(items)} CAA items with P89 → Q70")
    if not items:
        print("Nothing to do.")
        return 0

    for qid, archid in items:
        print(f"  {archid}  {qid}")

    if not args.execute:
        print("\nDry-run. Re-run with --execute to remove.")
        return 0

    wb = WikibaseSession(user_agent="HunterHouseBot/1.0 (remove_caa_use_q70)")
    print()
    fails = 0
    for qid, archid in items:
        stmt = find_p89_q70_statement(wb, qid)
        if not stmt:
            print(f"  {archid}  {qid}  — no matching P89→Q70 (skip)")
            continue
        res = wb.post("wbremoveclaims", claim=stmt)
        if "error" in res:
            print(f"  {archid}  {qid}  FAIL {res['error']}")
            fails += 1
        else:
            print(f"  {archid}  {qid}  ✓ removed {stmt}")
        time.sleep(0.25)   # gentle pacing
    print()
    print(f"Done — {len(items) - fails} ok, {fails} failed")
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
