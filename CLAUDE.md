# CLAUDE.md — Hunter House Foundation session context
# Live working memory. Full session history is rotated into frozen archives:
#   • CLAUDE_archive_v1.05.md — v1.03.00 → v1.05.02 (verbatim freeze, 2026-05-19)
#   • CLAUDE_archive_v1.02.md — through v1.02.18 (earlier freeze)
# The archives are read-only and consulted only for deep historical detail; git holds all of it too.

Load this file at the start of any Claude Code session.

---

## ⚑ Active working context — read FIRST, act accordingly

<!-- LINE-MARKER: the claude() launcher rewrites the next line. Keep it on its own line. -->
**LINE: NEXT**

- **LINE: NEXT** → all browse work goes in **`next.html`**. Do **not** edit `browse.html` except an explicit live hotfix (then mirror the change into `next.html`). Version label convention: `next.html`'s `VERSION` constant is `v1.05-test.NN` — bump `NN` on every push, note it in the session log. Promotion to live = the documented Staging workflow.
- **LINE: LIVE** → work directly in `browse.html`; normal `v1.MAJOR.SESSION.PATCH` convention applies. `next.html` is dormant.

At session start: announce which LINE is active and which file you'll be editing. If LINE and the user's stated intent disagree, ask before editing.

**Preview convention (standing):** any artifact Brandon needs to eyeball (PDF, image, export) is written to `~/Desktop` with a clear name and opened automatically — never left in a temp folder for him to hunt down.

---

## ⚑ Pending at next session start — prompt Brandon immediately

