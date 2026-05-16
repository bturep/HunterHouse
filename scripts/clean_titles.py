#!/usr/bin/env python3
"""
Clean bracketed annotations from all item labels in one pass.

Groups:
  A  — strip bracket only (title base remains meaningful, content redundant)
  B  — Untitled [x] → x  (bracket becomes the title)
  C  — Hunter House Photograph [x] → new descriptive title
  D  — strip bracket, move content to P100 notes
  E  — Land Survey [x] → Land Survey, x

Run with --dry-run first.
"""

import urllib.request, urllib.parse, json, http.cookiejar, sys, time

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

# ── Change table ──────────────────────────────────────────────────────────────
# Each entry: archive_id → { label, note (replaces P100), note_append (appends to P100) }
# note / note_append are optional; omit if no P100 change needed.

CHANGES = {

    # ── Group A: strip bracket — title base is meaningful, content redundant ──
    "HH-HHC-0019": {"label": "Hunter House Roof"},
    "HH-HHC-0020": {"label": "Hunter House Roof"},
    "HH-HHC-0021": {"label": "Hunter House Roof"},
    "HH-HHC-0060": {"label": "Entry Garden, Walkway and Driveway"},
    "HH-CAA-0025": {"label": "Hunter House - Scheme II"},
    "HH-CAA-0026": {"label": "Hunter House - Scheme II"},

    # ── Group B: Untitled [x] → x ─────────────────────────────────────────────
    "HH-HHC-0008": {"label": "Cascade Deck"},
    "HH-HHC-0009": {"label": "Cascade Deck"},
    "HH-HHC-0016": {"label": "Hunter Haus Addition, West Wing"},
    "HH-HHC-0017": {"label": "Hunter Haus Addition, West Wing Apartment"},
    "HH-HHC-0025": {"label": "Tower Elevation, Siding Detail, Stucco Box Detail"},
    "HH-HHC-0028": {"label": "Entry Door"},
    "HH-HHC-0029": {"label": "Entry Door"},
    "HH-HHC-0030": {"label": "Entry Door"},
    "HH-HHC-0031": {"label": "Entry Garden"},
    "HH-HHC-0048": {"label": "East Wing, South Face Addition"},
    "HH-HHC-0049": {"label": "SE Exit"},
    "HH-HHC-0050": {"label": "East Wing Dining Room"},
    "HH-HHC-0051": {"label": "East Wing Sunroom, Skywalk, Bedroom 1 Bathroom"},
    "HH-HHC-0052": {"label": "East Wing, SE Side Elevation"},
    "HH-HHC-0053": {"label": "Sunroom with Bedroom 2 Bathroom"},
    "HH-HHC-0054": {"label": "Sunroom, Skywalk, Bedroom 2 Bathroom"},
    "HH-HHC-0055": {"label": "Dining Room"},
    "HH-HHC-0059": {"label": "Entry Garden Walkway Lantern"},
    "HH-HHC-0061": {"label": "Entry Garden Walkway"},
    "HH-HHC-0070": {"label": "Veranda Roof"},
    "HH-HHC-0071": {"label": "Veranda Elevation, Plan"},
    "HH-HHC-0072": {"label": "Veranda Exterior, S.W. Screen Wall"},
    "HH-HHC-0107": {"label": "East Wing Living Room Extension"},
    "HH-HHC-0109": {"label": "Dining Room, Picture Frame Inset"},
    "HH-HHC-0110": {"label": "Shelves"},

    # ── Group C: photographs ───────────────────────────────────────────────────
    "HH-CAA-0010": {"label": "Hunter House, Atrium, Interior Garden"},
    "HH-CAA-0011": {"label": "Hunter House, Atrium, Sitting Area, Interior Garden"},
    "HH-CAA-0012": {"label": "Hunter House, Exterior, South West Side"},
    "HH-CAA-0013": {"label": "Hunter House, Living Room, Dining Room, Kotatsu"},
    "HH-CAA-0014": {"label": "Hunter House, Exterior, South West Side (2)"},
    "HH-CAA-0015": {"label": "Hunter House, Exterior, South West Side — Frances and Child"},
    "HH-CAA-0016": {"label": "Hunter House, Exterior, South West Side — Two Children, Construction"},
    "HH-CAA-0017": {"label": "Hunter House, Exterior, South Corner — Construction"},
    "HH-CAA-0018": {"label": "Hunter House, Living Room, Dining Room, Kotatsu — Frances and 3 Children"},
    "HH-CAA-0019": {"label": "Hunter House, Atrium, Interior Garden — Construction"},

    # ── Group D: strip bracket, add unique content to P100 notes ──────────────
    "HH-CAA-0001": {"label": "House for Frances and Richard Hunter - Pre-Scheme I",
                    "note": "Star Form"},
    "HH-CAA-0002": {"label": "House for Frances and Richard Hunter - Pre-Scheme I",
                    "note": "Star Form"},
    "HH-CAA-0003": {"label": "House for Richard and Frances Hunter - Pre-Scheme II",
                    "note_append": "Tilted Form"},
    "HH-CAA-0004": {"label": "House for Richard and Frances Hunter - Pre-Scheme II",
                    "note": "Tilted Form"},
    "HH-CAA-0005": {"label": "House for Richard and Frances Hunter - Pre-Scheme II",
                    "note": "Tilted Form"},
    "HH-CAA-0006": {"label": "House for Richard and Frances Hunter - Pre-Scheme II",
                    "note": "Tilted Form"},
    "HH-CAA-0020": {"label": "House for Frances and Richard Hunter - Scheme 1A",
                    "note": "East Wing Renovation"},
    "HH-CAA-0023": {"label": "House for Frances and Richard Hunter - Scheme 1A",
                    "note_append": "East Wing Roof Alteration"},
    "HH-CAA-0027": {"label": "Hunter House - Scheme II",
                    "note_append": "Colored with Legend"},
    "HH-HHC-0039": {"label": "East Wing Kitchen",
                    "note": "Circular Counter Extension"},
    "HH-HHC-0058": {"label": "Entry Garden Plan, Colored"},   # keep in title to distinguish from 0057
    "HH-HHC-0064": {"label": "Entry Garden Walkway, Primary Plan"},  # keep to distinguish from 0061

    # ── Group E: land surveys — strip bracket, fold into title ─────────────────
    "HH-HHC-0001": {"label": "Land Survey, Full Site Survey for Original Subdivision of Barbara Rankin Property"},
    "HH-HHC-0002": {"label": "Land Survey, Full Site Survey for Second Subdivision of Barbara Rankin Property"},
    "HH-HHC-0034": {"label": "Land Survey, Entry Garden Walkway"},
    "HH-HHC-0063": {"label": "Land Survey, Entry Garden Walkway"},
    "HH-HHC-0073": {"label": "Land Survey, SE Corner, East Wing"},
    "HH-HHC-0083": {"label": "Land Survey, Full Site Survey with Covenant"},
}

