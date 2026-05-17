#!/usr/bin/env python3
"""
Migrate archival path from P100 into P142 (Physical location) for CAA items.

P100 format:  "Fonds ref — S0004, SS0001, SSS0018, FL0003. [Optional prose note.]"

After migration:
  P142 = "S0004, SS0001, SSS0018, FL0003"   (path, trimmed)
  P100 = "Optional prose note."              (cleared if no prose)

Run with --dry-run first.
"""

import urllib.request, urllib.parse, json, http.cookiejar, sys, re, time

API = "https://hunterhouse.wikibase.cloud/w/api.php"
SPARQL = "https://hunterhouse.wikibase.cloud/query/sparql"
DRY_RUN = "--dry-run" in sys.argv

with open("/Users/brandonpoole/Documents/hh-wikibase-migration/.env") as f:
    env = dict(line.strip().split("=", 1) for line in f if "=" in line and not line.startswith("#"))

USER = "MyBot@my-bot"
PASSWORD = env["WIKIBASE_BOT_PASSWORD"]

jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

def api(params, method="GET"):
    params["format"] = "json"
    if method == "POST":
        data = urllib.parse.urlencode(params).encode()
        req = urllib.request.Request(API, data=data)
    else:
        req = urllib.request.Request(API + "?" + urllib.parse.urlencode(params))
    req.add_header("User-Agent", "HHBot/1.0")
    with opener.open(req) as r:
        return json.loads(r.read())

def sparql(q):
    req = urllib.request.Request(SPARQL, data=q.encode(), headers={
        "Content-Type": "application/sparql-query",
        "Accept": "application/sparql-results+json",
        "User-Agent": "HHBot/1.0"
    })
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["results"]["bindings"]

def parse_p100(notes):
    """Return (path, prose) split on ' — '. prose may be empty string."""
    sep = notes.find(" — ")
    if sep == -1:
        return None, notes  # no path, pure prose
    fonds_ref = notes[:sep]  # e.g. "Richard Hunter fonds (2019.61)" — not migrated
    remainder = notes[sep + 3:].strip()
    # remainder: "S0004, SS0001, SSS0018, FL0004. Note: '...'"
    # Split on ". Note" or ". note"
    note_match = re.search(r'\.\s*(Note\b)', remainder)
    if note_match:
        path = remainder[:note_match.start()].strip()
        prose = remainder[note_match.start()+1:].strip()  # keep "Note: ..."
    else:
        # No prose — just strip trailing period
        path = remainder.rstrip(". ")
        prose = ""
    return path, prose

# Login
lt = api({"action": "query", "meta": "tokens", "type": "login"})["query"]["tokens"]["logintoken"]
r = api({"action": "login", "lgname": USER, "lgpassword": PASSWORD, "lgtoken": lt}, "POST")
print("Login:", r["login"]["result"])

csrf = api({"action": "query", "meta": "tokens"})["query"]["tokens"]["csrftoken"]

# Fetch all CAA items with P100
rows = sparql("""
PREFIX wdt: <https://hunterhouse.wikibase.cloud/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?item ?qid ?id ?notes WHERE {
  ?item wdt:P2 ?id .
  ?item wdt:P100 ?notes .
  FILTER(STRSTARTS(?id, "HH-CAA"))
  BIND(STRAFTER(STR(?item), "/entity/") AS ?qid)
} ORDER BY ?id
""")

print(f"\nFound {len(rows)} CAA items with P100")
if DRY_RUN:
    print("DRY RUN — no writes\n")

ok = err = 0
for row in rows:
    qid   = row["qid"]["value"]
    iid   = row["id"]["value"]
    notes = row["notes"]["value"]

    path, prose = parse_p100(notes)

    if path is None:
        print(f"  {iid} ({qid}): pure prose, skipping path migration")
        continue

    print(f"\n  {iid} ({qid})")
    print(f"    P142 ← \"{path}\"")
    print(f"    P100 ← \"{prose}\" {'(clear)' if not prose else ''}")

    if DRY_RUN:
        continue

    try:
        # Write P142
        api({"action": "wbcreateclaim", "entity": qid, "snaktype": "value",
             "property": "P142", "value": json.dumps(path), "token": csrf}, "POST")

        # Update P100: clear or set to prose only
        if prose:
            # Get P100 statement GUID to update it
            entity = api({"action": "wbgetentities", "ids": qid, "props": "claims"})
            claims = entity["entities"][qid]["claims"].get("P100", [])
            if claims:
                guid = claims[0]["id"]
                api({"action": "wbsetclaimvalue", "claim": guid, "snaktype": "value",
                     "value": json.dumps(prose), "token": csrf}, "POST")
        else:
            # Remove P100 entirely
            entity = api({"action": "wbgetentities", "ids": qid, "props": "claims"})
            claims = entity["entities"][qid]["claims"].get("P100", [])
            if claims:
                guid = claims[0]["id"]
                api({"action": "wbremoveclaims", "claim": guid, "token": csrf}, "POST")

        ok += 1
        time.sleep(0.5)
    except Exception as e:
        print(f"    ERROR: {e}")
        err += 1

if not DRY_RUN:
    print(f"\nDone. OK: {ok}  Errors: {err}")
