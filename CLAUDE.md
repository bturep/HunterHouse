# CLAUDE.md — Hunter House Foundation session context

Load this file at the start of any Claude Code session. It covers the full project so you can immediately assist with site editing, Wikibase editing, and batch scripting.

---

## Memory protocol — instructions for Claude

This file is the persistent memory for this project. Follow these rules every session:

1. **On load** — read this file before doing anything else. Use it to orient.
2. **After each major task** — append a brief dated entry to the Session Log at the bottom. "Major task" means: any file edited and committed, any Wikibase items changed, any script run, any new design decision made.
3. **Mid-session** — if you discover something that changes the general understanding (a property works differently than documented, a QID was wrong, a workflow proved unreliable), update the relevant section of this file immediately, not just the log.
4. **End of session** — before the user leaves, consolidate: update the Cataloguing Status table if counts changed, revise any sections that are now out of date, and write a summary entry in the Session Log. Ask the user to commit and push so the updated CLAUDE.md lands on `main`.
5. **Never delete log entries.** Append only. The log is the audit trail.

---

## Project in one sentence

A static GitHub Pages site for the Hunter House Foundation + a live Wikibase at **hunterhouse.wikibase.cloud** cataloguing the architectural archive of Richard Morrow Hunter (1970–2020, 203 Goward Road, Saanich BC).

- **Local path:** `/Users/brandonpoole/Projects/HunterHouse`
- **GitHub repo:** github.com/bturep/HunterHouse
- **Live site:** https://bturep.github.io/HunterHouse/
- **Wikibase:** https://hunterhouse.wikibase.cloud
- **Deploy:** push to `main`, live in ~30 seconds via GitHub Pages

---

## Credentials and environment

All credentials live in `/Users/brandonpoole/Documents/hh-wikibase-migration/.env`.

Key values:
```
WIKIBASE_API=https://hunterhouse.wikibase.cloud/w/api.php
WIKIBASE_SPARQL=https://hunterhouse.wikibase.cloud/query/sparql
WIKIBASE_USER=Brandon
WIKIBASE_BOT_USER=MyBot@my-bot
WIKIBASE_BOT_PASSWORD=<in .env>
R2_PUBLIC_BASE=https://archive.hunterhousefoundation.com
```

The bot (`MyBot@my-bot`) was created via Special:BotPasswords and has write access to the Wikibase. Scripts load credentials from the `.env` file automatically — no manual entry needed.

---

## Repo file structure

```
HunterHouse/
├── index.html              Home — landing, Hunter epigraph, nav pathways
├── richard-hunter.html     Hunter — biography, chronology, exhibitions
├── the-house.html          House — narrative on the residence and drawing record
├── archive.html            Archive — how the catalogue is organised
├── about.html              About — mandate, people, fellowship, contact
├── browse.html             Browse — live Wikibase query, filter + search
│
├── assets/
│   ├── verso.css           Light design system (shared across all pages)
│   ├── inverse.css         Dark design system (reading pages only)
│   ├── Hunter.png          Portrait photo used on richard-hunter.html
│   └── hunter-mark.png     Foundation mark
│
├── scripts/
│   └── patch_dates.py      Batch Wikibase editor — adds P82 + updates descriptions
│
├── WIKIBASE.md             Full Wikibase reference (properties, QIDs, SPARQL, workflow)
├── CLAUDE.md               This file
├── README.md               Site architecture notes
└── Main_Page.wiki          Wikitext for hunterhouse.wikibase.cloud/wiki/Main_Page
```

---

## Design system

### Two CSS surfaces

| File | Surface | Used on |
|---|---|---|
| `assets/verso.css` | Light — ink on paper | All pages (header, catalogue) |
| `assets/inverse.css` | Dark — warm cream on near-black | 4 reading pages only |

Reading pages (richard-hunter, the-house, archive, about) load **both** stylesheets. The light `verso.css` governs the shared `<header class="site-top">`. The dark `inverse.css` governs `<main class="page-body">` and everything below it.

### Breakpoints

- `@media (max-width:767px)` — mobile. Global rules in `verso.css`. Per-page rules inline in `<style>` blocks.
- `@media (max-width:1100px)` — tablet. Handled inside `inverse.css` for the reading pages.
- `@media (max-width:760px)` — second inverse.css breakpoint (grids collapse to 1 col, title scales down).

### Key CSS tokens (verso.css)
```css
--ink: #202020; --muted: #6a6a6a; --rule: #e2e2e2;
--soft: #f7f5f0; --paper: #f4f0e6; --bg: #fafaf7;
--mono: 'JetBrains Mono', monospace;
```

