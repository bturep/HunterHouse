# WIKIBASE_MAINPAGE.md — Wikibase Main Page working file

Continuity record for editing **https://hunterhouse.wikibase.cloud/wiki/Main_Page**
(the MediaWiki front page of the Wikibase instance — *not* a site HTML file, not in the GitHub Pages deploy).

Read this file before resuming Main Page work. It is self-contained: current wikitext,
QID map, decisions, publish workflow, and revision history are all here so no re-querying
is needed to pick up.

---

## Status

| | |
|---|---|
| Live page | https://hunterhouse.wikibase.cloud/wiki/Main_Page |
| Current revision | **4439** |
| Last edited | 2026-05-17 (session: technical reframe) |
| Working branch when edited | `v1.04` |
| Editor | bot `MyBot@my-bot` via MediaWiki API |

### Revision history (for rollback)

| Rev | What |
|---|---|
| **4439** | Dropped ID-prefix column (only archive-item IDs are a real scheme); source-collection count made open-ended. **← current** |
| 4438 | First technical rewrite: removed biography / "character of the record" / "design arcs"; resolved Q? links; corrected ID scheme + counts; added Arrangement / Rights / Endpoints; epigraph removed. |
| 2864 | Original pre-edit page (long biography + character + design-arcs narrative, broken Q? links, malformed epigraph div, truncated `= Tools =`). Revert target if a full undo is ever wanted. |

Roll back with: edit the page text back to a prior revision's content (history is at
`Special:History/Main_Page`), or re-publish saved wikitext via the workflow below.

---

## What this page is for (intent agreed with Brandon)

- **Technical / data-model entry point.** Not a biography. Hunter-the-person narrative,
  "character of the record", and "design arcs" were deliberately removed — that material
  lives on the Foundation's public site (hunterhousefoundation.com), not here.
- This Wikibase page is **the data layer**: what the archive *is* structurally, how it is
  arranged, what the item model is, rights, and endpoints.
- Source text for the technical framing was lifted from `browse.html`'s about-pane
  (the `#about-pane` block, ~line 1185+ in browse.html) — keep the two in sync in spirit.

---

## Decisions made (don't re-litigate without reason)

1. **Epigraph dropped.** The Richard Hunter "Architecture, the sheltering art…" quote box
   was removed at Brandon's request (belongs on the Foundation site). Its old `<div>` was
   also malformed (`style=` missing opening quote) — moot now, but note if it ever returns.
2. **"Hunter House Foundation" is NOT an item.** The Wikibase models the organisational
   steward as **Q187 "Hunter House Stewardship Project"**. Use Q187; do not invent/link a
   "Hunter House Foundation" item. This also keeps Foundation branding off the technical page.
3. **CAA disambiguation:** the institution/repository is **Q178** (`archive`,
   "institutional archive at the University of Calgary"). **Q116** is a *different* item
   with the same label (a rights/permission item) — do **not** link Q116 as the repository.
4. **ID-prefix column removed from the Data model table.** Investigation showed only
   archive-item IDs are a real, curated, consistently-formatted scheme
   (`HH-HHC-0004`, `HH-CAA-0002` — zero-padded to 4 digits, P2 = "HH archive ID").
   The other prefixes exist in P2 but are unpadded and incidental (`HH-W-1`, `HH-P-1`,
   `HH-PH-23`, `HH-A-1`, `HH-B-1`, `HH-E-8`, `HH-I-1`) and are **not** a maintained
   identifier scheme — presenting them as the data model overstated reality. Page now says:
   every item is addressed by a persistent **Wikibase QID**; archive items additionally
   carry the curated HH-HHC-#### / HH-CAA-#### archive ID.
5. **"Six source collections" de-determined.** Brandon: more collections will come. Page
   now says "a growing set of source collections; more are expected as material is
   processed." Don't reintroduce a hard count.
6. **Source-collections table** shows *live catalogued counts* (HHC 114, CAA 35, others
   pending), not physical-accession extents. The CAA physical accession figures (2019.61 —
   344 drawings / 62 photographs / 0.22 linear m. textual / 1955–2010) are kept inline in
   the intro paragraph instead.

---

## Reference data (verified live 2026-05-17 — no need to re-query)

### Resolved QIDs (used in the page)

