# CLAUDE.md — Hunter House Foundation session context
# Replaces the v1.02 archive (see CLAUDE_archive_v1.02.md for full earlier log)

Load this file at the start of any Claude Code session.

---

## ⚑ Pending at next session start — prompt Brandon immediately

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

## Memory protocol

1. **On load** — read this file before doing anything else.
2. **After each major task** — append a dated entry to the Session Log.
3. **Mid-session** — if something changes the general understanding, update the relevant section immediately.
4. **End of session** — consolidate, update version/status tables, write summary entry, commit and push.
5. **Never delete log entries.** Append only.

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
├── assets/
│   ├── verso.css           Light design system (all pages)
│   └── inverse.css         Dark design system (4 reading pages only)
├── scripts/                Batch Wikibase + R2 scripts (see Scripts table)
├── WIKIBASE.md             Full property table, QIDs, SPARQL templates
├── WIKIDATA_DRAFT.md       Draft QuickStatements for 3 Wikidata items (not yet submitted)
└── CLAUDE_archive_v1.02.md Full session log through v1.02
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

## browse.html — current architecture (v1.03.00)

### Shell layout
```
.site-top  (41px header bar)
.shell (flex row):
  .panel-left  (28%, collapses to 41px)  ← list pane + handle
  .pane-image  (flex:1)                  ← image stage + foot
  .panel-right (28%, collapses to 41px)  ← record pane + handle
```

**Panel collapse**: `.panel-left.out` / `.panel-right.out` sets `width:41px`. Edge handle (`.panel-handle`) is `position:absolute`, protrudes 5px into image area. Content hidden via `max-width:0` on `.panel-content` when `.out`. `togglePanel(side)` toggles the class.

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
| VERSION constant | Line ~1303 in browse.html — **must be bumped on every push**. All version displays (topright, mobile button, about pane) read from this single constant. `CACHE_KEY` derived from it automatically. |
| Dark mode | `html.dark` + `localStorage['hhf_theme_v2']` |
| SPARQL | GET with `encodeURIComponent` in browser; POST in Python scripts |
| Mark feature | `const marked = new Set()`. M key → `toggleMark(id)` → toggles `.marked` class on row. Dot rendered via `.row.marked::after` pseudo-element at `left:32px, bottom:4px`. Session-only (not persisted). |
| Researcher notes | `localStorage["hhf_rn"]` keyed by archive ID. Two-step auth: name → pin. Registry: `RPINS = { "203BTP": { name:"Brandon Poole", initials:"BP", qid:null } }`. |
| Filter badge | Filled pill `background:var(--ink); color:var(--bg); border:0` — no white border in dark mode. |
| Data footer | Wikibase / SPARQL / JSON links at bottom of record pane (`margin-top:auto`). |

### Mobile
`@media (max-width:767px)`: shell collapses to column, three tabs (List / Item / Record), panels full-width, handles hidden. `switchMobileTab(pane)` manages `.mobile-active`.

### SPARQL query
browse.html fetches: P2 archId, P96 img, rdfs:label, P95 master, P82/P64/P118 dates, P62 phase, P84 phase2, P88 drawType, P87 area, P1 itype, P79 src, P80 creator, P140 builtBy, P141 designedBy, P89 use, P92 builtStatus, P86 setPos, P100 notes, P91 medium, P93 rights, P94 heldBy, P99 archiveLink, P142 location.

`firstDate()` reads P82 → P64 → P118. Never P83 (digitization date = 2026).

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
| P91 | medium | string, e.g. "Pencil on vellum" |
| P96 | preview image | URL — required for browse.html |
| P97 | legacy ID | old HH-A-XXXX IDs saved here |
| P99 | archive link | AtoM item-level URL (CAA items) |
| P100 | notes | curator prose, shown in record pane |
| P139 | Wikidata QID | external-id, not yet populated |
| P142 | Physical location | archival path, e.g. "S0004, SS0001, SSS0018, FL0003" |