### Key CSS tokens (inverse.css)
```css
--inv-bg: #1e1c1a; --inv-fg: #f3f1ec; --amber: #e4a47e; --plate: #f0e9d8;
```

---

## browse.html architecture

`browse.html` is the only dynamic page. It queries the Wikibase SPARQL endpoint at load time, builds an item list, and renders a three-pane shell.

### Shell layout (desktop)
```
.shell: grid 28% | 1fr | 28%
  .pane-list    — scrollable item list
  .pane-image   — selected item image + zoom
  .pane-meta    — selected item metadata (record)
```

### Mobile tabs
On `max-width:767px` the shell collapses to a single column and three tabs appear:
- **List** — item list
- **Item** — image pane
- **Record** — metadata pane

Tab switching: `switchMobileTab(pane)` toggles `.mobile-active` on panes and `.active` on tabs. Selecting an item on mobile auto-switches to the "image" pane.

### Date display
`firstDate()` reads P82 → P64 → P118 in order. Never reads P83 (date digitized — 2026 scan dates). Items with only P83 show "—" in browse.

### SPARQL queries
- **In the browser (browse.html):** use **GET** with `encodeURIComponent`. Browser encoding works correctly. POST is blocked by CORS.
- **In Python scripts:** use **POST** with `Content-Type: application/sparql-query`. Python's `urllib.parse.quote` mangles the query with GET; POST bypasses this.

---

## Wikibase — quick reference

See **`WIKIBASE.md`** for the full property table, all controlled-vocabulary QIDs, SPARQL query templates, QuickStatements syntax, and cataloguing status.

### Most-used properties
| PID | Label | Notes |
|---|---|---|
| P1 | instance of | Q88=drawing |
| P2 | HH archive ID | `HH-A-####` format |
| P62 | part of | project phase QID |
| P79 | source collection | Q180=HHC |
| P80 | creator | Q201=Richard Hunter |
| P82 | date created | year precision `/9` |
| P88 | drawing type | Q98=plan, Q99=elevation, etc. |
| P96 | preview image | URL — required for browse.html display |
| P100 | notes | prose shown in meta pane |

### Bot patching via API
```bash
python3 scripts/patch_dates.py
```
Loads `WIKIBASE_BOT_USER` / `WIKIBASE_BOT_PASSWORD` from `~/.../hh-wikibase-migration/.env` automatically. No input required.

### QuickStatements
Paste batches at: https://hunterhouse.wikibase.cloud/tools/quickstatements  
Note: the QS redirect chain sometimes fails. If items don't update, use `patch_dates.py` as a model and write a targeted Python script instead.

---

## Image pipeline — Cloudflare R2

Archive images are hosted on Cloudflare R2 at **https://archive.hunterhousefoundation.com**.

### Access
- `rclone` is installed and configured with the `hh-r2:` remote
- Credentials in `~/Documents/hh-wikibase-migration/.env` (R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_ACCOUNT_ID)
- Bucket name: `hunter-house-archive`

### Useful rclone commands
```bash
rclone ls hh-r2:hunter-house-archive          # list all files in bucket
rclone ls hh-r2:hunter-house-archive | grep HH-A-0044   # find a specific item
rclone copy /local/file.jpg hh-r2:hunter-house-archive  # upload a file
```

### Filename convention
```
HH-A-0044_Untitled_Cascade_Deck_1987-06-01_prev.jpg   ← preview (P96)
HH-A-0044_Untitled_Cascade_Deck_1987-06-01.jpg        ← master (P95)
```
Zero-padded ID, sanitized label, ISO date, `_prev` suffix for preview.

### Migration scripts (in `~/Documents/hh-wikibase-migration/scripts/`)
| Script | Purpose |
|---|---|
| `13a_r2_discover.py` | Probes public domain to find which files exist; builds `r2_manifest.tsv` |
| `13b_r2_write_claims.py` | Writes P96/P95 image URLs back to Wikibase items from the manifest |
| `13c_r2_manifest_from_local.py` | Builds manifest from a local file list instead of probing |

All scripts load credentials from `.env` automatically. Run from the `scripts/` directory.

### Workflow for adding images to new items
1. Upload files to R2 via `rclone copy`
2. Run `13a_r2_discover.py` (or `13c` if working from a local list) to build/update the manifest
3. Run `13b_r2_write_claims.py` to write P96/P95 URLs to Wikibase
4. Verify in browse.html — items with P96 appear in the gallery

---

## Batch change protocol — safe workflow for bulk Wikibase edits

