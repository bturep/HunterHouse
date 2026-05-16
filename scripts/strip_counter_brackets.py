#!/usr/bin/env python3
"""
Strip [N/N] counter brackets from Wikibase item labels.

Removes patterns like [1/3], [2/8], [10/10] from English labels.
Leaves all other bracket content (e.g. [Tilted Form], [Framing Plan]) intact.

Run with --dry-run first to review changes.
"""

import urllib.request, urllib.parse, json, http.cookiejar, sys, re, time

API    = "https://hunterhouse.wikibase.cloud/w/api.php"
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
        req  = urllib.request.Request(API + "?" + urllib.parse.urlencode(params))
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

COUNTER_RE = re.compile(r'\s*\[\d+/\d+\]')

def strip_counters(label):
    return COUNTER_RE.sub("", label).strip()

# Fetch all items with brackets in the label
rows = sparql("""
PREFIX wdt: <https://hunterhouse.wikibase.cloud/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?item ?id ?label WHERE {
  ?item wdt:P2 ?id .
  ?item rdfs:label ?label . FILTER(LANG(?label)="en")
  FILTER(CONTAINS(?label, "["))
} ORDER BY ?id
""")

targets = []
for r in rows:
    label = r["label"]["value"]
    if COUNTER_RE.search(label):
        qid      = r["item"]["value"].split("/").pop()
        new_label = strip_counters(label)
        targets.append((qid, r["id"]["value"], label, new_label))

print(f"{len(targets)} items with [N/N] counters{'  (DRY RUN)' if DRY_RUN else ''}\n")
for qid, iid, old, new in targets:
    print(f"  {iid}  ({qid})")
    print(f"    before: {old}")
    print(f"    after:  {new}")

if DRY_RUN:
    sys.exit(0)

print("\nWriting...")

# Login
lt = api({"action": "query", "meta": "tokens", "type": "login"})["query"]["tokens"]["logintoken"]
r  = api({"action": "login", "lgname": USER, "lgpassword": PASSWORD, "lgtoken": lt}, "POST")
print("Login:", r["login"]["result"])
csrf = api({"action": "query", "meta": "tokens"})["query"]["tokens"]["csrftoken"]

ok = err = 0
for qid, iid, old, new in targets:
    try:
        api({"action": "wbsetlabel", "id": qid, "language": "en",
             "value": new, "token": csrf}, "POST")
        print(f"  {iid}  ✓")
        ok += 1
        time.sleep(0.3)
    except Exception as e:
        print(f"  {iid}  ERROR: {e}")
        err += 1

print(f"\nDone.  OK: {ok}   Errors: {err}")
