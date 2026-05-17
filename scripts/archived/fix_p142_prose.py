#!/usr/bin/env python3
"""
Audit and fix P142 values that contain prose text mixed into the
archival path. The migration script only split on '. Note'; items with
'. Ref:' or other prose markers were stored verbatim.

For each CAA item, checks whether P142 contains a period followed by a
capital letter / 'c.' (prose signal). Splits at that boundary:
  - P142 ← path codes only (e.g. "S0004, SS0001, SSS0018, folder-19")
  - P100 ← prose remainder (e.g. "Ref: folder-19_03. c. 1985, pre-1990")

Run with --dry-run first to preview changes.
"""

import urllib.request, urllib.parse, json, http.cookiejar, sys, re, time

API   = "https://hunterhouse.wikibase.cloud/w/api.php"
SPARQL = "https://hunterhouse.wikibase.cloud/query/sparql"
DRY_RUN = "--dry-run" in sys.argv

with open("/Users/brandonpoole/Documents/hh-wikibase-migration/.env") as f:
    env = dict(line.strip().split("=", 1) for line in f if "=" in line and not line.startswith("#"))

USER     = "MyBot@my-bot"
PASSWORD = env["WIKIBASE_BOT_PASSWORD"]

jar    = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))

def api(params, method="GET"):
    params["format"] = "json"
    if method == "POST":
        data = urllib.parse.urlencode(params).encode()
        req  = urllib.request.Request(API, data=data)
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

# Detect prose mixed into a path string.
# Valid path tokens: S####, SS####, SSS####, FL####, folder-##  (codes only)
# A prose signal: period followed by space + capital letter, "c.", "Ref", etc.
PROSE_RE = re.compile(r'\.\s*(?=[A-Z]|c\.|[Rr]ef)')

def split_path_prose(location):
    """Return (path, prose). prose is '' if no split needed."""
    m = PROSE_RE.search(location)
    if not m:
        return location, ""
    path  = location[:m.start()].strip()
    prose = location[m.start()+1:].strip()  # drop the period
    return path, prose

# Login
lt = api({"action": "query", "meta": "tokens", "type": "login"})["query"]["tokens"]["logintoken"]
r  = api({"action": "login", "lgname": USER, "lgpassword": PASSWORD, "lgtoken": lt}, "POST")
print("Login:", r["login"]["result"])

csrf = api({"action": "query", "meta": "tokens"})["query"]["tokens"]["csrftoken"]

rows = sparql("""
PREFIX wdt: <https://hunterhouse.wikibase.cloud/prop/direct/>
SELECT ?item ?qid ?id ?location WHERE {
  ?item wdt:P2 ?id .
  ?item wdt:P142 ?location .
  FILTER(STRSTARTS(?id, "HH-CAA"))
  BIND(STRAFTER(STR(?item), "/entity/") AS ?qid)
} ORDER BY ?id
""")

print(f"\nFound {len(rows)} CAA items with P142")
if DRY_RUN:
    print("DRY RUN — no writes\n")

problems = [(r["qid"]["value"], r["id"]["value"], r["location"]["value"])
            for r in rows if PROSE_RE.search(r["location"]["value"])]

if not problems:
    print("No malformed P142 values found — all clean.")
    sys.exit(0)

print(f"{len(problems)} item(s) with prose mixed into P142:\n")

ok = err = 0
for qid, iid, location in problems:
    path, prose = split_path_prose(location)
    print(f"  {iid} ({qid})")
    print(f"    P142 (current): \"{location}\"")
    print(f"    P142 → \"{path}\"")
    print(f"    P100 → \"{prose}\"")

    if DRY_RUN:
        continue

    try:
        # Update P142 to path only
        entity = api({"action": "wbgetentities", "ids": qid, "props": "claims"})
        claims_142 = entity["entities"][qid]["claims"].get("P142", [])
        claims_100 = entity["entities"][qid]["claims"].get("P100", [])

        if claims_142:
            guid = claims_142[0]["id"]
            api({"action": "wbsetclaimvalue", "claim": guid, "snaktype": "value",
                 "value": json.dumps(path), "token": csrf}, "POST")

        # Set P100 to prose (add or update)
        if prose:
            if claims_100:
                guid100 = claims_100[0]["id"]
                api({"action": "wbsetclaimvalue", "claim": guid100, "snaktype": "value",
                     "value": json.dumps(prose), "token": csrf}, "POST")
            else:
                api({"action": "wbcreateclaim", "entity": qid, "snaktype": "value",
                     "property": "P100", "value": json.dumps(prose), "token": csrf}, "POST")

        ok += 1
        time.sleep(0.5)
    except Exception as e:
        print(f"    ERROR: {e}")
        err += 1

if not DRY_RUN:
    print(f"\nDone. OK: {ok}  Errors: {err}")