Next available IDs: **HH-HHC-0115**, **HH-CAA-0036**.

### Wikibase editing
- **Small (1–5 items):** QuickStatements at `/tools/quickstatements` — sometimes unreliable (redirect issue), fall back to Python script.
- **Bulk:** Python script modelled on `scripts/patch_dates.py`. Login flow: GET logintoken → POST login → GET csrftoken → write.
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
| `scripts/rename_ids.py` | HH-A → HH-HHC/CAA rename | Complete |
| `scripts/renumber_hhc.py` | HHC renumber 0036–0149 → 0001–0114 | Complete |
| `scripts/migrate_p142_location.py` | Move archival paths P100 → P142 | Complete |
| `scripts/fix_p142_prose.py` | Fix P142 values with mixed prose | Complete |
| `scripts/fill_p142_missing.py` | Fill P142 for 15 CAA items | Complete |

---

## Cataloguing status (May 2026)

| Collection | Catalogued | Images | Notes |
|---|---|---|---|
| HHC | ~114 items | partial (3 tiers) | Primary collection |
| CAA | 35 items | partial (3 tiers) | All have P142. Drawings + photos. |
| FUL | 9 items | partial | Fulker photographs |
| GES | 0 | none | Furniture drawings; pending |
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

Tags pushed: `v1.01.00` (fc98905), `v1.02.00` (2059cb7), `v1.02.18` (82065e6), `v1.03.00` (prior session), `v1.03.01` (prior session), `v1.03.08` (prior session).

---

## Session log

---

### 2026-05-15 — Sessions 01–02 condensed

Full log in `CLAUDE_archive_v1.02.md`. Summary of all work through v1.02.18:
- Built full mobile-responsive design system (verso.css, inverse.css, 4 reading pages).
- Splash redesigned to system monospace + self-hosted MP4; removed all render-blocking dependencies.
- browse.html: three-pane shell, progressive image loading (thumb/preview/large), zoom/pan/rotate, researcher notes panel (localStorage), dark mode, filter system, pill colour themes, typography consolidation, dim border system aligned to header grid.
- Wikibase: 149 items renamed (HH-A → HH-HHC/CAA), 114 HHC items renumbered, P91 medium written for 18 CAA items, P99 AtoM links for 25 CAA items, P142 physical location for all 35 CAA items, P139 Wikidata QID property created.
- Image pipeline: all 145 items have 3 R2 tiers (600px thumb / 2000px preview / 3840px large).
- scripts/clean_titles.py: bracket cleanup for ~60 items.
- WIKIDATA_DRAFT.md: three items drafted (not yet submitted).

---

### 2026-05-15 — Collapsible panels, mark feature, polish (v1.03.00)

**browse.html — collapsible panels**
- Left (browse) and right (record) panels now collapse independently to 41px (= header height).
- Collapse triggered by `.panel-handle` — a 10×40px button centred on each panel's inner edge, protruding 5px into the image area. On hover: dark fill, white chevron SVG. Chevron direction is CSS-only (rotate classes driven by `.out` state).
- Content hides via `max-width:0` on `.panel-content` when `.out`; `overflow:hidden` is on the content div (not the panel) so the handle can protrude.
- `z-index:1` on panels creates a stacking context so handles appear above the image pane.
- `togglePanel(side)` toggles the `.out` class. Handles hidden on mobile.
- Desktop panel width: 28% each (unchanged from before; previous session had a 320px regression which was corrected).

**browse.html — data footer**
- Wikibase / SPARQL / JSON links moved from record pane sections to a quiet footer row at the very bottom (`margin-top:auto`). Greyed out when no item selected.