Any operation that touches P2 (archive ID), P96/P95 (image URLs), or renames R2 files across many items must follow this protocol. It applies to the ID rename, any future re-numbering, and any bulk URL migration.

### Why this matters
Wikibase data is a live database — there is no git history for it. R2 files are the only copies of the images. A bad batch script can silently corrupt 150 items in seconds with no automatic undo. The protocol makes every change reversible.

---

### Step 0 — Export a snapshot before touching anything

Run this SPARQL query and save the result as a TSV in `~/Documents/hh-wikibase-migration/data/snapshots/` with a datestamped filename:

```sparql
PREFIX wdt: <https://hunterhouse.wikibase.cloud/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT ?item ?qid ?archId ?legacyId ?label ?preview ?master ?collection WHERE {
  ?item wdt:P2 ?archId .
  BIND(STRAFTER(STR(?item), "/entity/") AS ?qid)
  ?item rdfs:label ?label . FILTER(LANG(?label)="en")
  OPTIONAL { ?item wdt:P97 ?legacyId }
  OPTIONAL { ?item wdt:P96 ?preview }
  OPTIONAL { ?item wdt:P95 ?master }
  OPTIONAL { ?item wdt:P79 ?collection }
} ORDER BY ?archId
```

Commit the snapshot to git before proceeding:
```bash
git add data/snapshots/
git commit -m "Snapshot before <description of change>"
```

This snapshot is your ground truth. If anything goes wrong, it tells you exactly what every item looked like before.

---

### Step 1 — Create a git branch

```bash
git checkout -b migration/description-of-change
```

All scripts and mapping files for this change live on the branch. If the migration is abandoned, drop the branch and nothing is committed to main.

---

### Step 2 — Write the mapping file

Before running any script, write a TSV mapping every old state to every new state:
```
qid    old_id        new_id        old_p96_url    new_p96_url
Q331   HH-A-0027     HH-HHC-0027   https://...    https://...
```

Commit this mapping file to the branch. It is the ledger — the forward script reads it, and the revert script reads it in reverse.

---

### Step 3 — Write P97 (legacy ID) before changing P2

For every item, write the current P2 value into P97 *first*, before changing P2. This burns the old ID into Wikibase itself as a permanent record, and is the recovery anchor if P2 gets corrupted.

```python
# Always do this before wbsetclaim on P2:
add_claim(session, token, qid, "P97", old_id)   # legacy identifier
```

If the script fails partway through, items that were processed have P97 set. Items that weren't, still have the original P2. You can query for items where P2 ≠ P97 (when P97 exists) to find the boundary.

---

### Step 4 — R2: copy to new name, do NOT delete old files

```bash
rclone copy hh-r2:hunter-house-archive/HH-A-0027_name_date_prev.jpg \
            hh-r2:hunter-house-archive/HH-HHC-0027_name_date_prev.jpg
```

Old files stay in the bucket until Step 6 (verification passes). This means both URLs are live simultaneously during the migration window — no broken images.

---

### Step 5 — Update P2 and P96/P95 in Wikibase

Run the forward script. It reads the mapping file row by row:
1. `wbsetclaim` P2 ← new ID
2. `wbsetclaim` P96 ← new preview URL
3. `wbsetclaim` P95 ← new master URL (if present)
4. Log each QID as it completes

Build in a dry-run mode (`--dry-run`) that prints actions without executing them. Always run dry-run first.

---

### Step 6 — Verify before deleting anything

Run a SPARQL query to confirm:
- All expected items now have the new P2 format
- All P96 URLs resolve (HEAD probe each one)
- No items are missing a P2

Only after verification passes:
```bash
rclone delete hh-r2:hunter-house-archive/HH-A-0027_name_date_prev.jpg
```

---

### Step 7 — Merge and tag

```bash
git checkout main
git merge --no-ff migration/description-of-change
git tag v0.X
git push && git push --tags
```

---

### Revert procedure (if something goes wrong)

1. **Stop the forward script immediately.**
2. Run the revert script — it reads the mapping file in reverse:
   - Restore P2 from P97 on affected items
   - Restore P96/P95 old URLs (old R2 files are still present)
3. The snapshot from Step 0 is the reference for any items where state is ambiguous.
4. Do not delete old R2 files until the revert is confirmed clean.

---

### Pending: ID rename migration (HH-A-XXXX → HH-HHC-XXXX)

**Decision made 2026-05-14:**
- All Hunter House Collection items: `HH-A-XXXX` → `HH-HHC-XXXX` (same number, same zero-padding)
- CAA items: `HH-A-XXXX` → `HH-CAA-XXXX`
- Fulker items: `HH-A-XXXX` → `HH-FUL-XXXX`
- Each collection has its own sequence; numbers are preserved from current assignment
- Type letter (D/P/E/L/N) becomes UI-only, derived from P1 (instance of), not embedded in ID
- Old IDs preserved in P97 on every item

