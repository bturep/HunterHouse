# Hunter House Archive — Wikibase Context

Working reference for the Wikibase at **hunterhouse.wikibase.cloud**.  
Load this file at the start of any Claude session to enable assisted entry and batch editing.

---

## Instance

| | |
|---|---|
| **Base URL** | `https://hunterhouse.wikibase.cloud` |
| **JSON API** | `https://hunterhouse.wikibase.cloud/w/api.php` |
| **SPARQL** | `https://hunterhouse.wikibase.cloud/query/sparql` |
| **QuickStatements** | `https://hunterhouse.wikibase.cloud/tools/quickstatements` |
| **Item browser** | `https://hunterhouse.wikibase.cloud/wiki/Special:ItemDisambiguation` |
| **Search** | `https://hunterhouse.wikibase.cloud/wiki/Special:Search` |

Authentication: log in via the Wikibase.cloud account. QuickStatements uses OAuth — authorize once through the QS interface, tokens are reused per session.

---

## Recommended workflow

**Browser editing is slow.** The recommended alternative is **QuickStatements + Claude**.

### How it works

1. Open `WIKIBASE.md` in a Claude Code session (load this file or paste it).
2. Describe what you want to add or change — in plain language, from a spreadsheet, or by pasting a photo caption.
3. Claude generates a QuickStatements batch (see format below).
4. Paste the batch into `https://hunterhouse.wikibase.cloud/tools/quickstatements`.
5. Click **Run** — edits execute via the API in sequence.

For **new items**: use `CREATE` blocks (see §QuickStatements reference below).  
For **editing existing items**: use `Q###|P##|value` lines directly.  
For **bulk changes to many items at once**: use a SPARQL query to get the QIDs first, then generate edit lines.

---

## Properties (PIDs) — complete table

### Archive item properties

| PID | Label | Type | Notes |
|---|---|---|---|
| P1 | instance of | Item | Q88=drawing · Q89=photograph · Q90=correspondence · Q91=publication · Q92=ephemera · Q93=report · Q94=permit |
| P2 | HH archive ID | String | `HH-A-0001` format. **Required on all items.** |
| P62 | part of | Item | Project phase/set (primary). Link to a Q###. |
| P64 | start date | Time | Drawing date (preferred over P82 when known precisely) |
| P79 | source collection | Item | Q180=HHC · Q178=CAA · Q184=FUL · Q182=GES · Q181=FRH · Q183=IVH |
| P80 | creator | Item | Q201=Richard Hunter · Q221=John Fulker · etc. |
| P82 | date created | Time | Drawing date — use precision `/9` (year) or `/10` (month) |
| P83 | date digitized | Time | Date scanned — **do not use for sorting/display**; 2026 dates are digitization, not creation |
| P84 | part of phase | Item | Secondary phase link (use when item spans two phases) |
| P86 | set position | String | `"01 of 12"` — position within a project set |
| P87 | depicts area | Item | Multi-valued. See §Areas vocabulary below |
| P88 | drawing type | Item | Q98=plan · Q99=elevation · Q100=section · Q101=detail · etc. |
| P89 | drawing use | String | e.g. "Design development" · "Permit" · "Construction" |
| P90 | scale | String | e.g. `"1:50"` or `"NTS"` |
| P91 | medium | String | e.g. `"Pencil on vellum"` |
| P92 | built status | Item | Q51=built · Q52=partially built · Q53=unbuilt · Q54=theoretical |
| P93 | rights | Item | Link to rights statement item |
| P94 | held by | Item | Physical custodian |
| P95 | master file | URL | Full-resolution image URL |
| P96 | preview image | URL | Web-resolution preview URL. **Required for browse.html display.** |
| P97 | legacy identifier | String | Old ID if renumbered |
| P98 | unique identifier | String | UUID or other permanent ID |
| P99 | archive link | URL | Link to CAA finding aid or external record |
| P100 | notes | String | Prose description shown in browse.html meta pane. This is the human-readable note — not the auto-generated Wikibase description. |
| P118 | point in time | Time | Use when a single date applies (not a range) |
| P128 | sourced from | String | Citation or evidence for a claim |