**browse.html — mark feature (M key)**
- `const marked = new Set()` at module scope (session-only, not persisted).
- Press M while an item is selected → `toggleMark(id)` → toggles `.marked` class on the row.
- `.row.marked::after`: 4px dot, `position:absolute`, `left:32px` (centred under type badge), `bottom:4px`. Dark mode override for `--inv-fg`.
- M again removes the mark. Marks survive re-renders (renderList reads from the Set).

**browse.html — filter badge**
- Changed from outlined pill (`border:1px solid var(--ink)`) to filled pill (`background:var(--ink); color:var(--bg); border:0`). Eliminates the white border in dark mode.

**browse.html — image foot loading background**
- During `body.loading`, foot overrides to `background:var(--soft)` (light) / `#242220` (dark) with `border-top-color:transparent` — blends with viewer while data fetches. After loading, reverts to `var(--bg)` as normal.

**Various small fixes this session**
- Filter panel bottom border removed from list/phase-divider bar (prior session commit).
- Scroll pip opacity tweaks (prior session commits).
- Mark feature JS (`toggleMark` + M handler) was lost in intervening commits and restored.

**Version: v1.03.00**

---

### 2026-05-16 — Mobile bottom sheet overhaul (v1.03.01)

**Context / starting point**
Continued from prior session (v1.03.00). Mobile UI was mid-iteration: a contracted-list / bottom-sheet pattern had been built but had two unfixed bugs (images not displaying, scroll not working) and the contracted single-row strip felt awkward.

**browse.html — mobile bottom sheet, final layout**
- Sheet is now a fixed `72vh` panel, `position:absolute; bottom:0`, that floats over the list rather than covering it. Opens at `translateY(0)` (was `translateY(52px)` above a contracted 52px list strip).
- The contracted list strip (`mob-row-strip`, `panel-left.mob-contracted`) has been removed entirely. The full list remains visible and scrollable above the open sheet.
- Tapping the grip bar closes the sheet (was: toggle expanded/collapsed). No "full" state — full-screen image is handled by the lightbox.
- `mobToggleSheetFull` and `mob-sheet-full` CSS class removed.

**browse.html — image display fix**
- `renderMobSheet` was reading `item.img` (undefined) instead of `item.image` (the correct field from the SPARQL data mapping). Images now display correctly.
- Same bug existed in the lightbox click handler (`item?.img`) — fixed to `item?.image`. Tapping the image in the sheet now opens the full-screen lightbox.

**browse.html — scroll fix**
- `.mob-sheet-scroll` lacked `min-height:0`. Without it, iOS flex items refuse to shrink below content height and `overflow-y:auto` never engages. Added `min-height:0` and `-webkit-overflow-scrolling:touch`.

**browse.html — full record in mobile sheet**
- Removed researcher notes panel (`#mob-rn-panel`, `renderRN` call) from the sheet.
- Added three sections matching desktop record pane: `01 Description`, `02 Archival` (Location / Rights / Finding aid, conditional), `03 In the graph` (phase hierarchy path + sibling list).
- Siblings in the sheet are tappable (call `selectItem`) — same as desktop.
- Section header CSS (`.mob-sheet-scroll .meta-section h3`, `.graph-section h3`) added to mobile block; `.graph-path` and `.graph-siblings` styles work without parent scoping so they apply directly.

