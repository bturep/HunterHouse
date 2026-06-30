#!/usr/bin/env python3
"""
Post-swap fixups for the 0020↔0022 swap + Scheme I/II split.

After scripts/renumber_caa_25_32.py runs the slot swap with the
mapping_caa_swap_20_22.tsv mapping, this script tidies up the
phase/title/P86 state so the new groupings are consistent:

  1. Rename Q263 label
       "Hunter House - Phase II, Scheme II" (duplicate of Q262)
     → "Hunter House - Phase II, Scheme I"
     Q263 was the duplicate-label artifact; this re-purposes it
     for the new Scheme I phase.

  2. Clear the P84=Q262 claim on the new 0020 (Q338) so it only
     has P62=Q263 as its single phase claim — consistent with how
     every other CAA item uses a single phase property.

  3. Fix titles on 0021/0023/0024:
       "Hunter House - Phase II, Scheme I"
     → "Hunter House - Phase II, Scheme II"
     Brings titles into agreement with their P84=Q262 phase.

  4. Recompute P86 to match the new groupings:
       0020 (Scheme I, lone item)            → "1 of 1"
       0021, 0022 (=old 0020), 0023, 0024    → "1 of 4" ... "4 of 4"
     Slot-ID order within each set (same convention as elsewhere).

Modes: --dry-run | --execute
"""

import argparse, json, os, time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API = "https://hunterhouse.wikibase.cloud/w/api.php"
ENV = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")


def load_env():
    env = {}
    for ln in open(ENV):
        ln = ln.strip()
        if ln and not ln.startswith("#") and "=" in ln:
            k, _, v = ln.partition("=")
            env[k.strip()] = v.strip()
    return env