**v1.05 PROMOTED to live (2026-05-19).** `next.html` → `browse.html`; live is now **`v1.05.00`** (tagged). Staging line rolled forward — `next.html` is now **`v1.06-test.01`** (LINE: NEXT, all browse work continues there; `browse.html` is the stable public page again). Open threads carried into the v1.06 line:
- **A few small `next.html` tweaks** Brandon has queued (unspecified — ask him).
- **Held by** — P94 (CAA/FUL) vs P79 (HHC) ambiguity; needs a rule for which to write before it's editable.
- **Phase rename** — distinct from "change phase" (P62, done). Renaming edits the shared Phase item's label → affects every item in that phase. Needs a confirm-guard. (`wbsetlabel` on `item.phaseQID`.)
- **Built by / Designed by** (P140/P141) — 0 vocabulary exists; needs a person/org entity-search picker (not the in-use-vocab pattern).
- **GES collection ingest** — `GES_intake.xlsx` issued (~70 items: 35 Hunter furniture drawings + 35 photos of Gessinger's built furniture). When Brandon returns the filled sheet: mint phase items from the "Furniture piece / set" column, create any missing drawing-type items, flag rows missing the photographer ("Mary —") name, then generate the batch for confirmation. Generator: `scripts/make_ges_intake.py`.
- **Restart the edit proxy** each session: `python3 scripts/edit_proxy.py` (dies on Mac sleep; editing on `next.html` is inert without it; could be auto-wired into the `claude()` launcher later).
- **Housekeeping:** add `scripts/__pycache__/` to `.gitignore` (bytecode noise now untracked).
- Plus the long-standing **Wikidata items** and **RAD/archival-standards** items below (still deferred).

---

**P100 needs reassignment.** The "notes" property (P100) is no longer rendered in the record pane — curator notes were migrated to researcher notes (localStorage, BP). The property label and purpose should be reassigned to something more useful. Decide what P100 should become before next cataloguing session.

---

**Archival standards alignment — deferred.** The current cataloguing model uses ISAD(G) hierarchy loosely but is not formally RAD-compliant. Key gaps to revisit: (1) fonds-level item in Wikibase; (2) series level currently encodes physical custody (HHC/CAA) rather than creator function — decide whether to redefine or formally acknowledge as a custodial split; (3) Level of Description property (new P) needed for AtoM/LAC interoperability. Not urgent for current cataloguing work, but important before any academic write-up or cross-institutional integration.

---

**Wikidata items are ready to create.** Three items are drafted in `WIKIDATA_DRAFT.md`:
1. Richard Hunter (person)
2. Canadian Architectural Archives (institution)
3. Richard Hunter fonds

Brandon needs a free Wikimedia account — takes 2 minutes at `wikidata.org/wiki/Special:CreateAccount`. Once logged in, it's a QuickStatements copy-paste. After creation, add resulting Q-numbers to P139 on Q201 (Hunter) and Q116 (CAA) in our Wikibase.

**Prompt at session start:** "Ready to create your Wikimedia account and submit the three Wikidata items? It's a 5-minute job."

---

**PWA splash page** — reinstall needed on iPhone. The manifest already has `start_url: browse.html` but the old install is cached with index.html. Remove HH Archive from home screen and re-add from `bturep.github.io/HunterHouse/browse.html`.

---

**Rotation persistence — DECIDED (approach C: metadata now, bake later).** The viewer's T-key rotate is display-only. Brandon wants rotation to persist to the archive. Decision = hybrid:
- *Part 1 — **BUILT** (next.html v1.06-test.05, 2026-05-19):* property **P144 "display rotation"** (string; minted via new `scripts/mint_property.py`). next.html: SPARQL `OPTIONAL { ?item wdt:P144 ?rotation }` + `rotation` mapping; `renderImage` seeds `zoomState.rotation` from the stored value as the **base orientation** (fit/transpose logic already keyed off it). T stays casual (transient +90, writes nothing); an **admin-only `⤓ save`** control (`#zoom-rotsave` in the zoom bar, hidden unless admin AND rotated-off-base) writes the net via `setStringClaim` → P144 (create-then-remove; net 0 ⇒ clears the claim). Reversible. *Known v1 limit:* apply-at-render is **desktop image stage only** — the mobile sheet image + lightbox still show the unrotated file (deferred small follow-up; admin rotation is desktop-only anyway, and Part 2 bake fixes the bytes for all). *Caveat:* `index.html` prefetch lacks `?rotation` too → sync at promotion (see Staging note).
- *Part 2 (specced, later):* a maintenance "bake" script = `rotate_images.py` core driven by the `display rotation` claims — rotate master+3 tiers on R2, **then clear the claim**, then purge CDN. Explicit run only. Prerequisite: an automated Cloudflare cache-purge API token (not yet wired; `rotate_images.py` currently purges via dashboard).

---

**Curated mode / "exhibition lens" — Phase 1 BUILT (next.html v1.06-test.06).** A curator (artists/architects; first = Brandon Poole) authors a *selection* with a macro intro + per-item curator notes. It's a **mode/lens, not a filter**. Flow: pick a curator from the `[Curated]` list (top of BROWSE) → **curator threshold overlay** (about-pane-style `inset:0`, the gallery "title wall": a *standing* one-line "what is a curated lens" explainer [a `next.html` constant, shared across curators — NOT per-JSON] + curator bio + external link + **"Continue to exhibition" CTA**) → CTA **is** the confirm/commit (this overlay *replaces* the earlier dim-tags+separate-confirm step — net simplification) → filter pane collapses → list shows only that curation in the **curator's order** → right pane swaps researcher-notes for the **curator's note** → an intro card (the `#mark-bar` slot pattern, bigger: the curation's *macro argument* + **exit**) sits above the list. Esc also exits. Overlay = person + concept; card = content (keep separate). **Public-visible** (outreach/exhibition); only *editing* is gated. *Scope note:* the v1 overlay is a viewer-facing threshold only; a real **in-tool authoring tutorial** for invited curators belongs to Phase 2 (no in-browser authoring in v1). Decisions made:
- *Store (v1):* **static JSON** `curations/<slug>.json` `{curator{name,role,affiliation,qid,bio,url,url_label}, slug, title, intro, updated, items:[{id,pos,note}]}` + `curations/index.json` (curator chooser, forward-compat). (`curator.bio`/`url`/`url_label` feed the threshold overlay; `intro` is the card's macro argument.) Wikibase model (Curation = first-class item, membership + ordinal/curator-note qualifiers, reuses the phase/sibling arrangement pattern) is the **documented canonical target** for later (needs proxy `wbsetqualifier`).
- *Order (v1):* explicit integer `pos` per item (reuses the P86 "X of Y" mental model). In curation mode the ID/Phase/Year sort header is **locked/replaced ("Sequence")**; optional later "catalogue order" toggle.
- *Authoring (v1):* Brandon supplies ordered list + intro + per-item notes; the JSON is generated/committed (no in-browser curation editor in v1 — deferred). Any future bespoke exhibition `.html` consumes the same JSON (that's the contract).
- *Open at build:* intro text format (recommend plain w/ paragraph breaks); exact visual placement of `[Curated]`; search behaviour inside a curation; cache-busting the JSON (use `?v=`+VERSION). Curator-only role + in-browser authoring + multi-curator chooser = Phase 2.
- *Status: Phase 1 BUILT* (next.html v1.06-test.06). Seed `curations/index.json` + `curations/brandon-poole.json` (PLACEHOLDER content — real ids/intro/notes/bio/url pending from Brandon; swap-in needs **no rebuild**). `[Curated]` entry = `#curated-bar` above the filter panel (hidden if no curations / in-mode); threshold overlay `#curator-pane` (about-pane pattern, LENS_BLURB + bio + link + "Continue to exhibition"); `state.curation` drives an `applyFilters` early-return (authored membership, `pos` order, sort+filter locked with a toast); `#curation-card` intro card above the list with an **exit** button; record pane swaps `renderRN`→`renderCuratorNote`; mark-bar hidden in-mode. All gated behind `state.curation`/file presence (zero change when absent). *Deliberate v1 deviation:* Esc cancels the **threshold overlay** but does **not** exit an active curation (avoids clobbering Esc's zen/search/overlay duties) — leaving the lens is the always-visible card **exit** button. Revisit if Brandon wants Esc-to-exit.
- *Phase 2 (later):* in-browser curator authoring + the authoring tutorial, multi-curator polish, Wikibase promotion (Curation as first-class item w/ qualifiers; needs proxy `wbsetqualifier`), optional bespoke exhibition `.html` (consumes the same JSON).

---

## Memory protocol

1. **On load** — read this file before doing anything else.
2. **After each major task** — append a dated entry to the Session Log.
3. **Mid-session** — if something changes the general understanding, update the relevant section immediately.
4. **End of session** — consolidate, update version/status tables, write summary entry, commit and push.
5. **Never delete log entries.** Append only. Rotation = freeze a verbatim archive + condense here; the original is never destroyed (and git keeps every prior CLAUDE.md regardless).

---

## Project

A static GitHub Pages site + a live Wikibase cataloguing the architectural archive of Richard Morrow Hunter (1970–2020, 203 Goward Road, Saanich BC).

| | |
|---|---|
| Local path | `/Users/brandonpoole/Projects/HunterHouse` |
| GitHub | github.com/bturep/HunterHouse |
| Live site | https://bturep.github.io/HunterHouse/ |
| Wikibase | https://hunterhouse.wikibase.cloud |
| Deploy | push to `main` → live in ~30 s via GitHub Pages |

---

## Credentials

All credentials in `/Users/brandonpoole/Documents/hh-wikibase-migration/.env`.

```
WIKIBASE_BOT_USER=MyBot@my-bot
WIKIBASE_BOT_PASSWORD=<in .env>
R2_PUBLIC_BASE=https://archive.hunterhousefoundation.com
```

Bot has full write access. All scripts load credentials from `.env` automatically.

---

## Repo structure

```
HunterHouse/
├── index.html              Splash — full-bleed MP4 entry, navigates to browse.html
├── richard-hunter.html     Biography + chronology
├── the-house.html          Narrative on the residence
├── archive.html            How the catalogue is organised
├── about.html              Mandate, people, contact
├── browse.html             Live archive browser — SPARQL, filter, search
├── next.html               Staging copy of browse.html (v1.06-test.NN)
├── assets/
│   ├── verso.css           Light design system (all pages)
│   └── inverse.css         Dark design system (4 reading pages only)
├── scripts/                Batch Wikibase + R2 scripts (see Scripts table)
├── curations/              Curated-lens JSON (index.json + <slug>.json) — Phase 1 seed
├── WIKIBASE.md             Full property table, QIDs, SPARQL templates
├── WIKIDATA_DRAFT.md       Draft QuickStatements for 3 Wikidata items (not yet submitted)
├── CLAUDE_archive_v1.05.md Frozen full session log v1.03.00 → v1.05.02
└── CLAUDE_archive_v1.02.md Frozen full session log through v1.02
```

---

## Design system

Two CSS surfaces:
- `verso.css` — light (ink on paper). All pages, especially header.
- `inverse.css` — dark (cream on near-black). 4 reading pages only.

**Key tokens — verso.css**
```css
--ink:#1e1c1a; --muted:#76726a; --hint:#a8a59c;
--rule:#d6d2c8; --rule-soft:#e3dfd5; --soft:#ebe8df;
--bg:#f3f1ec; --red:#8b3a2a; --copper:#4f7a6b;
```
Dark mode (`html.dark`) overrides: `--ink:#f0ede6`, `--bg:#1a1816`, `--soft:#26231e`, etc.

**Dark mode toggle**: `html.dark` class via `localStorage['hhf_theme_v2']`. Default is dark.

---

## browse.html — current architecture

### Shell layout
```
.site-top  (41px header bar)
.shell (flex row):
  .panel-left  (28%, collapses to 41px)  ← list pane + handle
  .pane-image  (flex:1)                  ← image stage + foot
  .panel-right (28%, collapses to 41px)  ← record pane + handle
```

**Panel collapse**: `.panel-left.out` / `.panel-right.out` sets `width:41px`. Edge handle (`.panel-handle`) is `position:absolute`, protrudes 5px into image area. Content hidden via `max-width:0` on `.panel-content` when `.out`. `togglePanel(side)` toggles the class. (Note: `#info-pane` is a direct child of `#panel-right` — collapse rule for it is `.panel-right.out #info-pane{display:none}`, added v1.05.01.)

**Loading state**: `body.loading` applies `visibility:hidden` to list/rows/meta/foot. During loading, `.image-foot` overrides to `background:var(--soft)` (blends with viewer). Once data populates the `loading` class is removed.

### Image tiers (R2)
Three tiers per item:
- `_thumb.jpg` — 600px, 75% quality (shown first while loading)
- `_prev.jpg` — 2000px, 82% quality
- `_large.jpg` — 3840px, 85% quality (used as full-res download tier)

`renderImage()` loads thumb + large simultaneously; thumb shows first, large fades in over it.

### Key JS patterns
| Pattern | Detail |
|---|---|
| VERSION constant | The single source of truth — **must be bumped on every push**. `CACHE_KEY` derives from the full `VERSION`. `VERSION_DISPLAY` (added v1.05.02) strips the patch for the four public display points unless the label contains `-test` (staging shows the full label). |
| Dark mode | `html.dark` + `localStorage['hhf_theme_v2']` |
| SPARQL | GET with `encodeURIComponent` in browser; POST in Python scripts |
| Roles | `rnRole()` → `"admin"|"research"|"public"`; `canEditWikibase()` = admin; `canMark()` = not public. Single gate = the researcher-notes unlock. Desktop only; mobile read-only. |
| Researcher notes | `localStorage["hhf_rn"]` keyed by archive ID, name→pin auth. Registry `RPINS = { "203BTP": { name:"Brandon Poole", initials:"BP", qid:null, role:"admin" } }`. Notes are **private** (viewer-aware `rnVisibleNotes`; admin `[mine]`/`[all]` toggle). |
| Row flags | Per-researcher persistent: `hhf_marks` / `hhf_seen` keyed by pin, plus note-dot following `hhf_rn`. Researcher-only `.row-flags` register under the ID (mark / seen / note). |
| Admin inline edit | Click-to-edit on the record pane → `proxyEdit()` → local `scripts/edit_proxy.py` → Wikibase. Create-then-remove claim safety; optimistic state update. |
| Filter badge | Bracket style `[#]` (`::before "[" / ::after "]"`, no border/bg). |
| Data footer | Wikibase / SPARQL / JSON links at bottom of record pane (`margin-top:auto`). |

### Mobile
`@media (max-width:767px)`: shell collapses to column, three tabs (List / Item / Record), panels full-width, handles hidden. `switchMobileTab(pane)` manages `.mobile-active`. Bottom sheet with unified swipe pipeline. Mobile is **read-only** (researcher/admin tooling is desktop only).

### SPARQL query
browse.html fetches: P2 archId, P96 img, rdfs:label, P95 master, P82/P64/P118 dates, P62 phase, P84 phase2, P88 drawType, P87 area, P1 itype, P79 src, P80 creator, P140 builtBy, P141 designedBy, P89 use, P92 builtStatus, P86 setPos, P100 notes, P93 rights, P94 heldBy, P99 archiveLink, P142 location. (P91 medium removed v1.03.47.)

`firstDate()` reads P82 → P64 → P118. Never P83 (digitization date = 2026). `collectionOf(item) = item.heldBy || item.sourceCollection` (HHC carries collection via P79 only).

---

## Wikibase quick reference

See `WIKIBASE.md` for full property table, QIDs, and SPARQL templates.

### Most-used properties
| PID | Label | Notes |
|---|---|---|
| P1 | instance of | Q88=drawing, Q2=phase |
| P2 | HH archive ID | `HH-HHC-####` / `HH-CAA-####` format |
| P62 | part of | project phase QID |
| P79 | source collection | Q180=HHC, Q116=CAA |
| P80 | creator | Q201=Richard Hunter |
| P82 | date created | year precision `/9` |
| P88 | drawing type | Q98=plan, Q99=elevation, etc. |
| P91 | medium | string, e.g. "Pencil on vellum" (no longer in browse SPARQL) |
| P96 | preview image | URL — required for browse.html |
| P97 | legacy ID | old HH-A-XXXX IDs saved here |
| P99 | archive link | AtoM item-level URL (CAA items) |
| P100 | notes | curator prose (no longer rendered — slated for reassignment) |
| P139 | Wikidata QID | external-id, not yet populated |
| P142 | Physical location | archival path, e.g. "S0004, SS0001, SSS0018, FL0003" |
| P143 | access copy | URL — publication PDF; drives the browse/next PDF reader (created 2026-05-19) |
| P144 | display rotation | String — `90`/`180`/`270` CW; applied at render (desktop stage); created 2026-05-19 |

Next available IDs: **HH-HHC-0116**, **HH-CAA-0036**. (HH-HHC-0115 = Q490, the 1986 Hunter portfolio publication.)

### Wikibase editing
- **Small (1–5 items):** QuickStatements at `/tools/quickstatements` — sometimes unreliable (redirect issue), fall back to Python script.
- **Bulk:** Python script modelled on `scripts/patch_dates.py`. Login flow: GET logintoken → POST login → GET csrftoken → write.
- **Admin inline (browse/next.html, v1.05):** click-to-edit on the record pane → local edit proxy (`scripts/edit_proxy.py`, must be running) → Wikibase API. Desktop + admin role only.
- **SPARQL:** browser at `hunterhouse.wikibase.cloud/query`, or POST in Python (`Content-Type: application/sparql-query`). GET with URL encoding fails in Python.

---

## Image pipeline — Cloudflare R2

`rclone` remote: `hh-r2:hunter-house-archive`. Credentials in `.env`.

```bash
rclone ls hh-r2:hunter-house-archive              # list bucket
rclone copy local.jpg hh-r2:hunter-house-archive  # upload
```

Filename convention: `HH-HHC-0044_Label_Date_prev.jpg` (preview), `_thumb.jpg`, `_large.jpg`.

R2 folder structure per collection:
```
hunter-house-collection/    masters/ previews/ thumbs/ large/
canadian-architecture-archive/  masters/ previews/ thumbs/ large/
```

Script: `scripts/regen_previews.py` — flags `--thumb` (600px), none (2000px), `--large` (3840px).

---

## Batch change protocol (summary)

For any bulk P2/P96/P95 change: (1) export SPARQL snapshot to `data/snapshots/`, (2) create branch, (3) write mapping TSV, (4) write P97 legacy ID before changing P2, (5) R2 copy to new name (don't delete old), (6) update Wikibase, (7) verify, (8) delete old R2 files, (9) merge + tag.

Full protocol in `CLAUDE_archive_v1.02.md` §"Batch change protocol".

**Completed migrations:**
- HH-A-XXXX → HH-HHC-XXXX / HH-CAA-XXXX — COMPLETE 2026-05-14
- HH-HHC-0036–0149 → HH-HHC-0001–0114 — COMPLETE 2026-05-14
- R2 cleanup (510 stale files deleted) — COMPLETE 2026-05-14
- P142 migration from P100 — COMPLETE 2026-05-15

---

## Scripts

| Script | Purpose | Status |
|---|---|---|
| `scripts/patch_dates.py` | Add P82 date claims + update descriptions | Active |
| `scripts/regen_previews.py` | Regen preview/thumb/large images from TIF masters | Active |
| `scripts/clean_titles.py` | Strip/rewrite bracketed annotations from item labels | Active |
| `scripts/strip_counter_brackets.py` | Remove [N/N] counter patterns from labels | Active |
| `scripts/edit_proxy.py` | Local admin Wikibase write proxy (localhost:8731, bot creds server-side) | Active |
| `scripts/make_ges_intake.py` | Generate the GES collection intake workbook | Active |
| `scripts/ingest_publication.py` | Ingest a multi-page publication (masters byte-for-byte + SHA-256 manifest + cover tiers + access PDF → R2; create the Wikibase item). Dry-run default; `--execute` to write | Active |
| `scripts/mint_property.py` | Mint (or find, idempotent) one Wikibase property: `--label --desc --datatype` | Active |
| `scripts/rename_ids.py` | HH-A → HH-HHC/CAA rename | Complete |
| `scripts/renumber_hhc.py` | HHC renumber 0036–0149 → 0001–0114 | Complete |
| `scripts/migrate_p142_location.py` | Move archival paths P100 → P142 | Complete |
| `scripts/fix_p142_prose.py` | Fix P142 values with mixed prose | Complete |
| `scripts/fill_p142_missing.py` | Fill P142 for 15 CAA items | Complete |
| `scripts/rotate_images.py` | One-time R2 image rotation batch (17 items) | Complete |

(Completed one-time migration scripts also live in `scripts/archived/`.)

---

## Cataloguing status (May 2026)

| Collection | Catalogued | Images | Notes |
|---|---|---|---|
| HHC | ~114 items | partial (3 tiers) | Primary collection |
| CAA | 35 items | partial (3 tiers) | All have P142. Drawings + photos. |
| FUL | 9 items | partial | Fulker photographs |
| GES | 0 | none | Furniture drawings; intake sheet issued, pending return |
| FRH | 0 | none | Frances Hunter materials; pending |
| IVH | 0 | none | Ivan Hunter photographs; pending |

browse.html shows ~150 items (those with P2 + P96).

---

## Common tasks

### Add date (QuickStatements)
```
Q###|P82|+1992-00-00T00:00:00Z/9
```

### Create new archive item (QuickStatements)
```
CREATE
LAST|Len|"Label here"
LAST|Den|"architectural drawing; HHC; 1992"
LAST|P1|Q88
LAST|P2|"HH-HHC-0115"
LAST|P79|Q180
LAST|P80|Q201
LAST|P82|+1992-00-00T00:00:00Z/9
LAST|P62|Q###
LAST|P88|Q99
LAST|P96|"https://archive.hunterhousefoundation.com/hunter-house-collection/previews/HH-HHC-0115_Label_Date_prev.jpg"
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

### Find items missing preview image (SPARQL)
```sparql
SELECT ?item ?id WHERE {
  ?item wdt:P2 ?id .
  FILTER NOT EXISTS { ?item wdt:P96 ?x }
} ORDER BY ?id
```

---

## CCA Digital Archives reference (condensed)

CCA's ISAD(G) hierarchy maps directly to our Wikibase: fonds = Richard Hunter fonds, series = collection (P79), file = project phase (P62), item = archive item. Core principle: invest description effort at the file/phase level, not the individual item. P100 notes and phase labels are the right level. Full notes in `CLAUDE_archive_v1.02.md`.

---

## Version history (milestones)

| Version | Date | Notes |
|---|---|---|
| v1.01.00 | 2026-05-14 | Three-level versioning adopted; mobile responsiveness; dark design system; Wikibase date patching |
| v1.02.00 | 2026-05-15 | Full session 02: splash redesign, P142, progressive loading, 3840px tiers, researcher notes, dim border system, typography consolidation |
| v1.02.18 | 2026-05-15 | Image foot overhaul, large previews, browse.html refactor (−65 lines) |
| v1.03.00 | 2026-05-15 | Collapsible panels, mark feature, filter badge fix, loading-phase foot colour |
| v1.03.01 | 2026-05-16 | Mobile bottom sheet: Google Maps layout, full record sections, lightbox |
| v1.03.08 | 2026-05-16 | Image rotation batch job (17 items on R2); about card text size; PWA full-screen fix |
| v1.03.28 | 2026-05-16 | Mobile list-head alignment; portrait lock; white flash fixes; splash removed from PWA |
| v1.04.00 | 2026-05-16 | UI colour overhaul; about pane redesign; filter system; data fixes; CSS audit |
| v1.04.02 | 2026-05-17 | Panel↔fullscreen interlink fix; mobile sheet swipe nav (last live build before v1.05) |
| v1.05.00 | 2026-05-19 | **Promotion of the full v1.05 line.** Role system (Admin/Research/Public), local edit proxy, admin inline Wikibase editing (title, date, phase, item type, built, drawing type, areas), mark/seen/note row flags, info panel, keyboard scheme, filter & About typography parity. `next.html` → `browse.html`. |
| v1.05.02 | 2026-05-19 | Live hotfixes on the v1.05 line: info panel hidden when right panel collapsed; public version display drops the patch number. |

Tags pushed: `v1.01.00` (fc98905), `v1.02.00` (2059cb7), `v1.02.18` (82065e6), `v1.03.00`, `v1.03.01`, `v1.03.08`, `v1.04.00` (prior sessions), `v1.05.00` (2026-05-19 — v1.05 promotion).

Full per-version detail: `CLAUDE_archive_v1.05.md` (v1.03→v1.05), `CLAUDE_archive_v1.02.md` (≤v1.02).

---

## Staging / test page

A live-stable + parallel-test setup, zero extra infrastructure (plain GitHub Pages serves only `main`, so a git branch is **not** a separate URL — a duplicate file is).

| | |
|---|---|
| **Live** | `browse.html` → https://bturep.github.io/HunterHouse/browse.html — never edited during development; the stable public page |
| **Staging** | `next.html` → https://bturep.github.io/HunterHouse/next.html — the work-in-progress copy; break/iterate freely |

- Both files live on `main` (the only branch Pages serves). Pushing `next.html` redeploys the site but `browse.html` is untouched, so **live visitors are unaffected**.
- `next.html` carries `const VERSION = "v1.06-test.NN"` → its `CACHE_KEY` (`hhf_v1.06-test.NN`) is isolated from live (`hhf_v1.05.02`); the on-screen version shows which build you're on.
- `next.html` must stay in the **repo root** (relative `assets/…` paths). It links the shared `assets/verso.css` — inline `<style>` changes are isolated, but `verso.css` edits would leak to live. Fork to `assets/verso.next.css` only when a task needs CSS changes.
- `index.html` splash + the manifest `start_url` still point at `browse.html`; the installed PWA shows live. Test the new version in the **phone browser** at the `next.html` URL. `next.html` opened directly skips index.html's SPARQL prefetch (just a slightly slower first load — fine).

**Promotion (staging → live), when a version is ready:**
1. `cp next.html browse.html`
2. In `browse.html`, set `VERSION` to the real version (e.g. `v1.05`); update the session log.
3. (If `verso.css` was forked) `cp assets/verso.next.css assets/verso.css`.
4. Commit, `git tag v1.05.00 && git push --tags`, push. Live is now the new version.
5. Re-sync `next.html` from the new `browse.html` for the next cycle.

**⚠ Prefetch-sync at promotion:** if `next.html`'s `CATALOGUE_QUERY` changed since the last promotion, also sync `index.html`'s prefetch copy of that query. As of v1.06-test.05 it gained `?accessCopy` + `OPTIONAL{?item wdt:P143 ?accessCopy}` (PDF reader) **and** `?rotation` + `OPTIONAL{?item wdt:P144 ?rotation}` (display rotation). `cp next.html browse.html` carries them into `browse.html`, but `index.html` holds a *separate* copy — unsynced, the PDF "Read" affordance and stored rotation are dark for visitors who enter via the splash prefetch. (A code comment in next.html flags this too.)

**Hotfixing live mid-cycle:** edit `browse.html` directly, push (deploys live immediately). Then port the same change into `next.html` so it isn't lost at next promotion.

---

## Session log

> Entries below the v1.05 promotion are **digested**. Full verbatim per-version detail
> is frozen in `CLAUDE_archive_v1.05.md` (v1.03→v1.05) and `CLAUDE_archive_v1.02.md`
> (≤v1.02). The v1.05 promotion and its live hotfixes are kept in full as current
> live-state context. Never delete entries — append; rotate by freezing an archive.

---

### Sessions 01–02 — condensed (≤ v1.02.18)

Full log in `CLAUDE_archive_v1.02.md`. Built the full mobile-responsive design system (verso.css, inverse.css, 4 reading pages); splash redesigned to system monospace + self-hosted MP4 (no render-blocking deps); browse.html three-pane shell with progressive image loading, zoom/pan/rotate, researcher notes, dark mode, filter system, pill colour themes, typography consolidation, dim border system. Wikibase: 149 items renamed (HH-A → HH-HHC/CAA), 114 HHC renumbered, P91/P99/P142 written for CAA, P139 created. Image pipeline: all 145 items have 3 R2 tiers. WIKIDATA_DRAFT.md drafted (not submitted).

---

### v1.03.00 → v1.04.02 — condensed (2026-05-15 → 2026-05-17)

Full per-version detail in `CLAUDE_archive_v1.05.md`. The v1.03/v1.04 line on `browse.html`:

- **v1.03.00** — independently collapsible left/right panels (41px, edge `.panel-handle`); quiet data footer (`margin-top:auto`); session-only **mark feature** (M key, `marked` Set, `.row.marked::after` dot); filter badge → filled pill; loading-phase image-foot blends with viewer.
- **v1.03.01–v1.03.08** — mobile **bottom sheet** rebuilt: fixed 72vh floating panel, `item.image` (not `.img`) display fix, `min-height:0` scroll fix, full record sections with tappable siblings, lightbox. PWA icons recolored; manifest `short_name` → "HH Archive". **Image rotation batch** — `scripts/rotate_images.py` rotated 17 items (master TIF + 3 tiers) on R2; CDN cache purged. PWA full-screen specificity fix.
- **v1.03.21–v1.03.28** — mobile list-head alignment, portrait lock (manifest + CSS overlay + `screen.orientation.lock`), white-flash reduction (early `<style>` bg, `theme-color`/`color-scheme` metas). Splash folded into browse.html then removed entirely — PWA opens straight to the list; index.html stays as the web landing page only.
- **v1.04.00** — **UI colour overhaul**: all pill backgrounds removed → bracket-style text (`[Area]`, `[D]`), seven desaturated colour themes; type badge `.tmark` bracketed; phase stripped of interactive status (plain text, sortable only). About pane → full image-area takeover; CCA/CAA disambiguation fixed with external links. Collection filter (HHC/CAA/FUL) wired. `collectionOf()` helper fixes HHC "Held by" (P79 vs P94). P91 medium removed. Loading screen centering/background fixed. 6 dead CSS classes removed; 10 migration scripts → `scripts/archived/`. Graph current-item colour cascade fix.
- **v1.04.01–v1.04.02** — Wikibase **Main Page** reframed (biography → technical data-model entry point; continuity record `WIKIBASE_MAINPAGE.md`; org steward = Q187, CAA repo = Q178). Panel ↔ bottom-bar fullscreen interlink fix (`.out` class = single source of truth, `syncFsBtn()`). Mobile sheet **swipe navigation** (unified gesture pipeline, axis-lock; horizontal = adjacent item, vertical = open/close; pushed live as v1.04.02). Then: **Staging system established** (v1.04.03–04) — `next.html` created, Staging/promotion workflow documented, **⚑ Active-context `LINE:` marker** added, `claude()` launcher reworked to auto-stay on `main` and prompt LIVE/NEXT.

Live line ended this era at **v1.04.02**.

---

### v1.05 development line — condensed (2026-05-17 → 2026-05-18, next.html v1.05-test.01 → .28)

Full per-test-version detail in `CLAUDE_archive_v1.05.md`. The entire v1.05 line was built and tested on `next.html` only; `browse.html` stayed at v1.04.02 throughout. Goal: admin (Brandon) inline Wikibase editing + researcher tooling, **desktop only**, gated by the researcher-notes unlock.

- **Role system (Slices 1–2)** — `RPINS` entries gain `role`; Brandon = `admin`. `rnRole()` → admin/research/public; `canEditWikibase()` = admin. Single gate = researcher unlock. **Local edit proxy** chosen as backend: `scripts/edit_proxy.py` holds bot creds server-side, localhost:8731 only, admin-secret guarded, CORS-limited, allowlisted Wikibase write set, auto re-login. Runs only on Brandon's Mac while open (dies on sleep — restart each session).
- **Admin inline editing (Slices 3a–3d)** — click-to-edit on the desktop record pane → `proxyEdit()` → proxy → Wikibase, with optimistic state update, toast, and **create-then-remove** claim safety (a failed write never empties a field). Editable set: **Title** (`wbsetlabel`), **Date** (`YYYY-MM-DD`, precision 9/10/11), **Phase** (P62), **Item type** (P1), **Built** (P92) via property-scoped vocabulary pickers; **Drawing type** (P88) + **Areas** (P87) as multi-value chips popovers. Editable rows always render for admin (placeholder `—`). Edits hit the **real live Wikibase** (revision history = undo). Confirmed working by Brandon. Parked: Held-by (P94/P79 ambiguity), phase **rename**, person/org search for Built/Designed-by.
- **Researcher row flags (test.12 → .28)** — three per-researcher, persistent, desktop-only capabilities mirroring the notes infra (`hhf_marks` / `hhf_seen` / `hhf_rn`, keyed by pin): **Mark** (M, orange), **Seen/reviewed** (R, eye), **Note dot** (follows `hhf_rn`). Iterated heavily on the row-flag register (final: a compact left-aligned `.row-flags` cluster under the ID, three `.rf-slot` cells with two interior rules, researcher-only). **Marked bar** (`#mark-bar`, only/export/hold-to-clear). **Notes made private** (`rnVisibleNotes` viewer-aware; admin `[mine]`/`[all]` toggle). **Info panel** (`[?]` / `#info-pane`, role-aware, overlays the record panel). **Keyboard scheme**: `/` search, F fit, T turn, Z/↵ zen, =/− zoom, 1 1:1, M mark, R reviewed, ? info, Esc close/exit-zen, ↑/↓ nav (all gated by `!inInput`). Filter chips + About typography brought to parity with record-pane pills (bracket style, mono 11px). Several scope/stuck-filter bugfixes along the way.

Staging line ended this era at **next.html v1.05-test.28**, ready for promotion.

---

### 2026-05-19 — v1.05 promoted to live; v1.06 staging line opened (browse.html v1.05.00 · next.html v1.06-test.01)

**Promotion (documented Staging → Live cycle).** The full v1.05 line — built and tested entirely on `next.html` across v1.05-test.01→28 — went live.
- `cp next.html browse.html`; `browse.html` `VERSION` → **`v1.05.00`**. No `verso.css` fork existed (all v1.05 CSS was inline `<style>` in next.html), so step 3 was correctly skipped. Verified `browse.html` and `next.html` are byte-identical except the single `VERSION` line; script tags balanced; no hardcoded version literals (single source of truth = the `const VERSION` line; all four display points read it).
- `CACHE_KEY` auto-derives `hhf_` + VERSION → live cache breaks cleanly from `hhf_v1.04` to `hhf_v1.05.00`. Researcher data (`hhf_rn`, `hhf_marks`, `hhf_seen`) uses stable, non-versioned keys — **no user data wiped** by the bump.
- `next.html` `VERSION` → **`v1.06-test.01`**, opening the v1.06 staging cycle. Content identical to the new live; only the label rebranded (the "re-sync next.html" step). LINE stays **NEXT**.
- Committed in two commits: the promotion (tagged `v1.05.00`, pushed with `--tags`) then the next.html roll-forward. Version-history table, "Tags pushed" line, Staging-section CACHE_KEY example, and the Pending block all updated; global `~/.claude/CLAUDE.md` "Current versions" table bumped to v1.05.00.

**What is now live on the public site (v1.05.00):** role system (Admin/Research/Public via the researcher unlock; Brandon = admin), the local edit proxy path for admin inline Wikibase editing (title, date, phase, item type, built, drawing type, areas — desktop only, proxy must be running locally), per-researcher persistent mark/seen/note row flags, the marked bar, the `[?]` info panel, the full keyboard scheme, and the filter/About typography-parity polish.

**Versioning note.** This is the SESSION-level promotion milestone for the v1.05 line; tagged `v1.05.00` (not a MAJOR bump, so no GitHub Release per the snapshot rule — git tag only). Per Brandon's standing note: version numbers are convention; git is the real tracking.

**Also this session:** issued `GES_intake.xlsx` (Eric Gessinger Collection intake workbook — ~70 stub rows: 35 Hunter furniture drawings + 35 photos of Gessinger's built furniture, photographer "Mary —" left as a fill-in, free-text "Furniture piece / set" → phase at batch time). Generator `scripts/make_ges_intake.py`. Workbook + generator + `swatches.html` left untracked (working data, not committed in the promotion).

**Version: browse.html `v1.05.00` (LIVE, tagged) · next.html `v1.06-test.01` (staging).**

**Live hotfix — info panel hidden when right panel collapsed (browse.html v1.05.01 · next.html v1.06-test.02).** Bug: `#info-pane` is `position:absolute;inset:0` and sits as a direct child of `#panel-right`, a *sibling* of `.panel-content`. The collapse rule `.panel-right.out .panel-content{max-width:0}` only hides the content div, not the overlay — so collapsing the right pane while the info panel was open squeezed its text into the 41px strip instead of showing the blank collapsed sidebar. Fix: one CSS rule `.panel-right.out #info-pane{display:none}` (specificity 1·2·0 beats `#info-pane.open` 1·1·0, so it wins while collapsed and yields back on re-expand). CSS-only, covers every collapse path (edge handle, zen/Z, fullscreen button), no JS. Edited `browse.html` directly per the live-hotfix protocol, mirrored into `next.html` so it survives the next promotion; files remain byte-identical except VERSION. Behaviour note: if the info panel was open, collapsing hides it and re-expanding restores it (not dismissed) — acceptable; a "collapse fully dismisses it" variant is a possible later tweak on the v1.06 line.

**Version: browse.html `v1.05.01` (LIVE) · next.html `v1.06-test.02` (staging).**

**Display-version rule — public shows `vMAJOR.SESSION`, staging shows full (browse.html v1.05.02 · next.html v1.06-test.03).** Brandon: live should only ever read `vX.XX` (no patch number); staging should show the whole label. Added `VERSION_DISPLAY` next to the `VERSION` constant: `/-test/.test(VERSION) ? VERSION : VERSION.replace(/^(v\d+\.\d+).*$/,"$1")`. The four UI display points (topright, ap-ver, mob-about-ver, HHFA mobile button) now read `VERSION_DISPLAY`; `CACHE_KEY` still uses the full `VERSION`, so per-patch cache busting is unchanged. Derivation is identical code in both files — browse.html (`v1.05.02`, no `-test`) renders `v1.05`; next.html (`v1.06-test.03`, has `-test`) renders the full label. Files remain byte-identical except the VERSION line. Verified: `v1.05.02→v1.05`, `v1.05→v1.05`, `v1.06-test.03→v1.06-test.03`, `v2.00.00→v2.00`.

**Version: browse.html `v1.05.02` (LIVE, displays `v1.05`) · next.html `v1.06-test.03` (staging).**

---

### 2026-05-19 — working memory rotated (CLAUDE_archive_v1.05.md frozen)

Working memory compacted. The full `CLAUDE.md` at v1.05.02 / next.html v1.06-test.03 was frozen verbatim to **`CLAUDE_archive_v1.05.md`** (read-only FROZEN banner added; covers v1.03.00 → v1.05.02). This file rewritten: every living-reference section + the ⚑ Active-context marker (and the `LINE-MARKER` launcher comment) + the full ⚑ Pending block carried forward intact; only the session log rotated — v1.03→v1.04.02 and the v1.05-test.01→.28 line collapsed to two digest sections, the v1.05.00/.01/.02 promotion-and-hotfix entries kept in full as current live-state context. Strategy: log rotation with a frozen, non-editable snapshot (the project's own v1.02 precedent, refined with an explicit FROZEN banner so the two files can't drift); git retains all detail regardless. No code or version change — `browse.html` v1.05.02 and `next.html` v1.06-test.03 untouched. LINE stays **NEXT**.

---

### 2026-05-19 — first publication ingested + in-browser PDF reader (next.html v1.06-test.04)

Working LINE: **NEXT**. First multi-page **publication** added to the archive and a PDF reader built to view it. Live `browse.html` untouched.

- **Ingest — `HH-HHC-0115` = `Q490`** ("Richard Hunter Architect — Portfolio (1986, self-published)"). New script **`scripts/ingest_publication.py`** (model: one item, 10 pages as an internal sequence; dry-run default with the preview PDF auto-opened on the Desktop per the standing convention; `--execute` writes). Uploaded **byte-for-byte**: 10 master TIFs (~2.04 GB) → `hunter-house-collection/masters/HH-HHC-0115/HH-HHC-0115_p01..p10.tif`, a **SHA-256 fixity manifest** (new preservation habit), the 3 cover tiers from the title page, and a 6.3 MB 10-page access PDF → `…/pdf/`. A page-order bug (the un-numbered cover sorting last because `1986.tif` ends in 4 digits) was caught in the dry-run and fixed (longest-common-prefix ordering) before anything uploaded. New Wikibase property **P143 "access copy" (url)** minted by the script; `Q490` carries P1=Q91(publication)/P2/P79=Q180/P80=Q201/P82=1986/P96/P143. Verified: all R2 objects 200 (PDF `application/pdf` 6.3 MB; master p01 = 204,454,670 B = source-exact); Q490 claims complete. WIKIBASE.md table filled (P139/P142/P143); next HHC ID → **0116**.
- **PDF reader (`next.html`).** `OPTIONAL { ?item wdt:${ACCESS_PID} ?accessCopy }` (`ACCESS_PID="P143"`) + mapping. Desktop: a bracket-style `[ Read publication (PDF) ]` affordance under the record title opens `#pdf-pane` — a native-browser `<iframe>` overlay on the image area (same pattern as `#about-pane`/`#info-pane`), with title + `↓ PDF` link + ×/Esc (frame blanked on close). Mobile: a plain `Open publication (PDF) ↗` new-tab link (iframed PDFs are unreliable on iOS). Zero effect on non-publication items (affordance only renders when `accessCopy` exists). All inline JS passes `node --check`. **Known follow-up:** `index.html`'s prefetch `CATALOGUE_QUERY` is *not* synced — deliberately deferred to promotion (flagged in a next.html comment + the Staging checklist); harmless until then (the OPTIONAL is backward-compatible; live `browse.html` unaffected).
- **Also this session (design only, captured in Pending):** rotation persistence decided as hybrid **C** (metadata now → bake later); **Curated mode / exhibition lens** designed (static-JSON store, numeric order, gallery "title-wall" threshold overlay whose "Continue to exhibition" CTA is the confirm). Both queued behind this commit. Standing **preview convention** added (artifacts → `~/Desktop`, auto-opened). Edit proxy restarted this session.

**Version: next.html `v1.06-test.04`** (staging). Live `browse.html` unchanged at `v1.05.02`.

---

### 2026-05-19 — rotation persistence Part 1 (next.html v1.06-test.05)

Working LINE: **NEXT**. Approach-C Part 1 built (metadata layer). Live `browse.html` untouched.

- **Property P144 "display rotation"** (string) minted via new reusable **`scripts/mint_property.py`** (`--label/--desc/--datatype`, idempotent — exact-label match reused).
- **`next.html`:** `ROTATE_PID="P144"`; SPARQL `OPTIONAL { ?item wdt:P144 ?rotation }` + `?rotation` SELECT + `rotation` mapping (normalised int, 0/90/180/270). `renderImage` seeds `zoomState.rotation` from the stored value as the **base orientation** instead of always 0 (the existing fit/`constrainPan` transpose logic already keys off `zoomState.rotation % 180`, so 90/270 fits correctly). The **T key stays casual** (transient +90, no write). New **admin-only `#zoom-rotsave` ("⤓ save")** control in the zoom bar — hidden unless `canEditWikibase()` AND the displayed rotation differs from stored; click → `setStringClaim(qid, P144, net)` (new helper, create-then-remove; `net===0` ⇒ clears the claim) → updates `state.items` rotation → toast. Reversible by definition. All inline JS passes `node --check`.
- **Known v1 limitation (logged, not hidden):** apply-at-render covers the **desktop image stage only**. The mobile sheet image and the lightbox still display the unrotated file — a deferred small follow-up (admin rotation is desktop-only regardless; Part 2's bake pass fixes the actual bytes for every consumer). **Part 2** (bake script + Cloudflare purge token) remains specced/queued.
- Unrelated, ongoing: a background poller is still waiting on the Wikibase Cloud SPARQL index to pick up `HH-HHC-0115`/P143 (query-service propagation lag — code/data verified correct; not a bug).

**Version: next.html `v1.06-test.05`** (staging). Live `browse.html` unchanged at `v1.05.02`.

---

### 2026-05-19 — Curated mode / exhibition lens, Phase 1 (next.html v1.06-test.06)

Working LINE: **NEXT**. Built the full curated-lens *viewing* mode (no in-browser authoring — that's Phase 2). Live `browse.html` untouched.

- **Store:** new `curations/` dir — `index.json` (lens chooser) + `brandon-poole.json` (PLACEHOLDER content: real archive ids `HH-HHC-0001/0010/0050`, `HH-CAA-0001/0010` so the lens visibly works; Brandon replaces title/intro/per-item notes/bio/url — **no rebuild needed**, just edit the JSON & push).
- **next.html (all gated behind `state.curation` / file presence — zero behaviour change when absent):** `loadCurationIndex()` on boot; `#curated-bar` `[Curated]` entry above the filter panel; threshold overlay `#curator-pane` (about-pane overlay pattern — standing `LENS_BLURB` + curator name/role/affiliation + bio + external link + **"Continue to exhibition →"** = the confirm); `enterCuration/exitCuration`; `applyFilters` early-returns the authored membership in `pos` order; sort headers + filter-toggle locked in-mode (toast); `#curation-card` intro card (curator + title + macro intro + **exit**) above the list; record pane swaps `renderRN → renderCuratorNote`; researcher mark-bar hidden in-mode. CSS bracket-consistent. All inline JS passes `node --check`; curations JSON valid.
- **Deliberate v1 deviation from the captured spec:** Esc cancels the *threshold overlay* but does **not** exit an active curation — Esc already serves zen/search/overlay-close; binding it to also nuke the lens caused conflicts. Leaving the lens is the always-visible card **exit** button. Logged in Pending; revisit if Brandon wants Esc-to-exit.
- **Phase 2** (in-browser authoring + tutorial, multi-curator polish, Wikibase promotion, optional exhibition `.html`) remains queued.
- Unrelated/ongoing: `HH-HHC-0115`/P143 still awaiting the Wikibase Cloud SPARQL index (their infra lag — code/data verified correct).

**Version: next.html `v1.06-test.06`** (staging). Live `browse.html` unchanged at `v1.05.02`.

---

### 2026-05-19 — PDF reader → stage-integrated; search matches item type (next.html v1.06-test.07)

Working LINE: **NEXT**. Reworked the PDF reader per Brandon, plus a small search fix. Live `browse.html` untouched.

- **PDF reader, native + stage-integrated** (replaces the v1.06-test.04 separate overlay). The `#pdf-frame` iframe now lives *inside* `#stage`; a `.pane-image.pdf-mode` class hides the canvas and shows the PDF, and **repurposes the existing foot bar**: image-only controls (zoom/pct/fit/1:1/rotate/rotsave/seps) hide; **`↓ PDF`** (`#pdf-dl`, replaces `↓ Original`), a real **Fullscreen** button (`#pdf-fs`, Fullscreen API on `#stage`, vendor-prefixed), and **`✕ image`** close (`#pdf-close`) show; zen (`#zoom-fs`) stays; the title shows in the foot-left. `openPdf/closePdf/pdfFullscreen` replace `openPdfPane/closePdfPane`; `renderImage` calls `closePdf()` so switching items returns to the image; Esc closes the PDF and early-returns when `document.fullscreenElement` (lets the browser just exit fullscreen). Old `#pdf-pane`/header/CSS removed cleanly (grep-verified no stale refs). All inline JS passes `node --check`.
- **Native-viewer limits (unchanged, by design):** single-page-vs-continuous and the viewer's *internal* grey are the browser's and not controllable via a plain iframe — accepted as the cost of the no-library choice (Brandon chose native, stage-integrated over PDF.js). Our chrome/frame backing matches the stage (`var(--soft)`/dark) so the surrounding view area is seamless.
- **Search now matches item type:** added `it.itemType` to the `applyFilters` search haystack — typing "drawings"/"photographs" surfaces all of that type (previously only drawing *sub*-types/titles matched). Client-side only; no SPARQL/prefetch change. (Search remains intentionally inert inside a curated lens.)
- Mobile PDF path unchanged (open-in-tab). Rotation mobile/lightbox gap + Curated Phase 2 + Rotation Part 2 still queued; `HH-HHC-0115`/P143 still awaiting Wikibase Cloud's SPARQL index (their infra).

**Version: next.html `v1.06-test.07`** (staging). Live `browse.html` unchanged at `v1.05.02`.

---

### 2026-05-19 — PDF reader tweaks: foot trigger, no title, no fullscreen button (next.html v1.06-test.08)

Working LINE: **NEXT**. Three small follow-ups to the stage-integrated PDF reader per Brandon.

- **Removed the `#pdf-fs` Fullscreen button + `pdfFullscreen()` + the Esc-fullscreen guard + the `exitFullscreen` call in `closePdf`.** Zen (`#zoom-fs` / Z) is the maximize-the-view affordance; we don't need a separate Fullscreen API path. The project's pre-existing `#fs-toggle` browser-fullscreen header button stays untouched.
- **Removed `#pdf-title` from the foot-left.** Title belongs in the side panel record, not the bottom bar — that's the bar's convention.
- **Relocated the "View PDF" trigger from the record pane to the foot-left.** Removed `.pub-read` button (and its handler) from `renderMeta`; added `#pdf-view` in `.foot-left`, with `syncFootPdfView(item)` toggling `hidden` + setting `data-url` per item selection (called from `renderImage`). Click → `openPdf(url)` (signature trimmed: no title arg). Hidden in pdf-mode. The bottom-right keeps `↓ PDF` (foot-dl) for download. **Mobile** sheet still uses the `.pub-read` link (Open in tab) — no foot bar on mobile, so the in-record affordance stays there by necessity. All inline JS passes `node --check`.

**Version: next.html `v1.06-test.08`** (staging). Live `browse.html` unchanged at `v1.05.02`.

---

### 2026-05-19 — Foot bar: drop pixel count; View PDF ↔ ✕ in the same foot-left slot; ↓ PDF always foot-right (next.html v1.06-test.09)

Working LINE: **NEXT**. Three small follow-ups to the foot bar per Brandon.

- **Removed `#foot-dims`** (image pixel count) — element, CSS, and the two `renderImage` setters. The bar no longer carries metric clutter.
- **Foot-left = single PDF-control slot.** `#pdf-close` moved out of `.zoom-ctl` into `.foot-left`; **View PDF** and **✕** occupy the *exact same position* — visible alternately by mode. Close-button text simplified from `✕ image` to just `✕`.
- **Foot-right = `↓ PDF` whenever the item has one** (both image AND pdf-mode), replacing `↓ Original`. So download position is consistent across modes.
- **`syncFootPdfView()` is now the single source of truth** for foot controls — reads `state.selectedId` + `pdf-mode`, sets `hidden`/`href` for `#pdf-view`/`#pdf-close`/`#pdf-dl`/`#if-full`. Called from `renderImage`, `openPdf`, `closePdf`. The View-PDF click handler reads the current item directly (no `data-url` plumbing). All inline JS passes `node --check`.

**Version: next.html `v1.06-test.09`** (staging). Live `browse.html` unchanged at `v1.05.02`.

---

### 2026-05-19 — Firefox PDF side-tab nudge (next.html v1.06-test.10)

Brandon asked if any of the native PDF viewer chrome could be hidden (annotation tools row, side tab). Honest answer: not with the cross-origin iframe approach we picked — that's the trade-off we accepted vs. PDF.js. Implemented the only cheap nudge available: append `#pagemode=none` to the iframe `src` in `openPdf`, which asks **Firefox's bundled PDF.js to open with the side panel collapsed** (Chrome/Safari ignore it; harmless). The top annotation row remains uncontrollable in any browser. Defensive: only appended when the URL has no existing fragment. PDF.js path stays available if the constraint becomes intolerable.

**Version: next.html `v1.06-test.10`** (staging). Live `browse.html` unchanged at `v1.05.02`.

---

### 2026-05-19 — Hide "In the graph" section when an item has no phase (next.html v1.06-test.11)

Per Brandon: the publication has no phase, so the empty "No phase assigned. Item not yet linked into work hierarchy." block in the record was just noise. **The whole `<section class="graph-section">` is now omitted when `phaseLabel` is null** — in both `renderMeta` (desktop) and `renderMobSheet` (mobile). The graph-empty fallback HTML in `graphPathHTML` is left in place but unused (harmless dead branch; preserved for safety). JS clean.

**Version: next.html `v1.06-test.11`** (staging). Live `browse.html` unchanged at `v1.05.02`.

---

### 2026-05-19 — Switched to bundled PDF.js with a Minimal toolbar (next.html v1.06-test.12)

Brandon reversed the earlier native-vs-PDF.js call after seeing the irreducible native-viewer chrome (annotation row, side tab, browser-specific layout). Switched to **self-hosted PDF.js v5.7.284**, vendored under `assets/pdfjs/`.

- **Install.** Dropped the official `pdfjs-5.7.284-dist.zip` into `assets/pdfjs/` and pruned to **5.7 MB**: kept `build/pdf.mjs` + `build/pdf.worker.mjs`; `web/viewer.html` + `viewer.css` + `viewer.mjs` + `images/` + `iccs/` + `wasm/` + `locale/en-US/` only. Dropped all `*.mjs.map` (~9 MB), all other locales (~2.7 MB), `cmaps/` (~1.6 MB, non-Latin charmaps unused for English PDFs), `standard_fonts/` (~800 KB, our PDFs are JPEG-in-PDF), `pdf.sandbox.mjs` (PDF embedded JS, unused), `debugger.*`, the sample PDF.
- **Override.** `assets/pdfjs/web/hh-pdfjs.css` (loaded after `viewer.css` from a one-line edit to `viewer.html`) handles two jobs: (1) **hides every toolbar item outside the Minimal set** — `#editorModeButtons`, `#editorModeSeparator`, `#printButton`, `#downloadButton`, `#secondaryToolbarToggle`, `#viewFindButton`; (2) **themes what's kept** to match the archive foot-bar — mono font, our soft / ink / muted / rule tokens, our `↑ ↓ − +` glyphs replacing PDF.js's icon backgrounds via `::after` (the localized label `<span>` inside each button is visually-hidden). A tiny inline `<script>` in `viewer.html` reads `?theme=dark|light` from the URL and tags `<html>` so the override switches palette to match the archive's current mode.
- **Wiring.** `openPdf(url)` now sets the iframe `src` to `assets/pdfjs/web/viewer.html?file=<encoded url>&theme=<dark|light>`. Everything else — the foot-left View PDF ↔ ✕ swap, the foot-right ↓ PDF download, `closePdf`, mobile open-in-tab — unchanged. The `#pagemode=none` Firefox nudge from v1.06-test.10 is no longer relevant (different viewer) and was removed. All inline JS passes `node --check`.
- **⚠ Prerequisite for the viewer to actually render: R2 CORS.** PDF.js does cross-origin XHR to fetch the PDF bytes; `archive.hunterhousefoundation.com` currently returns no `Access-Control-Allow-Origin`, so the fetch is blocked. Brandon adds a CORS rule on the R2 bucket once: `AllowedOrigins: ["https://bturep.github.io", "http://localhost"]` (or `*`), `AllowedMethods: ["GET","HEAD"]`, `AllowedHeaders: ["*"]`, `MaxAgeSeconds: 86400`. Cloudflare dashboard → R2 → bucket → Settings → CORS Policy.
- **Minimal toolbar contents** (per Brandon's pick): `↑` prev page · `↓` next page · page-N-of-N input · `−` zoom out · `+` zoom in · zoom-mode dropdown (Auto / Fit Page / Fit Width / %). Nothing else.

**Version: next.html `v1.06-test.12`** (staging). Live `browse.html` unchanged at `v1.05.02`.

---

### 2026-05-19 — PDF.js toolbar fixes + ↓ PDF actually downloads (next.html v1.06-test.13)

Two bugs Brandon reported on first look at the PDF.js viewer.

- **Bar looked terrible** — two distinct causes:
  - PDF.js v5 paints toolbar icons via `::before { mask-image: var(--…-icon) }`. My override only nuked `background-image`, so my `::after` text glyphs stacked **on top of** PDF.js's chevrons (`^↑`, `v↓`, `−−`, `++`). Fixed: `#previous::before, #next::before, #zoomOutButton::before, #zoomInButton::before { display:none !important; }`.
  - The left-most sidebar toggle in v5 is `#viewsManagerToggleButton` (renamed from `sidebarToggleButton`), missed by my first grep. Added it + `#viewsManager` to the hide list.
- **`↓ PDF` was opening in a new tab instead of downloading.** Cross-origin browsers ignore the `download` attribute. **Bypassed CORS entirely** by setting `Content-Disposition: attachment; filename="…"` on the PDF *object* in R2 via `boto3 copy_object` (data-plane op — works with the existing rclone keys, no admin needed). Verified over the public URL: `content-disposition: attachment; …`. PDF.js's XHR fetch is unaffected (it reads bytes regardless of disposition). The foot `<a id="pdf-dl">` also got `download` (filename hint) and lost `target="_blank"`. **`scripts/ingest_publication.py` updated** so future publications upload with the same `--header-upload Content-Disposition`. Side-effect: navigating directly to the PDF URL in a browser now downloads instead of previewing — the "directly viewable by URL" fallback during SPARQL lag is no longer; acceptable since PDF.js renders it inline once CORS is set.
- All inline JS passes `node --check`.

**R2 CORS still pending** to make the in-app PDF.js viewer actually fetch & render. Tried via the rclone keys — `AccessDenied` (object-only scope; CORS is a bucket-config op). Brandon to either (a) add the rule via Cloudflare dashboard, or (b) mint a new R2 API token with **Admin Read & Write** scope and paste it; I run the boto3 PutBucketCors. Documented in the v1.06-test.12 entry above.

**Version: next.html `v1.06-test.13`** (staging). Live `browse.html` unchanged at `v1.05.02`.