### Other properties in the schema (for reference)

| PID | Label | Type |
|---|---|---|
| P3 | Wikidata ID | ExternalId |
| P4 | architect | Item |
| P5 | client | Item |
| P6 | dedicated to | Item |
| P7 | street address | String |
| P25 | CAA archive reference | ExternalId |
| P30 | date of birth | Time |
| P32 | date of death | Time |
| P57 | VIAF ID | ExternalId |
| P60 | official website | URL |
| P63 | phase type | Item |
| P65 | end date | Time |
| P66 | precedes | Item |
| P67 | follows | Item |
| P85 | documents Work | Item |
| P107 | fonds reference | String |
| P109 | finding aid URL | URL |

---

## Controlled vocabulary

### Item types (P1)

| QID | Label |
|---|---|
| Q88 | drawing |
| Q89 | photograph |
| Q90 | correspondence |
| Q91 | publication |
| Q92 | ephemera |
| Q93 | report |
| Q94 | permit |

### Drawing types (P88)

| QID | Label |
|---|---|
| Q98 | plan |
| Q99 | elevation |
| Q100 | section |
| Q101 | detail |
| Q102 | foundation plan |
| Q103 | framing plan |
| Q104 | floor framing plan |
| Q105 | roof framing plan |
| Q106 | roof plan |
| Q107 | ceiling plan |
| Q108 | reflected ceiling plan |
| Q109 | electrical plan |
| Q110 | site plan |
| Q111 | land survey |
| Q112 | survey |
| Q113 | construction (drawing type — check) |

### Built status (P92)

| QID | Label |
|---|---|
| Q51 | built |
| Q52 | partially built |
| Q53 | unbuilt |
| Q54 | theoretical / speculative |
| Q55 | demolished |
| Q56 | status unknown |

### Source collections (P79)

| QID | Code | Name | Custodian | Count |
|---|---|---|---|---|
| Q180 | HHC | Hunter House Collection | Hunter House Foundation | 110 |
| Q178 | CAA | Canadian Architectural Archives | University of Calgary | 18 |
| Q184 | FUL | John Fulker Collection | West Vancouver Museum | 9 |
| Q182 | GES | Eric Gessinger Collection | Eric Gessinger | pending |
| Q181 | FRH | Frances Hunter Collection | Frances Hunter | pending |
| Q183 | IVH | Ivan Hunter Collection | Ivan Hunter | pending |

### Project phases / sets (P62 / P84)

These are the QIDs for project sets that items belong to.

| QID | Label |
|---|---|
| Q256 | Pre-Scheme I — Star Form |
| Q257 | Pre-Scheme II — Tilted Form |
| Q258 | 1970 Scheme 1 — OG Build |
| Q259 | Original Cottage Permit |
| Q260 | Hunter Residence Photographs |
| Q261 | Pier for 203 Goward Road |
| Q262 | Scheme 1A — East Wing Renovation |
| Q263 | Hunter House Addition Scheme I |
| Q264 | Cascade Deck |
| Q265 | Scheme II — Pencil Studies |
| Q266 | 1990 Hunter Haus Addition Permit Set |
| Q267 | 1990 West Wing Construction |
| Q268 | Colour Studies for Hunter House |
| Q269 | 1995 Hunter House Roof Permit Set |
| Q270 | 1996 Beam Repairs (Brown and Grant Engineering) |
| Q271 | 1996 Tower & Apartment Construction |
| Q272 | Bedroom 1 Closet |
| Q273 | 2002 Entry Door Set |
| Q274 | 2005 West Wing Studio (Island Work Station) |
| Q276 | 2008 East Wing Construction |
| Q278 | 2009 East Wing Kitchen Counter |
| Q279 | 2010 East Wing Dining Room Design |
| Q281 | 2015 Veranda Roof Set |