| Entity | QID | Type |
|---|---|---|
| Hunter Residence (the Work) | **Q234** | house / Work |
| Richard Morrow Hunter | **Q201** | human |
| Frances Hunter (person; old page said "Frances Mead Hunter") | **Q202** | human |
| Eric Gesinger | **Q209** | human |
| Ivan Hunter | **Q203** | human |
| Hunter House Stewardship Project (the org steward) | **Q187** | stewardship project |
| Richard Hunter fonds (fonds-level item) | **Q179** | archival collection (fonds) |
| Canadian Architectural Archives — repository/institution | **Q178** | archive |
| Canadian Architectural Archives — *do not use as repo* | Q116 | rights/permission item, same label |
| West Vancouver Museum | **Q186** | museum |
| Hunter House Collection | **Q180** | archival collection |
| John Fulker Collection | **Q184** | archival collection |
| Eric Gesinger Collection | **Q182** | archival collection |
| Frances Hunter Collection | **Q181** | archival collection |
| Ivan Hunter Collection | **Q183** | archival collection |

Not yet in Wikibase: a dedicated "Hunter House Foundation" org item (use Q187 instead).

### Live counts (P2 prefix grouping / P79 source collection)

| Item Type | Count | P2 prefix in data (note format) |
|---|---|---|
| Work | 22 | `HH-W-1` (unpadded) |
| Phase | 38 | `HH-PH-23` (unpadded) |
| Area | 36 | `HH-A-1` (unpadded) |
| Archive Item | 149 | `HH-HHC-0004` / `HH-CAA-0002` (**4-digit padded — the real scheme**) |
| Person | 33 | `HH-P-1` (unpadded) |
| Event | 5 | `HH-E-8` (unpadded) |
| Institution | 20 | `HH-I-1` (unpadded) |
| Building | 3 | `HH-B-1` (unpadded) |
| Place | — | no P2 (Wikidata-linked) |

- Archive items by source collection: **HHC 114** (110 with preview image) · **CAA 35**
  (35 with image). Other four collections: 0 catalogued yet.
- ~485 total entity items; only 306 carry any P2. ~150 are the browse.html-visible
  archive items (P2 + P96).
- `wdt:` prefix on this instance = `https://hunterhouse.wikibase.cloud/prop/direct/`
  (NOT the wikidata.org default — SPARQL fails silently/0-results without the explicit
  PREFIX). SPARQL endpoint: `https://hunterhouse.wikibase.cloud/query/sparql`.

---

## Publish workflow

`/tmp` is ephemeral — the working copy there will be gone next session. The **canonical
current wikitext is embedded at the bottom of this file**. To edit & republish:

1. Write the embedded wikitext (or your edited version) to a working file, e.g.
   `/tmp/mainpage_new.wikitext`. Or pull the live version fresh:
   ```bash
   curl -s "https://hunterhouse.wikibase.cloud/w/api.php?action=parse&page=Main_Page&prop=wikitext&format=json" \
     | python3 -c "import sys,json;open('/tmp/mainpage_new.wikitext','w').write(json.load(sys.stdin)['parse']['wikitext']['*'])"
   ```
2. Edit the working file.
3. Publish with the bot (credentials in `~/Documents/hh-wikibase-migration/.env`:
   `WIKIBASE_BOT_USER=MyBot@my-bot`, `WIKIBASE_BOT_PASSWORD=…`). The login flow is:
   GET logintoken → POST `action=login` → GET csrftoken → POST `action=edit`.
   The exact script used this session is reproduced below — save as
   `/tmp/publish_mainpage.py`, set the `"summary"` string, run `python3`:

```python
import os, requests
ENV = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")
cred = {}
for line in open(ENV):
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1); cred[k.strip()] = v.strip()
USER, PASS = cred["WIKIBASE_BOT_USER"], cred["WIKIBASE_BOT_PASSWORD"]
API = "https://hunterhouse.wikibase.cloud/w/api.php"
text = open("/tmp/mainpage_new.wikitext").read()
s = requests.Session()
s.headers.update({"User-Agent": "HunterHouse-MainPage-Update/1.0 (bturep)"})
ltok = s.get(API, params={"action":"query","meta":"tokens","type":"login","format":"json"}).json()["query"]["tokens"]["logintoken"]
assert s.post(API, data={"action":"login","lgname":USER,"lgpassword":PASS,"lgtoken":ltok,"format":"json"}).json()["login"]["result"] == "Success"
ctok = s.get(API, params={"action":"query","meta":"tokens","format":"json"}).json()["query"]["tokens"]["csrftoken"]
r = s.post(API, data={"action":"edit","title":"Main_Page","text":text,
    "summary":"<EDIT SUMMARY HERE>","token":ctok,"bot":1,"format":"json"}).json()
print(r["edit"]["result"], "rev", r["edit"].get("newrevid"), "was", r["edit"].get("oldrevid"))
```

