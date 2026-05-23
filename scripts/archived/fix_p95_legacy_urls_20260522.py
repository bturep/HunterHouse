#!/usr/bin/env python3
"""
ARCHIVED 2026-05-22 — ran once, all 6 rewrites succeeded; final
verify_r2_links pass returned 354/354 URLs at 200. One incidental
duplicate was created on Q425 (a pre-existing correct P95 claim was
not visible during the initial SPARQL planning pass due to lag) and
manually deleted in a follow-up. Net effect: every catalogue item now
has exactly one good P95 URL.

(Imports `_wikibase` from the parent scripts/ dir; to resurrect, copy
back to scripts/ or run with PYTHONPATH=scripts.)

Fix the 6 dead P95 master-image URLs surfaced by
scripts/verify_r2_links.py on 2026-05-22.

Background: the 2026-05-14 HH-A → HH-HHC rename migration correctly
renamed the master TIFs in R2 but missed updating the P95 (master
image URL) claim on 6 items. The R2 files exist at their new
"HH-HHC-NNNN_…" paths; only the Wikibase claims still point at the
legacy "HH-A-NNNN_…" paths.

Pattern for each affected item:
    new_url = re.sub(r"HH-A-\\d+_", f"{archId}_", old_url)

Safety:
  1. Dry-run by default (no writes; --execute to apply).
  2. Pre-flight HEAD-check on every proposed NEW URL — if any new URL
     also returns non-2xx, the script refuses to write that one (so we
     don't trade one bad URL for another).
  3. Per-item: wbcreateclaim with the new URL first; only then
     wbremoveclaims for the legacy claim (matches the create-then-remove
     pattern already used in browse.html/next.html setStringClaim). If
     create fails the legacy claim survives untouched.

Use after execute:
    python3 scripts/verify_r2_links.py --pid P95
to confirm every P95 URL now returns 200.
"""

import argparse
import json
import re
import sys

try:
    import requests
except ImportError:
    sys.exit("Missing 'requests'.  pip3 install requests")

from _wikibase import WikibaseSession


WIKIBASE = "https://hunterhouse.wikibase.cloud"
SPARQL   = f"{WIKIBASE}/query/sparql"
P95      = "P95"  # master image URL

# Items surfaced by verify_r2_links on 2026-05-22 — hardcoded rather than
# re-discovered so the change is explicit and reviewable.
AFFECTED = [
    "HH-HHC-0036",
    "HH-HHC-0037",
    "HH-HHC-0038",
    "HH-HHC-0039",
    "HH-HHC-0040",
    "HH-HHC-0066",
]

LEGACY_RE = re.compile(r"HH-A-\d+_")
USER_AGENT = "HunterHouseBot/1.0 (fix_p95_legacy_urls)"


def sparql_p95_for(arch_id):
    """Return (qid, old_url) for the item with this archId, or None."""
    q = f"""
PREFIX wdt: <https://hunterhouse.wikibase.cloud/prop/direct/>
SELECT ?item ?url WHERE {{
  ?item wdt:P2 "{arch_id}" .
  ?item wdt:P95 ?url .
}}
"""
    r = requests.get(SPARQL, params={"query": q, "format": "json"},
                     headers={"Accept": "application/sparql-results+json",
                              "User-Agent": USER_AGENT}, timeout=30)
    r.raise_for_status()
    rows = r.json()["results"]["bindings"]
    if not rows:
        return None
    qid = rows[0]["item"]["value"].rsplit("/", 1)[-1]
    return (qid, rows[0]["url"]["value"])