*To add a new project set: create a new item with `instance of` → `Q2` (architectural phase).*

### Key people (P80 / P4 / P5)

| QID | Name |
|---|---|
| Q201 | Richard Morrow Hunter |
| Q202 | Frances Hunter |
| Q203 | Ivan Hunter |
| Q221 | John Fulker |
| Q205 | Floyd Marinescu |
| Q206 | Olivia Jol |
| Q207 | Brandon Poole |
| Q209 | Eric Gessinger |

### Key works / buildings

| QID | Name |
|---|---|
| Q234 | Hunter Residence (203 Goward Road) |
| Q198 | Sloss House |
| Q199 | Kerr House |

---

## Identifier schema

| Prefix | Type | Example |
|---|---|---|
| `HH-A-####` | Architectural drawing | `HH-A-0001` |
| `HH-P-####` | Photograph | `HH-P-0009` |
| `HH-L-####` | Letter / correspondence | `HH-L-0004` |
| `HH-E-####` | Engineering document | `HH-E-0002` |
| `HH-N-####` | Notebook / sketch | `HH-N-0001` |

IDs are zero-padded to four digits and run in order of cataloguing. They are never reassigned. P97 holds the legacy ID if an item was renumbered.

---

## QuickStatements reference

### Format

Each line is a tab-separated command. The first field is the item QID (or `CREATE` / `LAST`). The second field is the property. The third is the value.

```
# Create a new item
CREATE
LAST|Len|"HH-A-0148"
LAST|Den|"architectural drawing; HHC; 1992"
LAST|P1|Q88
LAST|P2|"HH-A-0148"
LAST|P79|Q180
LAST|P80|Q201
LAST|P82|+1992-00-00T00:00:00Z/9
LAST|P62|Q268
LAST|P88|Q99
LAST|P96|"https://example.com/preview/HH-A-0148.jpg"
LAST|P100|"Elevation study for the West Wing colour scheme. Coloured pencil."

# Edit an existing item — add a missing property
Q462|P88|Q109
Q462|P82|+1992-00-00T00:00:00Z/9

# Edit an existing item — change a string value
Q462|P100|"Electrical plan for the living room bay extension."
```

### Date precision codes

| Code | Meaning | Example |
|---|---|---|
| `/9` | Year only | `+1990-00-00T00:00:00Z/9` |
| `/10` | Month | `+1990-06-00T00:00:00Z/10` |
| `/11` | Day | `+1990-06-15T00:00:00Z/11` |

Dates before 1000 CE need a leading zero: `+0958-00-00T00:00:00Z/9`.

### Common patterns

**Add preview image to an existing item:**
```
Q###|P96|"https://..."
```

**Set position within a project set:**
```
Q###|P86|"03 of 10"
```

**Link to a second phase (for items spanning two sets):**
```
Q###|P84|Q###
```

**Multi-valued property (e.g. multiple areas):**
```
Q###|P87|Q###
Q###|P87|Q###
```
(Repeat the property line — Wikibase appends each as a separate statement.)

---

## SPARQL queries

### All items with archive IDs and image URLs
```sparql
SELECT ?item ?id ?imageUrl WHERE {
  ?item wdt:P2 ?id .
  ?item wdt:P96 ?imageUrl .
} ORDER BY ?id
```

### Items missing a preview image (P96)
```sparql
SELECT ?item ?id WHERE {
  ?item wdt:P2 ?id .
  FILTER NOT EXISTS { ?item wdt:P96 ?x }
} ORDER BY ?id
```

### Items missing a date (P82, P64, P118 all absent)
```sparql
SELECT ?item ?id WHERE {
  ?item wdt:P2 ?id .
  FILTER NOT EXISTS { ?item wdt:P82 ?x }
  FILTER NOT EXISTS { ?item wdt:P64 ?x }
  FILTER NOT EXISTS { ?item wdt:P118 ?x }
} ORDER BY ?id
```

