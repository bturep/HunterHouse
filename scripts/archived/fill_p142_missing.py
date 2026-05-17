#!/usr/bin/env python3
"""
Write P142 (Physical location) for the 15 CAA items that had none.

Drawing items: full FL path confirmed from fonds hierarchy + AtoM links.
Photographs: path stops at SSS0001 (sub-subseries) — FL not determinable
without physical access to the boxes.

Run with --dry-run first.
"""

import urllib.request, urllib.parse, json, http.cookiejar, sys, time

API    = "https://hunterhouse.wikibase.cloud/w/api.php"
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
        req  = urllib.request.Request(API + "?" + urllib.parse.urlencode(params))
    req.add_header("User-Agent", "HHBot/1.0")
    with opener.open(req) as r:
        return json.loads(r.read())

# QIDs from SPARQL query
ITEMS = [
    # Cottage for Ric and Frances Hunter (FL0005, Folder 18)
    ("Q357", "HH-CAA-0007", "S0004, SS0001, SSS0018, FL0005"),
    ("Q356", "HH-CAA-0008", "S0004, SS0001, SSS0018, FL0005"),
    ("Q347", "HH-CAA-0009", "S0004, SS0001, SSS0018, FL0005"),

    # Photographs — stop at SSS0001, FL not determinable without box access
    ("Q345", "HH-CAA-0010", "S0004, SS0003, SSS0001"),
    ("Q330", "HH-CAA-0011", "S0004, SS0003, SSS0001"),
    ("Q337", "HH-CAA-0012", "S0004, SS0003, SSS0001"),
    ("Q350", "HH-CAA-0013", "S0004, SS0003, SSS0001"),
    ("Q344", "HH-CAA-0014", "S0004, SS0003, SSS0001"),
    ("Q346", "HH-CAA-0015", "S0004, SS0003, SSS0001"),
    ("Q332", "HH-CAA-0016", "S0004, SS0003, SSS0001"),
    ("Q354", "HH-CAA-0017", "S0004, SS0003, SSS0001"),
    ("Q358", "HH-CAA-0018", "S0004, SS0003, SSS0001"),
    ("Q355", "HH-CAA-0019", "S0004, SS0003, SSS0001"),

    # Hunter House - Scheme II (FL0006, Folder 19)
    ("Q352", "HH-CAA-0026", "S0004, SS0001, SSS0018, FL0006"),

    # Hunter House Addition - Scheme I (FL0007, Folder 20)
    ("Q334", "HH-CAA-0028", "S0004, SS0001, SSS0018, FL0007"),
]

# Login
lt = api({"action": "query", "meta": "tokens", "type": "login"})["query"]["tokens"]["logintoken"]
r  = api({"action": "login", "lgname": USER, "lgpassword": PASSWORD, "lgtoken": lt}, "POST")
print("Login:", r["login"]["result"])

csrf = api({"action": "query", "meta": "tokens"})["query"]["tokens"]["csrftoken"]

print(f"\n{len(ITEMS)} items to write{'  (DRY RUN)' if DRY_RUN else ''}\n")

ok = err = 0
for qid, iid, location in ITEMS:
    print(f"  {iid} ({qid})  ←  \"{location}\"")
    if DRY_RUN:
        continue
    try:
        api({"action": "wbcreateclaim", "entity": qid, "snaktype": "value",
             "property": "P142", "value": json.dumps(location), "token": csrf}, "POST")
        ok += 1
        time.sleep(0.4)
    except Exception as e:
        print(f"    ERROR: {e}")
        err += 1

if not DRY_RUN:
    print(f"\nDone. OK: {ok}  Errors: {err}")
