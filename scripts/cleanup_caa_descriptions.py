#!/usr/bin/env python3
"""
CAA description cleanup.

For each CAA item:
  - Writes P91 (medium) where known from original P100 text
  - Updates P100 to cleaned version: fonds hierarchy path + unique notes only.
    Removes info already held in other properties (source institution, date, set position).

Items skipped:
  CAA-0007/0008/0009  — P100 is "OG Scheme", a unique curatorial note, left unchanged
  CAA-0010–0019       — photographs, no P100
  CAA-0028            — no P100

Usage:
  python3 scripts/cleanup_caa_descriptions.py --dry-run
  python3 scripts/cleanup_caa_descriptions.py
"""

import json, os, time, argparse
import requests

API     = "https://hunterhouse.wikibase.cloud/w/api.php"
SPARQL  = "https://hunterhouse.wikibase.cloud/query/sparql"
ENV     = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")

FONDS   = "Richard Hunter fonds (2019.61)"

# P91 medium values keyed by archive ID
MEDIUM = {
    "HH-CAA-0001": "Pencil on tracing paper",
    "HH-CAA-0002": "Pencil on tracing paper",
    "HH-CAA-0003": "Pencil on vellum",
    "HH-CAA-0004": "Pencil on vellum",
    "HH-CAA-0005": "Pencil on vellum",
    "HH-CAA-0006": "Pencil on vellum",
    "HH-CAA-0020": "Pencil on vellum",
    "HH-CAA-0021": "Pencil on vellum",
    "HH-CAA-0022": "Pencil on vellum",
    "HH-CAA-0023": "Pencil on vellum",
    "HH-CAA-0024": "Pencil on vellum",
    "HH-CAA-0029": "Hand-coloured",
    "HH-CAA-0030": "Hand-coloured",
    "HH-CAA-0031": "Hand-coloured",
    "HH-CAA-0032": "Hand-coloured",
    "HH-CAA-0033": "Hand-coloured",
    "HH-CAA-0034": "Hand-coloured",
    "HH-CAA-0035": "Hand-coloured",
}

# Clean P100 values keyed by archive ID.
# None = skip (no P100 to update). Entries in SKIP_P100 keep their existing value.
SKIP_P100 = {"HH-CAA-0007", "HH-CAA-0008", "HH-CAA-0009"}  # "OG Scheme" — keep

CLEAN_P100 = {
    "HH-CAA-0001": f"{FONDS} — S0004, SS0001, SSS0018, FL0003.",
    "HH-CAA-0002": f"{FONDS} — S0004, SS0001, SSS0018, FL0003.",
    "HH-CAA-0003": (
        f"{FONDS} — S0004, SS0001, SSS0018, FL0004. "
        "Note on drawing: 'Kitchen entirely on rock outcropping. "
        "Skywalk/Veranda inception as Eyrie. Program generally prescribed.'"
    ),
    "HH-CAA-0004": f"{FONDS} — S0004, SS0001, SSS0018, FL0004.",
    "HH-CAA-0005": f"{FONDS} — S0004, SS0001, SSS0018, FL0004.",
    "HH-CAA-0006": f"{FONDS} — S0004, SS0001, SSS0018, FL0004.",
    "HH-CAA-0020": f"{FONDS} — S0004, SS0001, SSS0018, FL0002.",
    "HH-CAA-0021": f"{FONDS} — S0004, SS0001, SSS0018, FL0002.",
    "HH-CAA-0022": f"{FONDS} — S0004, SS0001, SSS0018, FL0002.",
    "HH-CAA-0023": (
        f"{FONDS} — S0004, SS0001, SSS0018, FL0002. "
        "Note: 1981 (with [1988?] notation on drawing)."
    ),
    "HH-CAA-0024": f"{FONDS} — S0004, SS0001, SSS0018, FL0002.",
    "HH-CAA-0025": (
        f"{FONDS} — S0004, SS0001, SSS0018, folder-19. "
        "Ref: folder-19_01. c. 1985, pre-1990."
    ),
    "HH-CAA-0026": "c. 1985, pre-1990.",
    "HH-CAA-0027": (
        f"{FONDS} — S0004, SS0001, SSS0018, folder-19. "
        "Ref: folder-19_03. c. 1985, pre-1990."
    ),
    "HH-CAA-0029": f"{FONDS} — S0004, SS0001, SSS0018, FL0001.",
    "HH-CAA-0030": f"{FONDS} — S0004, SS0001, SSS0018, FL0001.",
    "HH-CAA-0031": f"{FONDS} — S0004, SS0001, SSS0018, FL0001.",
    "HH-CAA-0032": f"{FONDS} — S0004, SS0001, SSS0018, FL0001.",
    "HH-CAA-0033": f"{FONDS} — S0004, SS0001, SSS0018, FL0001.",
    "HH-CAA-0034": f"{FONDS} — S0004, SS0001, SSS0018, FL0001.",
    "HH-CAA-0035": f"{FONDS} — S0004, SS0001, SSS0018, FL0001.",
}