Status: **COMPLETE — 2026-05-14**
- 149 items renamed in Wikibase (P2 updated, old ID saved to P97)
- 290 R2 files copied to new names (old HH-A- files still in bucket, pending deletion)
- browse.html cache bumped to v7, tagged v0.6
- Revert script available at `scripts/revert_ids.py` if needed

---

## Scripts

### `scripts/patch_dates.py`
Adds P82 date claims and updates English descriptions on a hardcoded list of 18 items. Reads bot credentials from `.env`. No prompts.

To adapt for a new batch: copy the script, replace the `ITEMS` list, adjust `desc` template and year in `main()`.

---

## Wikibase editing workflow

**For small changes (1–5 items):** Use QuickStatements. Claude generates tab-separated QS lines; you paste and run.

**For bulk changes or when QS is unreliable:** Write a Python script modelled on `patch_dates.py`. The key API calls:
- `wbsetdescription` — set English description
- `wbcreateclaim` — add a property claim
- Login flow: GET logintoken → POST login → GET csrftoken → write operations

**For SPARQL queries:** Claude can write them; run at https://hunterhouse.wikibase.cloud/query or via POST in Python.

---

## Cataloguing status (as of May 2026)

| Collection | Catalogued | Images | Notes |
|---|---|---|---|
| HHC | ~110 items | partial | Primary working collection |
| CAA | 18 items | partial | Early drawings, donated 2019/21 |
| FUL | 9 items | partial | Fulker photographs |
| GES | 0 | none | Furniture drawings; pending |
| FRH | 0 | none | Frances Hunter materials; pending |
| IVH | 0 | none | Ivan Hunter photographs; pending |

**browse.html shows ~147 items** (those with P2 + P96).

**Known gaps:**
- Items missing P82 date: run the SPARQL query in WIKIBASE.md §"Items missing a date"
- Items missing P96 preview image: run the SPARQL query in WIKIBASE.md §"Items missing a preview image"

---

## Common tasks

### Add a date to an existing item (QuickStatements)
```
Q###|P82|+1992-00-00T00:00:00Z/9
```

### Create a new archive item (QuickStatements)
```
CREATE
LAST|Len|"HH-A-0148"
LAST|Den|"architectural drawing; HHC; 1992"
LAST|P1|Q88
LAST|P2|"HH-A-0148"
LAST|P79|Q180
LAST|P80|Q201
LAST|P82|+1992-00-00T00:00:00Z/9
LAST|P62|Q###
LAST|P88|Q99
LAST|P96|"https://archive.hunterhousefoundation.com/preview/HH-A-0148.jpg"
LAST|P100|"Prose note here."
```

### Add a new project phase
```
CREATE
LAST|Len|"2018 East Wing Permit Set"
LAST|Den|"project phase; Hunter Residence"
LAST|P1|Q2
LAST|P62|Q234
```

### Find items missing a date (SPARQL)
```sparql
SELECT ?item ?id WHERE {
  ?item wdt:P2 ?id .
  FILTER NOT EXISTS { ?item wdt:P82 ?x }
  FILTER NOT EXISTS { ?item wdt:P64 ?x }
  FILTER NOT EXISTS { ?item wdt:P118 ?x }
} ORDER BY ?id
```

### Find items missing a preview image (SPARQL)
```sparql
SELECT ?item ?id WHERE {
  ?item wdt:P2 ?id .
  FILTER NOT EXISTS { ?item wdt:P96 ?x }
} ORDER BY ?id
```

---

## Session log

Append an entry after every major task. Format: `### YYYY-MM-DD — brief title`. Never delete entries.

---

### 2026-05-14 — Mobile responsiveness, dark design system, Wikibase date patching, CLAUDE.md

**Site work**
- Added `@media (max-width:767px)` block to `assets/verso.css` — global mobile rules (header grid, nav scroll, reading layout collapse).
- Created `assets/inverse.css` — dark surface design system for the 4 reading pages (richard-hunter, the-house, archive, about). Tokens: `--inv-bg:#1e1c1a`, `--inv-fg:#f3f1ec`, `--amber:#e4a47e`. Built-in breakpoints at 1100px and 760px.
- Replaced all 4 reading pages wholesale from a design handoff at `/Users/brandonpoole/Downloads/design_handoff_inverted_pages/`. Each now loads `verso.css` + `inverse.css`, has a 240px h1, and uses `.sec` grid sections.
- `browse.html` — added mobile tab-switch UI (List / Item / Record tabs). Shell collapses to single column on mobile. `switchMobileTab()` function manages `.mobile-active` class. Selecting an item on mobile auto-switches to the "image" pane.
- `index.html` — added mobile CSS inline (`hero-grid`, `lede-row`, `featured-band` stack to 1 column).