# ── Fetch QIDs + current P100 state ──────────────────────────────────────────
ids_list = ", ".join(f'"{i}"' for i in CHANGES)
rows = sparql("""
PREFIX wdt: <https://hunterhouse.wikibase.cloud/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?item ?id ?label ?notes WHERE {
  ?item wdt:P2 ?id .
  ?item rdfs:label ?label . FILTER(LANG(?label)="en")
  OPTIONAL { ?item wdt:P100 ?notes }
  FILTER(?id IN (""" + ids_list + """))
}
""")

# Deduplicate (multiple P100 rows possible)
state = {}
for r in rows:
    iid = r["id"]["value"]
    if iid not in state:
        state[iid] = {
            "qid":   r["item"]["value"].split("/").pop(),
            "label": r["label"]["value"],
            "notes": r.get("notes", {}).get("value", ""),
        }

# ── Preview all changes ───────────────────────────────────────────────────────
print(f"{len(CHANGES)} items to update{'  (DRY RUN)' if DRY_RUN else ''}\n")

for iid, change in sorted(CHANGES.items()):
    if iid not in state:
        print(f"  {iid}  NOT FOUND in Wikibase — skipping")
        continue
    s = state[iid]
    print(f"  {iid}  ({s['qid']})")
    print(f"    label:  {s['label']}")
    print(f"    label→  {change['label']}")
    if "note" in change:
        existing = s["notes"]
        print(f"    P100:   {existing or '(none)'}")
        print(f"    P100→   {change['note']}")
    elif "note_append" in change:
        existing = s["notes"]
        appended = (existing.rstrip(" .") + " — " + change["note_append"]).strip() if existing else change["note_append"]
        print(f"    P100:   {existing or '(none)'}")
        print(f"    P100→   {appended}")

if DRY_RUN:
    sys.exit(0)

# ── Login ────────────────────────────────────────────────────────────────────
lt   = api({"action": "query", "meta": "tokens", "type": "login"})["query"]["tokens"]["logintoken"]
r    = api({"action": "login", "lgname": USER, "lgpassword": PASSWORD, "lgtoken": lt}, "POST")
print("\nLogin:", r["login"]["result"])
csrf = api({"action": "query", "meta": "tokens"})["query"]["tokens"]["csrftoken"]

# ── Apply ────────────────────────────────────────────────────────────────────
print("\nWriting...\n")
ok = err = 0

for iid, change in sorted(CHANGES.items()):
    if iid not in state:
        continue
    s   = state[iid]
    qid = s["qid"]
    try:
        # 1. Update label
        api({"action": "wbsetlabel", "id": qid, "language": "en",
             "value": change["label"], "token": csrf}, "POST")

        # 2. Handle P100 notes if needed
        if "note" in change or "note_append" in change:
            # Fetch current P100 claim guid (if any)
            entity   = api({"action": "wbgetentities", "ids": qid, "props": "claims"})
            claims   = entity["entities"][qid]["claims"].get("P100", [])
            existing = s["notes"]

            if "note_append" in change:
                new_note = (existing.rstrip(" .") + " — " + change["note_append"]).strip() if existing else change["note_append"]
            else:
                new_note = change["note"]

            if claims:
                guid = claims[0]["id"]
                api({"action": "wbsetclaimvalue", "claim": guid, "snaktype": "value",
                     "value": json.dumps(new_note), "token": csrf}, "POST")
            else:
                api({"action": "wbcreateclaim", "entity": qid, "snaktype": "value",
                     "property": "P100", "value": json.dumps(new_note), "token": csrf}, "POST")

        print(f"  {iid}  ✓")
        ok += 1
        time.sleep(0.3)

    except Exception as e:
        print(f"  {iid}  ERROR: {e}")
        err += 1

print(f"\nDone.  OK: {ok}   Errors: {err}")