def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    return env


def get_caa_items(s):
    """Return list of (qid, archive_id) for all HH-CAA items via SPARQL."""
    query = """
PREFIX wdt: <https://hunterhouse.wikibase.cloud/prop/direct/>
SELECT ?item ?archId WHERE {
  ?item wdt:P2 ?archId .
  FILTER(STRSTARTS(?archId, "HH-CAA-"))
} ORDER BY ?archId
"""
    r = s.post(SPARQL, data=query,
               headers={"Content-Type": "application/sparql-query",
                        "Accept": "application/sparql-results+json"})
    r.raise_for_status()
    rows = r.json()["results"]["bindings"]
    return [(
        row["item"]["value"].rsplit("/", 1)[-1],
        row["archId"]["value"]
    ) for row in rows]


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


def write_string_claim(s, token, qid, prop, value, dry_run):
    """Create or overwrite a monovalued string claim."""
    claims = get_claims(s, qid, prop)
    if claims:
        claim_id = claims[0]["id"]
        if dry_run:
            print(f"      [DRY] SET {prop} = {value!r}")
            return True
        r = s.post(API, data={
            "action": "wbsetclaimvalue", "claim": claim_id,
            "snaktype": "value", "value": json.dumps(value),
            "token": token, "format": "json",
        })
        return "error" not in r.json()
    else:
        if dry_run:
            print(f"      [DRY] CREATE {prop} = {value!r}")
            return True
        r = s.post(API, data={
            "action": "wbcreateclaim", "entity": qid,
            "snaktype": "value", "property": prop,
            "value": json.dumps(value),
            "token": token, "format": "json",
        })
        return "error" not in r.json()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                        help="Print changes without writing to Wikibase")
    args = parser.parse_args()

    env = load_env(ENV)

    s = requests.Session()
    s.headers.update({"User-Agent": "HunterHouseBot/1.0"})

    print("Querying CAA items from Wikibase…")
    items = get_caa_items(s)
    print(f"Found {len(items)} CAA items.\n")

    login(s, env["WIKIBASE_BOT_USER"], env["WIKIBASE_BOT_PASSWORD"])
    token = csrf(s)

    prefix = "DRY RUN — " if args.dry_run else ""
    print(f"{prefix}Processing {len(items)} CAA items.\n")

    for qid, aid in items:
        medium     = MEDIUM.get(aid)
        new_p100   = CLEAN_P100.get(aid)
        skip_p100  = aid in SKIP_P100

        if medium is None and new_p100 is None and not skip_p100:
            print(f"  {aid} ({qid})  — no changes needed, skipping")
            continue

        print(f"  {aid} ({qid})")

        if medium:
            ok = write_string_claim(s, token, qid, "P91", medium, args.dry_run)
            status = "ok" if ok else "FAIL"
            print(f"    P91 medium: {status} → {medium!r}")

        if new_p100:
            ok = write_string_claim(s, token, qid, "P100", new_p100, args.dry_run)
            status = "ok" if ok else "FAIL"
            print(f"    P100 notes: {status} → {new_p100[:60]}…")
        elif skip_p100:
            print(f"    P100 notes: unchanged (OG Scheme — preserved)")

        if not args.dry_run:
            time.sleep(0.3)

    print(f"\n{'DRY RUN complete.' if args.dry_run else 'Done.'}")


if __name__ == "__main__":
    main()