4. After publishing, update the **Status** table and **Revision history** in this file,
   and append a one-line note to the change log below.

---

## Open / possible next edits (not yet done)

- Brandon will review in browser and request further edits — none pending as of rev 4439.
- Consider whether the **Arrangement** section's "series = source collection" framing
  needs the RAD/custody caveat noted in CLAUDE.md (series currently encodes physical
  custody, not creator function — deferred archival-standards item).
- If a real "Hunter House Foundation" org item is ever created in the Wikibase, revisit
  decision #2 (currently routed to Q187 Stewardship Project).
- Other four collections (Fulker / Gesinger / Frances / Ivan) show "—" / pending — update
  counts here and on the page when any are catalogued.

---

## Change log

- **2026-05-17** — Created this continuity file. Page at rev 4439. Session work:
  reframed Main Page from biography → technical data-model entry point (rev 4438),
  then dropped ID-prefix column + de-determined collection count (rev 4439).

---

## Canonical current wikitext (= live rev 4439 — verbatim)

Everything between the fences is the exact page source. Keep this updated to match the
live page whenever you publish.

```wikitext
__NOTOC__
<div style="font-family:'Iowan Old Style','Palatino',Georgia,serif; font-size:2em; font-weight:500; letter-spacing:-0.015em; margin-bottom:6px;">Hunter House Archive</div>
<div style="color:#6a6a6a; font-size:0.95em; margin-bottom:28px; font-style:italic;">An open, structured catalogue of the architectural records of the [[Item:Q234|Hunter Residence]] and the wider authorship of [[Item:Q201|Richard Morrow Hunter]] (1930–2023).</div>

= About =

This Wikibase is the structured record of the architectural archive catalogued by the [[Item:Q187|Hunter House Stewardship Project]]: the drawings, photographs, surveys, permits, and related materials documenting the design and continuous revision of the [[Item:Q234|Hunter Residence]] at 203 Goward Road, Prospect Lake, Saanich, British Columbia, together with the broader body of work by [[Item:Q201|Richard Morrow Hunter]]. Biographical and narrative context is maintained separately on the Foundation's public site; this instance is the data layer.

It is an open-data archive built on [https://wikiba.se/ Wikibase], the knowledge-graph software underlying [https://www.wikidata.org/ Wikidata]. Items are persistent and individually addressable by URI; statements are typed [https://www.w3.org/TR/rdf11-concepts/ RDF triples] carrying qualifiers, references, and ranks; the catalogue is [https://www.w3.org/TR/sparql11-query/ SPARQL]-queryable and federable against external [https://www.w3.org/wiki/LinkedData Linked Open Data] endpoints. Archival description follows [https://www.wikidata.org/wiki/Wikidata:GLAM GLAM] conventions and the [https://github.com/CCA-Public/digital-archives-manual Canadian Centre for Architecture's Digital Archives Manual], with multi-level arrangement at fonds, series, file, and item. Items are aligned to external identifiers (Q-IDs) for cross-catalogue reconciliation.

= Arrangement =

Description follows a four-level hierarchy. Effort is invested at the file and series levels rather than the individual item, after CCA practice.

{| class="wikitable" style="font-size:0.95em;"
! Level !! Maps to !! In this Wikibase
|-
| '''Fonds''' || ISAD(G) / RAD fonds || [[Item:Q179|Richard Hunter fonds]] — the whole of Hunter's professional and personal records
|-
| '''Series''' || Source collection || The source collections below; an item's series is recorded on the ''source collection'' property
|-
| '''File''' || Project phase || Discrete design iterations and schemes within a Work (''part of'' → Phase)
|-
| '''Item''' || Archive Item || The primary materials — drawings, photographs, correspondence, permits, interviews
|}

= Source collections =

The archive draws on a growing set of source collections; more are expected as material is processed. The complementary character of the two largest is significant: Hunter donated his original 1970–74 build documentation to the [[Item:Q178|Canadian Architectural Archives]] (University of Calgary, accession 2019.61 — 344 drawings, 62 photographs, 0.22 linear m. textual, 1955–2010) and kept the working files for everything that came after. Together they form a continuous fifty-year drawing record of a single property. Catalogued counts below reflect the live state of this Wikibase.

'''Institutional custody'''

{| class="wikitable" style="font-size:0.95em; margin-bottom:14px;"
! Collection !! Custodian !! Catalogued here !! Reference
|-
| '''[[Item:Q178|Canadian Architectural Archives]]''' || University of Calgary · accession 2019.61 || 35 archive items || [https://searcharchives.ucalgary.ca/richard-hunter-accession Finding aid →]
|-
| '''[[Item:Q184|John Fulker Collection]]''' || [[Item:Q186|West Vancouver Museum]] || — || Pending integration
|}

'''Personal custody'''

{| class="wikitable" style="font-size:0.95em;"
! Collection !! Custodian !! Catalogued here !! Status
|-
| '''[[Item:Q180|Hunter House Collection]]''' || [[Item:Q187|Hunter House Stewardship Project]] || 114 archive items || Primary collection
|-
| '''[[Item:Q182|Eric Gesinger Collection]]''' || [[Item:Q209|Eric Gesinger]] || — || Pending processing
|-
| '''[[Item:Q181|Frances Hunter Collection]]''' || [[Item:Q202|Frances Hunter]] || — || Pending processing
|-
| '''[[Item:Q183|Ivan Hunter Collection]]''' || [[Item:Q203|Ivan Hunter]] || — || Pending processing
|}

= Data model =

The archive is organized into nine Item Types, each with its own controlled vocabulary. Every item is addressed by a persistent Wikibase QID; archive items additionally carry a curated identifier (the ''HH archive ID'' property) in the HH-HHC-#### / HH-CAA-#### form. Counts are live.

{| class="wikitable" style="font-size:0.95em;"
! Item Type !! Covers !! Count
|-
| '''Work''' || Buildings, additions, gardens, renovations, theoretical projects, and other authored architectural works || 22
|-
| '''Phase''' || Discrete design iterations, schemes, and sub-projects within a Work || 38
|-
| '''Area''' || Named architectural sub-parts of a Work — wings, rooms, towers, gardens, decks, built features || 36
|-
| '''Archive Item''' || The primary materials, sub-typed by medium: drawing, photograph, engineering document, land survey, permit set, ephemera || 149
|-
| '''Person''' || Individuals connected to Hunter's practice and to the archive || 33
|-
| '''Event''' || Dated occurrences — exhibitions, sojourns, interviews, site visits, screenings || 5
|-
| '''Institution''' || Source repositories, covenant holders, educational and religious bodies, the stewardship project itself || 20
|-
| '''Building''' || Discrete physical structures designed by others that Hunter renovated or added to || 3
|-
| '''Place''' || Named geographic locations referenced by the archive || —
|}

= Rights =

Structured metadata: [https://creativecommons.org/publicdomain/zero/1.0/ CC0], per Wikibase/Wikidata convention. Content — drawings, documents, photographs: [https://creativecommons.org/licenses/by-nc-nd/4.0/ CC BY-NC-ND 4.0], rights granted by Frances Hunter. Material held by the [https://asc.ucalgary.ca/ Canadian Architectural Archives, University of Calgary] remains under separate stewardship; contact them for use.

= Endpoints =

* '''Browse''' — [[Special:AllPages]] · [[Special:ListProperties]] · [[Special:Search]]
* '''Query''' — [https://hunterhouse.wikibase.cloud/query SPARQL endpoint]
* '''Web-rendered view''' — [https://bturep.github.io/HunterHouse/ bturep.github.io/HunterHouse], a queried front end over this Wikibase. The Foundation's public-facing site will be at hunterhousefoundation.com.
* '''Source''' — [https://github.com/bturep/HunterHouse github.com/bturep/HunterHouse]
```