### Items by project phase
```sparql
SELECT ?item ?id ?label WHERE {
  ?item wdt:P62 Q266 .   # replace Q266 with target phase QID
  ?item wdt:P2 ?id .
  ?item rdfs:label ?label . FILTER(LANG(?label)="en")
} ORDER BY ?id
```

### Items missing a phase (P62 and P84 both absent)
```sparql
SELECT ?item ?id WHERE {
  ?item wdt:P2 ?id .
  FILTER NOT EXISTS { ?item wdt:P62 ?x }
  FILTER NOT EXISTS { ?item wdt:P84 ?x }
} ORDER BY ?id
```

### Count by source collection
```sparql
SELECT ?coll ?collLabel (COUNT(?item) AS ?n) WHERE {
  ?item wdt:P79 ?coll .
  SERVICE wikibase:label { bd:serviceParam wikibase:language "en" }
} GROUP BY ?coll ?collLabel ORDER BY DESC(?n)
```

### All items with notes (P100)
```sparql
SELECT ?item ?id ?notes WHERE {
  ?item wdt:P2 ?id .
  ?item wdt:P100 ?notes .
} ORDER BY ?id
```

---

## Cataloguing status

| Collection | Target | Catalogued | Images | Notes |
|---|---|---|---|---|
| HHC | ~200+ | 110 | partial | Primary working collection |
| CAA | ~344 drawings + 62 photos | 18 | partial | Early drawings donated 2019/2021 |
| FUL | 9 (full set) | 9 | partial | Fulker photographs |
| GES | unknown | 0 | none | Furniture drawings; pending ingest |
| FRH | unknown | 0 | none | Frances Hunter materials; pending |
| IVH | unknown | 0 | none | Ivan Hunter photographs; pending |

**Current Wikibase item count with P2 + P96:** 147 items shown in browse.html.

**Known gaps (from browse.html):**  
Items HH-A-80, HH-A-86 and others show "—" in the Year column — they have a P83 (date digitized) but no drawing date (P82/P64/P118). These need a drawing date added.

---

## Working notes

### Date property priority
The public site reads dates in this order: **P82 → P64 → P118**. It never reads P83 (date digitized). Items with only P83 will show "—" in browse.html. When adding dates, use P82 for "date created" on drawings.

### Notes field (P100)
The `meta-body` pane in browse.html shows P100 as the lede. Write P100 as a single prose sentence or short paragraph — no metadata formatting. The auto-generated Wikibase `schema:description` (which looks like "architectural drawing; HHC; 1990") is not shown publicly.

### browse.html filter
The "Source" dropdown in browse.html filters by P79 label. The value displayed is the label of the linked item, not the code (HHC/CAA etc.). This is resolved from Wikibase at load time.

### Creating a new project phase item
Before cataloguing a new project set, create its phase item:
```
CREATE
LAST|Len|"2018 East Wing Permit Set"
LAST|Den|"project phase; Hunter Residence"
LAST|P1|Q2
LAST|P62|Q234
```
Then use `LAST`'s QID (from QuickStatements output) as P62 on all items in the set.

---

## How to use this file with Claude

At the start of a session:
> "Load WIKIBASE.md from the HunterHouse repo. I want to add [description / paste CSV rows / paste scan list]."

Claude will generate QuickStatements batches using the QIDs and property codes above.  
You paste the batch into `hunterhouse.wikibase.cloud/tools/quickstatements` and run it.

Example prompts:
- "Generate QuickStatements for these 5 items — [paste scan log with IDs, dates, types]"
- "HH-A-0148 is missing a date and phase. It's a 1992 elevation, part of Q268."
- "Run a SPARQL query to find all items with no P100 note."
- "I want to add a new project phase called '2018 East Wing Permit Set'. What QS lines do I need?"