def head_ok(url):
    """True iff HEAD returns 2xx."""
    try:
        r = requests.head(url, allow_redirects=True, timeout=10,
                          headers={"User-Agent": USER_AGENT})
        return r.status_code < 400, r.status_code
    except requests.exceptions.RequestException as e:
        return False, type(e).__name__


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--execute", action="store_true",
                    help="actually write to Wikibase (default: dry-run)")
    args = ap.parse_args()

    # ── Plan phase: gather + verify NEW URLs reachable on R2 ──
    print(f"→ planning rewrites for {len(AFFECTED)} items …")
    plans = []  # list of dicts {arch_id, qid, old_url, new_url, new_url_status}
    for arch_id in AFFECTED:
        got = sparql_p95_for(arch_id)
        if not got:
            print(f"  ⚠ {arch_id}: no item or no P95 claim found — skipping")
            continue
        qid, old_url = got
        new_url = LEGACY_RE.sub(f"{arch_id}_", old_url)
        if new_url == old_url:
            print(f"  ⚠ {arch_id}: URL already matches archId — already fixed?")
            continue
        ok, status = head_ok(new_url)
        plans.append({
            "arch_id": arch_id, "qid": qid, "old_url": old_url,
            "new_url": new_url, "new_url_ok": ok, "new_url_status": status,
        })

    # ── Print plan ──
    print()
    print("Planned rewrites:")
    print("─" * 80)
    safe = []
    for p in plans:
        mark = "✓" if p["new_url_ok"] else "✗"
        print(f"  {mark} {p['arch_id']} ({p['qid']})  [new URL HEAD → {p['new_url_status']}]")
        print(f"      old: {p['old_url']}")
        print(f"      new: {p['new_url']}")
        if p["new_url_ok"]:
            safe.append(p)
    print("─" * 80)
    print(f"{len(safe)} of {len(plans)} rewrites are safe to apply "
          f"(new URL returns 2xx).")

    if not args.execute:
        print(f"\nDry run. Re-run with --execute to apply {len(safe)} rewrite(s).")
        return

    if len(safe) < len(plans):
        unsafe = [p for p in plans if not p["new_url_ok"]]
        print(f"\n⚠ {len(unsafe)} item(s) would have an unreachable new URL — refusing "
              f"to write those:")
        for p in unsafe:
            print(f"    - {p['arch_id']} (status {p['new_url_status']})")
        print(f"  Proceeding with the {len(safe)} safe rewrite(s) only.")

    # ── Execute phase: create-then-remove per item ──
    print()
    wb = WikibaseSession(user_agent=USER_AGENT)
    ok_count = 0
    fail_count = 0
    for p in safe:
        arch_id, qid, old_url, new_url = p["arch_id"], p["qid"], p["old_url"], p["new_url"]
        print(f"→ {arch_id} ({qid}):")

        # Look up the live entity to get the legacy claim's UUID.
        ent = wb.get("wbgetentities", ids=qid)["entities"][qid]
        old_claim_ids = [
            st["id"]
            for st in (ent.get("claims") or {}).get(P95, [])
            if st.get("mainsnak", {}).get("datavalue", {}).get("value") == old_url
        ]
        if not old_claim_ids:
            print(f"  ⚠ no matching P95 claim with the legacy URL — skipping")
            continue

        # Create new P95 first.
        res = wb.post("wbcreateclaim", entity=qid, snaktype="value",
                      property=P95, value=json.dumps(new_url))
        if "error" in res:
            print(f"  ✗ create failed: {res['error']}")
            fail_count += 1
            continue
        new_id = res.get("claim", {}).get("id", "?")
        print(f"  ✓ created new P95 → {new_id}")

        # Remove the legacy one(s) — if there happens to be more than one
        # matching the old URL, sweep them all.
        for old_id in old_claim_ids:
            res = wb.post("wbremoveclaims", claim=old_id)
            if "error" in res:
                print(f"  ✗ remove failed for {old_id}: {res['error']}")
                fail_count += 1
            else:
                print(f"  ✓ removed legacy P95 claim {old_id}")
        ok_count += 1

    print()
    print(f"✓ done.  {ok_count} item(s) rewritten, {fail_count} failure(s).")
    print(f"  Verify:  python3 scripts/verify_r2_links.py --pid P95")


if __name__ == "__main__":
    main()