def make_session():
    s = requests.Session()
    s.mount("https://", HTTPAdapter(max_retries=Retry(
        total=5, backoff_factor=1.5,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST"])))
    s.headers.update({"User-Agent": "HunterHouseBot/1.0"})
    return s


def login(s, env):
    lt = s.get(API, params={"action":"query","meta":"tokens",
                            "type":"login","format":"json"}
              ).json()["query"]["tokens"]["logintoken"]
    r = s.post(API, data={"action":"login","lgname":env["WIKIBASE_BOT_USER"],
                          "lgpassword":env["WIKIBASE_BOT_PASSWORD"],
                          "lgtoken":lt,"format":"json"}).json()
    if r["login"]["result"] != "Success":
        raise SystemExit(f"login failed: {r['login']}")
    print(f"  logged in as {r['login']['lgusername']}")


def csrf(s):
    return s.get(API, params={"action":"query","meta":"tokens",
                              "format":"json"}
                ).json()["query"]["tokens"]["csrftoken"]


def get_claims(s, qid, prop):
    return s.get(API, params={"action":"wbgetclaims","entity":qid,
                              "property":prop,"format":"json"}
                ).json().get("claims",{}).get(prop, [])


# ── operations ───────────────────────────────────────────────────────────

def op_set_label(s, token, qid, new_label, dry):
    r = s.get(API, params={"action":"wbgetentities","ids":qid,"props":"labels",
                           "languages":"en","format":"json"}).json()
    cur = r["entities"][qid]["labels"]["en"]["value"] if "en" in r["entities"][qid]["labels"] else ""
    print(f"  {qid}  label: {cur!r}  →  {new_label!r}")
    if cur == new_label:
        print(f"    (already correct, skipping)")
        return
    if dry:
        print(f"    [DRY] wbsetlabel")
        return
    r = s.post(API, data={"action":"wbsetlabel","id":qid,"language":"en",
                          "value":new_label,"token":token,"format":"json"}).json()
    if "error" in r:
        print(f"    ERROR: {r['error']}")
    else:
        print(f"    wrote: {r['entity']['labels']['en']['value']!r}")


def op_remove_claim(s, token, qid, prop, target_qid, dry):
    """Remove the P{prop} claim on qid whose value equals target_qid."""
    claims = get_claims(s, qid, prop)
    for c in claims:
        val = c.get("mainsnak",{}).get("datavalue",{}).get("value",{})
        # Wikibase item values are dicts like {"entity-type":"item","numeric-id":262,"id":"Q262"}
        if isinstance(val, dict) and val.get("id") == target_qid:
            cid = c["id"]
            print(f"  {qid}  remove {prop} → {target_qid}  ({cid})")
            if dry:
                print(f"    [DRY] wbremoveclaims")
                return
            r = s.post(API, data={"action":"wbremoveclaims","claim":cid,
                                  "token":token,"format":"json"}).json()
            if "error" in r:
                print(f"    ERROR: {r['error']}")
            else:
                print(f"    removed")
            return
    print(f"  {qid}  no {prop}={target_qid} claim found, skipping")


def op_set_string(s, token, qid, prop, value, dry):
    claims = get_claims(s, qid, prop)
    if claims:
        cid = claims[0]["id"]
        cur = claims[0].get("mainsnak",{}).get("datavalue",{}).get("value")
        print(f"  {qid}  {prop}: {cur!r}  →  {value!r}")
        if cur == value:
            print(f"    (already correct, skipping)")
            return
        if dry:
            print(f"    [DRY] wbsetclaimvalue")
            return
        r = s.post(API, data={"action":"wbsetclaimvalue","claim":cid,
                              "snaktype":"value","value":json.dumps(value),
                              "token":token,"format":"json"}).json()
        if "error" in r:
            print(f"    ERROR: {r['error']}")
        else:
            print(f"    wrote")
    else:
        print(f"  {qid}  {prop} (no existing claim): create  → {value!r}")
        if dry:
            print(f"    [DRY] wbcreateclaim")
            return
        r = s.post(API, data={"action":"wbcreateclaim","entity":qid,
                              "snaktype":"value","property":prop,
                              "value":json.dumps(value),"token":token,
                              "format":"json"}).json()
        if "error" in r:
            print(f"    ERROR: {r['error']}")
        else:
            print(f"    created")


def main():
    p = argparse.ArgumentParser()
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--execute", action="store_true")
    args = p.parse_args()
    dry = args.dry_run

    if not dry:
        if input("ABOUT TO MUTATE WIKIBASE. Type YES: ").strip() != "YES":
            raise SystemExit("Aborted.")

    env = load_env()
    s = make_session()
    print("login")
    login(s, env)
    token = csrf(s)

    # 1. Rename Q263 label.
    print("\n[1] Rename Q263 → 'Hunter House - Phase II, Scheme I'")
    op_set_label(s, token, "Q263", "Hunter House - Phase II, Scheme I", dry)

    # 2. Clear P84=Q262 on the new 0020 (Q338) so it has only P62=Q263.
    print("\n[2] Clear P84=Q262 on Q338 (the new 0020)")
    op_remove_claim(s, token, "Q338", "P84", "Q262", dry)

    # 3. Fix titles on 0021, 0023, 0024 → "Phase II, Scheme II".
    print("\n[3] Fix titles on 0021, 0023, 0024 → 'Hunter House - Phase II, Scheme II'")
    new_title = "Hunter House - Phase II, Scheme II"
    for qid in ["Q349", "Q336", "Q353"]:
        op_set_label(s, token, qid, new_title, dry)

    # 4. Recompute P86 within the new Scheme I (just Q338) and Scheme II.
    #    Scheme I: slot 0020 = Q338 → "1 of 1"
    #    Scheme II: 0021=Q349, 0022=Q335, 0023=Q336, 0024=Q353 → 1..4 of 4
    print("\n[4] Recompute P86 (set position)")
    p86_updates = [
        ("Q338", "1 of 1"),  # slot 0020 (Scheme I)
        ("Q349", "1 of 4"),  # slot 0021 (Scheme II, 1986)
        ("Q335", "2 of 4"),  # slot 0022 (Scheme II, 1981) — was old 0020
        ("Q336", "3 of 4"),  # slot 0023 (Scheme II, 1986)
        ("Q353", "4 of 4"),  # slot 0024 (Scheme II, 1986)
    ]
    for qid, val in p86_updates:
        op_set_string(s, token, qid, "P86", val, dry)
        if not dry: time.sleep(0.3)

    print(f"\n{'DRY RUN complete' if dry else 'Done.'}")


if __name__ == "__main__":
    main()