**Wikibase — date patching**
- Audited browse.html for undated items ("—" in year column). Found 18 items with only P83 (digitization date, not drawing date).
- Assigned year 2018 to 16 items (HH-A-75 through HH-A-90, Dining Room Schemes I–VIII + East Wing design dev).
- Assigned year 2020 to 2 items (HH-A-143, HH-A-144, East Wing Construction Fragments).
- Skipped HH-A-145 (orphan, no phase context).
- Also updated English descriptions from `"...;undated"` to `"...;2018"` / `"...;2020"`.
- QuickStatements proved unreliable (redirect issues). Wrote `scripts/patch_dates.py` to call MediaWiki API directly.
- Script updated to load bot credentials (`MyBot@my-bot`) from `~/Documents/hh-wikibase-migration/.env` automatically — no prompts.
- Patch confirmed working and run successfully.

**Key findings / gotchas**
- SPARQL GET requests return 0 results on this Wikibase.cloud instance due to URL encoding. Always use POST with `Content-Type: application/sparql-query`.
- P83 = date digitized (2026 scan dates). browse.html `firstDate()` reads P82 → P64 → P118, never P83. Items with only P83 show "—".
- QuickStatements at `/tools/quickstatements` has a redirect chain issue. Fall back to Python API scripts when QS fails.
- Bot username is `MyBot@my-bot` (Special:BotPasswords). Credentials in `.env`.

**Files changed this session**
`assets/verso.css`, `assets/inverse.css` (new), `index.html`, `richard-hunter.html`, `the-house.html`, `archive.html`, `about.html`, `browse.html`, `WIKIBASE.md` (new), `scripts/patch_dates.py` (new), `CLAUDE.md` (this file, new)

---

### 2026-05-14 — Project consolidation, launcher, persistent memory system

- All projects moved to `~/Projects/` — single consolidated location.
- Repo moved from `~/github/HunterHouse` to `~/Projects/HunterHouse`. Remote unchanged.
- `CLAUDE.md` updated with new local path and memory protocol instructions.
- `~/.zshrc` updated with `claude()` project picker function — 3 projects: Hunter House, HHRCS, Poole Portfolio.
- `CLAUDE.md` created for HHRCS (`~/Projects/HHRCS`) and Brandon-Poole (`~/Projects/Brandon-Poole`).
- Apposite Studio kept at `~/Projects/Apposite-Studio` as archived record — not in launcher.
- Deleted: `~/hhrcs_esp32` (no remote), `~/Documents/GitHub/brandonpoole` (emenel's repo), `~/ext4fuse`.
- Git push/add/commit confirmed already pre-authorised in Claude Code `settings.local.json`.

---

### 2026-05-14 — Splash entry page (v0.5) and view-transition patch

**Site work**
- Replaced `index.html` wholesale with the cinematic splash from `/Users/brandonpoole/Downloads/design_handoff_splash/`. The new page is a full-bleed film entry (Vimeo background loop, `v0.5` imprint, 56px title plate, animated "Enter →" cue). Click anywhere triggers a JS exit animation (JS + CSS), then navigates to `archive.html` at t=870ms.
- Patched `assets/inverse.css`: inserted the 7-line `@view-transition` block after `:root{}`. This opts the reading pages into cross-document View Transitions and assigns `view-transition-name:hh-mark` to `.markid` — enabling the browser-native morph of the title plate from splash centre to reading-page corner on Chrome/Edge 126+ and Safari TP.
- The four reading pages, `browse.html`, and `assets/verso.css` are untouched.

**Tech notes**
- Splash uses React 18.3.1 + @babel/standalone 7.29.0 (UMD CDN, SRI-pinned) for the Vimeo Film component. Same CDN pattern as existing site pages.
- Vimeo video ID: `1184581518`. Film fades in on `play`/`playing` postMessage from player, with a 2 s fallback.
- Cross-doc View Transitions are progressive enhancement — JS-only exit animation is the fallback for Safari/Firefox.
- To swap Vimeo for a self-hosted MP4: see README in the handoff bundle (`_reference_only/`) — replace `<Film>` component body with a `<video autoPlay loop muted playsInline>` element.

**Files changed**
`index.html` (replaced), `assets/inverse.css` (view-transition block added)