**browse.html — PWA icons (prior sub-session)**
- `scripts/regen_icons.py` updated: `BG=(6,5,4)` (#060504 near-black), `MARK=(184,180,172)` (#B8B4AC dim warm cream). Source pulled from git history (`git show 4a13a68:assets/icon-512.png`).
- manifest.json `short_name` changed to `"HH Archive"`. All `apple-mobile-web-app-title` tags updated to match.

**Version: v1.03.01**

---

### 2026-05-16 — Image rotation, about card polish, PWA full-screen fix (v1.03.08)

**Image rotation batch job (scripts/rotate_images.py)**
- 17 archive items rotated on R2 (master TIF + thumb/prev/large JPEG tiers each).
- HH-CAA-0018: mirror horizontal. HH-HHC-0004/0037/0062: 90° CCW. 13 HHC items (0005/0008/0009/0038/0070/0071/0092/0098–0103/0109): 90° CW.
- Script: `scripts/rotate_images.py` — downloads to `/tmp/rotate_work/`, transforms with Pillow, re-uploads via rclone.
- Cloudflare CDN cache purged via dashboard → Caching → Purge Cache → Prefix on both collection directories after upload.

**browse.html — about card text size (v1.03.07)**
- Reduced font sizes in `.mob-about-*` CSS: body/credits text from 12px → 10px, title from 13px → 11px, version from 11px → 10px, credits dt from 10px → 9px.

**browse.html — PWA full-screen fix (v1.03.08)**
- Root cause: `html.pwa .mob-sheet{height:72vh}` (CSS specificity 21) was overriding `.mob-sheet.mob-sheet-img-expanded{height:100%}` (specificity 20) in standalone PWA mode. Sheet stayed at 72vh when image was tapped — foot moved to bottom of 72vh sheet, but top bar didn't move.
- Fix: added `html.pwa .mob-sheet.mob-sheet-img-expanded{height:100%}` (specificity 31) — one line, no JS changes, no staged swipe changes.
- Tapping the image in PWA now correctly expands the sheet to full height, pushing the top bar up to the browse bar position.

**Version: v1.03.08**

---

### 2026-05-16 — Mobile list-head alignment, portrait lock, PWA flash fix (v1.03.28)

**Context / starting point**
Continued from v1.03.08. Session focused entirely on mobile UI polish and PWA behaviour.

**browse.html — list compression revert + reload button (v1.03.21)**
- Reverted `padding-left:8px` on `.row .title-wrap` (had compressed list entries rightward).
- Reduced `#mob-reload` font-size 22px → 17px (overshot mark on prior session).
- Hardcoded `HHFA v1.03.21` in mobile-version button HTML to eliminate JS-set flash.
- Added `margin-left:8px` to Phase sort header for ID/Phase visual spacing.

**browse.html — sort header alignment, BROWSE indent, portrait lock (v1.03.22–v1.03.25)**
- Root cause of YEAR misalignment traced: sort-arrow span (`min-width:9px`) sits right of the "Year" label inside the button, pushing text 12px left of button edge — hidden on mobile (v1.03.24).
- `sort-mini{flex-grow:1;justify-content:flex-end;gap:22px}` packs ID/PHASE/YEAR cluster to the right; YEAR right edge flush with year column and version text above.
- List-head `padding-left` 28px → 20px on mobile: BROWSE left-aligns with type chip column.
- Portrait lock: `"orientation":"portrait"` in manifest.json; CSS overlay (`#rotate-msg`) on landscape phones; `screen.orientation.lock('portrait')` JS call for PWA context.
- Sort-mini gap increased 14px → 22px for consistent ID / PHASE / YEAR spacing.

**browse.html + index.html — white flash reduction (v1.03.26)**
- `index.html`: added `<meta name="theme-color" content="#1a1816">` (was missing); early `<style>html,body{background:#1a1816}</style>` before preload link.
- `browse.html`: `<meta name="color-scheme" content="light">` → `dark light`; added `<style>html{background:#1a1816}</style>` as first `<head>` child, before render-blocking external CSS links.
- These reduce but don't eliminate the iOS WebKit navigation-boundary flash.

**Architecture change — splash folded in then removed (v1.03.27–v1.03.28)**
- v1.03.27: Splash moved into browse.html as a `position:fixed` overlay to eliminate navigation entirely. manifest `start_url` changed from index.html → browse.html. Tiny inline script hides overlay immediately if `hhf_splash` sessionStorage flag is set.
- v1.03.28: User decided no splash on app open. Overlay CSS/HTML/JS removed from browse.html. PWA now opens directly to the browse list. index.html remains as web landing page only.

**Version: v1.03.28**
