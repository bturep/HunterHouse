# CLAUDE.md — Hunter House Foundation session context
# Replaces the v1.02 archive (see CLAUDE_archive_v1.02.md for full earlier log)

Load this file at the start of any Claude Code session.

---

## ⚑ Active working context — read FIRST, act accordingly

<!-- LINE-MARKER: the claude() launcher rewrites the next line. Keep it on its own line. -->
**LINE: NEXT**

- **LINE: NEXT** → all browse work goes in **`next.html`**. Do **not** edit `browse.html` except an explicit live hotfix (then mirror the change into `next.html`). Version label convention: `next.html`'s `VERSION` constant is `v1.05-test.NN` — bump `NN` on every push, note it in the session log. Promotion to live = the documented Staging workflow.
- **LINE: LIVE** → work directly in `browse.html`; normal `v1.MAJOR.SESSION.PATCH` convention applies. `next.html` is dormant.

At session start: announce which LINE is active and which file you'll be editing. If LINE and the user's stated intent disagree, ask before editing.

---

## ⚑ Pending at next session start — prompt Brandon immediately

**v1.05 editing — open threads (LINE: NEXT, work in `next.html`).** Slices 3a–3d shipped & tested (Date `YYYY-MM-DD`, Phase, Item type, Built, Drawing type, Areas, title — all admin-gated via local proxy). Brandon to handle, tomorrow:
- **A few small `next.html` tweaks** Brandon has queued (unspecified — ask him).
- **Held by** — P94 (CAA/FUL) vs P79 (HHC) ambiguity; needs a rule for which to write before it's editable.
- **Phase rename** — distinct from "change phase" (P62, done). Renaming edits the shared Phase item's label → affects every item in that phase. Needs a confirm-guard. (`wbsetlabel` on `item.phaseQID`.)
- **Built by / Designed by** (P140/P141) — 0 vocabulary exists; needs a person/org entity-search picker (not the in-use-vocab pattern).
- **Promote `next.html` → live `browse.html`** when v1.05 is ready — the documented one-step Staging-workflow cycle (cp, bump to `v1.05.00`, tag, push).
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
| v1.04.00 | 2026-05-16 | UI colour overhaul; about pane redesign; filter system; data fixes; CSS audit |

Tags pushed: `v1.01.00` (fc98905), `v1.02.00` (2059cb7), `v1.02.18` (82065e6), `v1.03.00` (prior session), `v1.03.01` (prior session), `v1.03.08` (prior session), `v1.04.00` (this session).

---

## Staging / test page

A live-stable + parallel-test setup, zero extra infrastructure (plain GitHub Pages serves only `main`, so a git branch is **not** a separate URL — a duplicate file is).

| | |
|---|---|
| **Live** | `browse.html` → https://bturep.github.io/HunterHouse/browse.html — never edited during development; the stable public page |
| **Staging** | `next.html` → https://bturep.github.io/HunterHouse/next.html — the work-in-progress copy; break/iterate freely |

- Both files live on `main` (the only branch Pages serves). Pushing `next.html` redeploys the site but `browse.html` is untouched, so **live visitors are unaffected**.
- `next.html` carries `const VERSION = "v1.05-test"` → its `CACHE_KEY` (`hhf_v1.05-test`) is isolated from live (`hhf_v1.04`); the on-screen version shows which build you're on.
- `next.html` must stay in the **repo root** (relative `assets/…` paths). It links the shared `assets/verso.css` — inline `<style>` changes are isolated, but `verso.css` edits would leak to live. Fork to `assets/verso.next.css` only when a task needs CSS changes.
- `index.html` splash + the manifest `start_url` still point at `browse.html`; the installed PWA shows live. Test the new version in the **phone browser** at the `next.html` URL. `next.html` opened directly skips index.html's SPARQL prefetch (just a slightly slower first load — fine).

**Promotion (staging → live), when a version is ready:**
1. `cp next.html browse.html`
2. In `browse.html`, set `VERSION` to the real version (e.g. `v1.05`); update the session log.
3. (If `verso.css` was forked) `cp assets/verso.next.css assets/verso.css`.
4. Commit, `git tag v1.05.00 && git push --tags`, push. Live is now the new version.
5. Re-sync `next.html` from the new `browse.html` for the next cycle.

**Hotfixing live mid-cycle:** edit `browse.html` directly, push (deploys live immediately). Then port the same change into `next.html` so it isn't lost at next promotion.

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

---

### 2026-05-16 — UI colour overhaul, about pane redesign, filter system, data fixes (v1.04.00)

**Context / starting point**
Continued from v1.03.28. Session covered deep design and data work: the entire pill colour system was redesigned, the about pane was rebuilt, several data bugs were fixed, and the filter system was extended.

**browse.html — about pane redesign (v1.03.29–v1.03.35)**
- About pane moved from thin header overlay to full image-area takeover (same pattern as `#about-pane` with `position:absolute;inset:0`). Clicking "Hunter House Foundation Archive" in the header now opens the pane on desktop; on mobile it opens the existing `#mob-about` sheet.
- About pane background: `var(--soft)` light / `#242220` dark — matches image-stage, distinct from panel colour.
- Version number click removed from `#topright`; that role transferred to the markid link.
- About text updated: CCA/CAA disambiguation fixed throughout (CCA = Canadian Centre for Architecture, Montreal; CAA = Canadian Architectural Archives, Calgary). Links added to all external references (Wikibase, RDF, SPARQL, GLAM, CCA Digital Archives Manual, CC0, CC BY-NC-ND, CAA site).
- Credits: Floyd Marinescu (pc-sage), Olivia Jol (pc-slate), Brandon Poole (c-yellow).

**verso.css — dead class removal**
- Removed 6 unused classes: `.browse-cta`, `.colophon`, `.aside-block`, `.aside-toc`, `.page-title`, `.reading-layout` (and their responsive overrides). These had no callers in any page.

**scripts/archived/ — migration script archive**
- Moved 10 completed one-time migration scripts to `scripts/archived/`: rename_ids.py, renumber_hhc.py, revert_*.py, migrate_p142_location.py, fix_p142_prose.py, fill_p142_missing.py, cleanup_caa_descriptions.py, r2_cleanup.sh, renumber_hhc_r2.sh.

**browse.html — loading screen (v1.03.40–v1.03.41)**
- Fixed `pill is not defined` JS error: `renderMeta` called `pill()` which was only in scope inside `renderMobSheet`; replaced with inline template literal.
- Loading screen background fixed: was `var(--bg)` (panel dark), now `var(--soft)` / `#242220` to match image-stage.
- Loading screen centering fixed: moved `#load-screen` from inside `.image-stage` up to `.pane-image` level, so `position:absolute;inset:0` covers the full pane height including the 41px footer, giving true vertical centre.

**browse.html — pill colour system overhaul (v1.03.42–v1.03.45)**
- Removed all pill backgrounds. Pills are now bracket-style text: `[Area]`, `[Drawing type]` etc., using `::before{content:"["}` / `::after{content:"]"}` pseudo-elements.
- Seven colour themes (`pc-sage`, `pc-stone`, `pc-slate`, `pc-clay`, `pc-moss`, `pc-indigo`, `pc-denim`) all desaturated to "shade over hue" — low saturation, legible in both modes.
- Copper and red kept as the dominant brand colours; phase assigned to `var(--copper-deep)` (matching phase dividers), then stripped of interactive status entirely (see below).
- Areas (pc-sage) shifted from olive-green to amber/ochre (`#7a5820` / `#c09858`) — distinct from moss-green, architecturally warm.
- Light mode pill saturation punched up so categories are clearly distinguishable on light background. Dark mode unchanged.
- Phase `.row .ph` changed to `var(--muted)` — warm grey, clearly non-interactive, no overlap with copper link colour.

**browse.html — type badge cleanup (v1.03.44)**
- `.tmark` (type badge in list rows) converted from coloured pill-with-background to bracket style `[D]`, `[P]`, `[LS]` etc. with `pc-stone` colour and no background.
- Removed 12 per-type CSS colour override rules (both light and dark modes).
- Selected row still turns the badge `var(--red-deep)`.

**browse.html — phase stripped of interactive status (v1.03.45)**
- Phase removed from filter panel (was briefly added as chips — too many items to be useful).
- Phase in record pane reverted to plain text (not a clickable pill).
- `filterPhase` state, `applyFilters` check, badge count, `clearAllFilters` all cleaned up.
- Phase remains sortable via the left-pane column header.

**browse.html — collection filter added (v1.03.43–v1.03.46)**
- HHC / CAA / FUL collection chips added to Browse filter panel.
- `filterCollection` upgraded from dead string to a working `Set`.
- Wired into `applyFilters`, `updateFilterBadge`, `clearAllFilters`, and pill click handler.

**browse.html — HHC "Held by" fix (v1.03.46)**
- Root cause: HHC items carry collection via P79 (source collection) only; P94 (held by) is only set on CAA/FUL items. `item.heldBy` was null for HHC → no "Held by" row rendered.
- Added `collectionOf(item) = item.heldBy || item.sourceCollection` helper. Applied in both record pane renderers, `applyFilters`, and `uniqueCollections` in filter panel.
- Expanded `ARCHIVE_ABBREV`: added `"hunter house" → "HHC"` and `"fulker" → "FUL"` (previously only CAA was mapped).

**browse.html — medium field removed (v1.03.47)**
- P91 (medium) removed from SPARQL SELECT and OPTIONAL clause, data mapping, search haystack, mobile sheet, and desktop record pane. Six spots, clean removal.

**browse.html — graph current-item colour fix (v1.03.48)**
- `.pane-meta .graph-path .node .lbl{color:var(--ink)}` was overriding the base `.node.this .lbl{color:var(--red-deep)}` via equal-specificity + later-in-file cascade. Desktop showed plain text; mobile/PWA showed red (because `.mob-sheet-scroll` had re-stated the override explicitly).
- Fixed by adding `.pane-meta .graph-path .node.this .lbl{color:var(--red-deep)}` after the offending rule.
- Same pattern for `.sib.current .pos` — added `.pane-meta .graph-siblings .sib.current .pos{color:var(--red)}`.

**Version: v1.04.00**

---

### 2026-05-17 — Wikibase Main Page reframe + panel/fullscreen interlink fix (v1.04.01)

**Wikibase Main Page** (https://hunterhouse.wikibase.cloud/wiki/Main_Page)
- Reframed from biography → technical data-model entry point. Removed the "character of the record" and "design arcs" narrative and the Hunter biography (that content belongs on the Foundation public site). Added Arrangement (fonds→series→file→item), Rights, and Endpoints sections; resolved all `Q?` placeholder links; corrected the ID-prefix claims and counts against the live Wikibase; dropped the ID-prefix column (only archive-item IDs `HH-HHC-####`/`HH-CAA-####` are a real curated scheme). Live revisions 4438→4439.
- Full continuity record committed as **`WIKIBASE_MAINPAGE.md`** (current wikitext, resolved QID map, decisions, publish workflow, revision history). Read that file before resuming Main Page edits. Key decisions: org steward = Q187 "Hunter House Stewardship Project" (no "Hunter House Foundation" item exists); CAA repository = Q178 (not Q116, a same-label rights item).

**browse.html — panel ↔ bottom-bar fullscreen button interlink (v1.04.01)**
- Bug: the bottom-bar "hide panels" button (`#zoom-fs`) kept a private `fsActive` flag + snapshot of panel states; the edge handles (`togglePanel`) only flipped the `.out` class and never updated it, so the two drifted apart. Closing both panels by hand then pressing the button did nothing (it snapshotted "already hidden" and "restored" to hidden).
- Fix: removed the flag/snapshot. The panels' `.out` classes are now the single source of truth. Button rule: both hidden → reveal both; otherwise hide both. Edge handles now also call `syncFsBtn()` so the button icon/title always reflects real state. Initialised on load.
- Tradeoff accepted: the old (broken) "remember exactly which panel was open and restore it" behaviour is replaced by a clean hide-all/show-all toggle.

**Version: v1.04.01**

**browse.html — mobile sheet swipe navigation (v1.04.02)**
- Unified the mobile bottom-sheet gestures into one pipeline (replaced the bar-only vertical-swipe IIFE). Single `mode` state: `null | pending | v | h`.
- Image area (sheet open, NOT full-screen): first finger move locks an axis. Horizontal → `selectAdjacent(±1)` (swipe left = next, right = previous; bounds-checked against `state.filtered`, follow-finger `translateX`, 0.18s slide-out then re-render, snap-back if at an edge or under 50px). Vertical → same as the bar.
- Vertical open/close (down = close/collapse, up = expand) now also works on the image area and the foot bar, not just the top bar. Original bar behaviour preserved exactly.
- Record area (`#mob-sheet-scroll`) deliberately left with no gesture handlers → native vertical scroll, no side gesture, as required.
- Full-screen (`mob-sheet-img-expanded`) still owned by the existing pinch-zoom/pan handlers — new pipeline early-returns there. Added `swipeConsumedClick` guard so a finished swipe's trailing synthetic click can't also toggle full-screen (self-clears on consume + 500ms safety).
- Pushed straight to main (deploys live) at Brandon's choice so swipes can be tested on-device; revertible.

**Version: v1.04.02**

**Staging page established (v1.04.03)**
- Created `next.html` (copy of `browse.html`, `VERSION = "v1.05-test"`) as the parallel work-in-progress page at https://bturep.github.io/HunterHouse/next.html. Live `browse.html` untouched and stable. Full workflow + promotion steps documented in the new "Staging / test page" section above. v1.05 development happens in `next.html` from here.

**Version: v1.04.03**

**Active working-context marker (v1.04.04)**
- Added the "⚑ Active working context" block at the top of CLAUDE.md with a machine-rewritable `**LINE: NEXT|LIVE**` marker. Claude reads this first each session to know whether to edit `next.html` (NEXT, label `v1.05-test.NN`) or `browse.html` (LIVE). Conceptual clarification logged: version numbers are pure convention; git is the real version tracking. `claude()` launcher to be extended to flip this marker at session start (pending Brandon's OK to edit ~/.zshrc).
- Launcher wired: `~/.zshrc` `claude()` now prompts "Working line: LIVE / NEXT" (only for projects carrying the `LINE:` marker) and rewrites the CLAUDE.md marker. `zsh -n` verified. Active in new terminals only.

**Version: v1.04.04**

### 2026-05-17 — v1.05 line begins: role system foundation (next.html · v1.05-test.01)

Working LINE: **NEXT** — all edits in `next.html`; `browse.html` untouched. Goal of the v1.05 line: admin (Brandon) inline editing of Wikibase description fields, **desktop-only**, gated by the existing researcher-notes unlock, writing through a Cloudflare Worker proxy (auth path chosen). Scope settled over several clarifications:
- Researcher/Admin modes are **desktop browser only**. Mobile stays read-only; mobile researcher-notes display is explicitly **out of scope** ("something else", later).
- Role hierarchy: **Public** (not unlocked, read-only) · **Research** (notes/marking/selections) · **Admin** = Brandon only (+ Wikibase field editing). Researcher-notes unlock is the single gate.
- Saved selections + marking = desktop, `localStorage` (per-device, fine — not needed on mobile).

**Slice 1 done (this entry) — role plumbing, client-only, no Worker yet:**
- `RPINS` entries gain `role`; Brandon = `"admin"`. Role flows automatically through `rnUnlock` (stores full entry) into `rnSession()`.
- Added `rnRole()` → `"admin"|"research"|"public"` and `canEditWikibase()` (`role === "admin"`).
- Unlocked researcher-notes header now shows the role (`Brandon Poole · admin`) so the gate is visible/verifiable on desktop.
- No editing UI or Worker yet — that's Slice 2 (Cloudflare Worker; needs Brandon's Cloudflare deploy steps) then Slice 3 (field-edit UI + item pickers).

**Version: v1.05-test.01** (next.html). Live `browse.html` unchanged.

**Slice 2 done — local edit proxy (`scripts/edit_proxy.py`).** Backend chosen: **local proxy** (no Cloudflare account, no Floyd; runs only on Brandon's Mac, edits only from that machine while running). Holds the bot credential server-side; relays an allowlisted Wikibase write set (`wbsetlabel/description/aliases`, `wbcreateclaim`, `wbsetclaim`, `wbremoveclaims`) to the API. Localhost-only (127.0.0.1:8731), admin-secret guarded (admin pin, or `EDIT_PROXY_SECRET` in `.env`), CORS limited to the staging origin + localhost. Login + CSRF reuse the proven scripts/ flow; auto re-login on stale token. Smoke-tested OK. Run: `python3 scripts/edit_proxy.py`. Caveat: Chrome allows https→http://localhost; Safari may block it.

**Slice 3d done — multi-value Areas + Drawing type; Date full-precision; always-show editable rows (next.html · v1.05-test.07–08).** Date editor now accepts YYYY-MM-DD (month/day optional), writing Wikibase time precision 9/10/11 (`setTimeClaim`, was year-only `setYearClaim`). Multi-value editor for **Drawing type (P88)** and **Areas (P87)**: ✎ opens a chips+search popover — current values as removable chips (`removeMultiItem` by matching value QID→GUID), search to add (`addMultiItem`), optimistic array update + re-render, popover stays open for several edits. Editable rows (Date/Phase/Item type/Drawing type/Built/Areas) now always render for admin even when empty (placeholder `—`) so first values can be added; non-admin display unchanged. Editable set complete: Date, Phase, Item type, Drawing type, Built, Areas. Still parked: Held-by (P94/P79 ambiguity), phase **rename**, person/org search for Built-by/Designed-by.

**Slice 3c done — vocab scoping fix + Phase + Date (next.html · v1.05-test.06).** Fixed Item-type picker showing ~30 options: `vocabQuery(pid)` now property-scoped — P1→archive-item-ID-prefix subjects (6 media types), P62→phase items (38), default→global distinct. Built by/Designed by (P140/P141) dropped from editable set (0 values exist; need a person/org search — later). Added **Phase** (P62, reuses the picker) and **Date** (P82) — Date uses a dedicated year input writing year-precision-9 time value via `setYearClaim` (create-then-remove). Editable now: Date, Phase, Item type, Built. Confirmed working by Brandon: item type + built edits round-trip, browse unaffected.

**Slice 3b done — single-value item-field picker (next.html · v1.05-test.05).** Reusable: editable rows (Item type P1, Built P92, Built by P140, Designed by P141) get a ✎ (admin only) → `openFieldPicker` popover offering that property's existing vocabulary (`getVocab(pid)` SPARQL distinct, cached). Pick → `setSingleItemClaim` = wbgetclaims (read, origin=*) then **create-then-remove** via proxy (failure never empties the field) → optimistic `state.items` update + `renderMeta`. Reused `proxyEdit`/`hhToast`. Read paths smoke-tested. Held-by (P94/P79 ambiguous) + Areas multi-value (P87) = 3c; phase-title = 3d.

**Slice 3a done — inline title editing end-to-end (next.html · v1.05-test.02).** Proves the full pipeline: admin-gated click-to-edit on the desktop record `.meta-title` → `proxyEdit()` → local proxy → `wbsetlabel` on `item.qid` → optimistic update of `state.items` + list row + toast. Helpers added: `PROXY_URL`, `hhToast()`, `proxyEdit()` (admin secret = `rnSession().pin`), `wireMetaEdit()` (called at end of `renderMeta`, no-op unless `canEditWikibase()`). Same `proxyEdit` plumbing now reused by later slices. Next: **Slice 3b** — reusable entity-picker for the QID-valued single-value fields (item type P1, built status P92, built/drawn/held by P140/P141/P94) via wbgetclaims→wbremoveclaims+wbcreateclaim; then **3c** multi-value Areas (P87 ±); then **3d** phase-title (`wbsetlabel` on `item.phaseQID`, with "renames the whole phase" guard). next.html = Brandon's primary-researcher working structure for v1.05 (metadata edits + UI iteration together).

---

### 2026-05-17/18 — Session summary (LIVE at v1.04.02 · staging next.html at v1.05-test.11)

Large session. **Live `browse.html`:** panel↔fullscreen interlink fix (v1.04.01), mobile sheet swipe nav (v1.04.02). **Infra:** staging system established — `next.html` (copy, `v1.05-test.NN`) served on `main` alongside live `browse.html`; documented Staging/promotion workflow; "⚑ Active working context" `**LINE:**` marker; `claude()` launcher reworked so Hunter House auto-stays on `main` and the only prompt is **browse.html (LIVE) / next.html (NEXT)** — git-branch picker dropped for LINE projects (`v1.04` is **archive**, ignored). `WIKIBASE_MAINPAGE.md` rescued from `v1.04` onto `main` (30a992d). **Editing feature (next.html, Slices 1–3d):** roles (Admin/Research/Public via researcher unlock; Brandon=admin), local edit proxy `scripts/edit_proxy.py` (bot creds server-side, localhost-only, admin-secret), admin-gated inline editing of Title, Date (`YYYY-MM-DD`, precision 9/10/11), Phase, Item type, Built (pickers), Drawing type + Areas (multi-value chips), with optimistic update, create-then-remove claim safety, proxy-offline grey-out + auto-recover, lock/unlock re-render. Tested working by Brandon; edits hit the **real live Wikibase** (revision history = undo). Parked items → see Pending section.

**Versioning note:** no SESSION bump / git tag taken tonight — v1.05 is mid-development on staging and **not promoted**; the live line stays `v1.04`. All work is committed and pushed to `main` (remote), so memory is durable without a tag. Bump SESSION + tag at v1.05 promotion (or per Brandon's call). Per Brandon: version numbers are convention; git is the real tracking.

**State for resume:** `LINE: NEXT`; edit `next.html`; restart proxy with `python3 scripts/edit_proxy.py`; `browse.html` untouched since v1.04.02; open threads in the Pending section above.

---

### 2026-05-18 — MARK dialled in as a researcher tool (next.html · v1.05-test.12)

Working LINE: **NEXT** — all edits in `next.html`; `browse.html` untouched. Turned the invisible session-only M-key toy into a real, persistent **Research-role** capability (Public stays read-only; mobile out of scope per v1.05).

- **Per-researcher persistence.** New `hhf_marks = { [pin]: [archId,…] }` in localStorage, mirroring the `rnLoad/rnSave` pattern. Helpers: `canMark()` (`rnRole() !== "public"`), `marksKey()` (= `rnSession().pin`), `marksLoad/marksSave`, `marksHydrate()` (sync in-memory `marked` Set ↔ active researcher; empty for Public). Hydrated on boot and on every auth change via `rerenderRecord()`.
- **Role gate.** `toggleMark` and the M-key handler now no-op for Public. One researcher's marks never leak to the Public view or to another researcher (per-pin slot).
- **Marked bar** — slim researcher-only toolbar (`#mark-bar`) between `.list-head` and the rows; hidden for Public and on mobile. Shows `◆ N marked`; empty-state shows *"press M on a row to mark it"* (makes the otherwise-undiscoverable shortcut visible). Actions: **only** (toggles `state.filterMarkedOnly` → list narrows to marks), **export** (`navigator.clipboard` copy of sorted IDs, toast confirms), **clear** (hold-1.5s, reuses the `rn-del` hold-to-confirm safety; new `mark-charge` clip-path sweep).
- **Filter integration.** `state.filterMarkedOnly` wired into `applyFilters`, `updateFilterBadge` (+1), `clearAllFilters` (resets it). `renderList()` now calls `renderMarkBar()` at its tail so the bar stays in sync through every render path.
- Decision: placed in the **browse pane** (not a panel below the record-pane notes) — the marked set is list-scoped (count/only/clear/export all act on the list); a global panel in the per-item record pane would mismatch. All 4 requested affordances built.
- Pushed v1.05-test.12 (3e66149) for on-device testing.

**v1.05-test.13 — visible per-row mark + single-item unmark (Brandon feedback).** The old `.row.marked::after` was a 4px dot in the row's bottom-left corner — technically rendering but easy to miss ("no mark on the item itself"). Replaced with `.row .row-mark` — a copper `◆` in the row's left margin (absolutely positioned, grid untouched; hover → red). It's a real element and **click-to-unmark that one item**: the `#rows` click delegate now checks `e.target.closest(".row-mark")` first and calls `toggleMark` instead of `selectItem`. Answers "remove a single item, not all of them" — per-item via the diamond or M-key toggle; clear-all stays the hold gesture. Hidden on mobile alongside `.mark-bar`. Syntax-checked OK.

**v1.05-test.14 — row diamond resized + aligned (Brandon).** `.row-mark` 9px→13px and moved from row vertical-centre (`top:50%`) to `top:13px` (= row `padding-top` 11px + `.archid` `padding-top` 2px) so it sits on the first text line, aligned with the `[D]` item-type badge. CSS-only.

**Version: v1.05-test.14** (next.html). Live `browse.html` unchanged.

**v1.05-test.15 — note-presence row dot + stuck-filter bugfix (Brandon).**
- *Note dot.* New per-row indicator for entries that carry a researcher note (`hhf_rn`). Deliberately distinct from the mark: a quiet `var(--muted)` **● dot in the right margin**, non-interactive (selecting the row already shows the note). Helpers `rnNotedIds()` (one blob-parse → Set of noted ids, computed once per `renderList`) and `rnSyncRow(archId)` (live-toggles a single row's `.has-note` after note add/edit/delete in `renderRN`). Row gets `has-note` class; hidden on mobile with the mark. Not role-gated — notes are publicly visible, so the dot follows the note, not the researcher unlock.
- *Bugfix (Brandon-reported).* With "only" active, unmarking the **last** item emptied the list while `filterMarkedOnly` stayed true and the bar's zero-state has no toggle → stranded: badge showed `1`, list empty, no way back. `toggleMark` now captures `wasOnly`, auto-clears `filterMarkedOnly` when `marked.size` hits 0, and re-renders whenever it *was* in only-mode (so the full list returns on exit). Reload also escapes (flag isn't persisted).

**Version: v1.05-test.15** (next.html). Live `browse.html` unchanged.

**v1.05-test.16 — notes made private + admin all/mine toggle + bracket filter badge (Brandon).**
- *Filter badge → `[#]`.* `.filter-badge` was a bordered circle; now bracket convention (`::before "[" / ::after "]"`, no border/bg, `margin-left:5px`) to match the `[D]`/`[Area]` pill style. JS untouched (still `textContent = total`).
- *Notes are now private.* Researcher notes are no longer public. `rnVisibleNotes(archId)` returns notes paired with their **raw array index** (so edit/delete still hit the right entry when the view is filtered): Public → none; researcher → only `n.by === session.initials`; admin → all **only when** the new `rnShowAll` toggle is on. `rnNotedIds()` and `rnSyncRow()` are viewer-aware, so the row note-dots are private too. Public branch of `renderRN` no longer renders any notes or count (just the unlock affordance). `setEditMode` highlight now matches on `data-idx` (raw index) instead of DOM position, since visible rows can be non-contiguous.
- *Admin toggle.* `[mine]`/`[all]` button in the rn header, **admin-role only** (`.rn-allbtn`, bracket style). Flips `rnShowAll` (session-scoped, reset on lock-out), re-renders the panel + list dots. Default = mine.

**Version: v1.05-test.16** (next.html). Live `browse.html` unchanged.

**v1.05-test.17 — row flags relocated + restyled (Brandon).** Split-margin indicators replaced by a single `.row-flags` cluster absolutely positioned **below the item ID on the left** (`left:20px;top:30px`, flex, gap 6px). `.rf-mark` = orange dot (`#cf7a2c`, dark `#e8924a`; hover → `--red-deep`; still click-to-unmark, delegate now matches `.rf-mark`). `.rf-note` = small page/document SVG icon in `var(--copper)` (teal), non-interactive. Visibility still driven by `.row.marked` / `.row.has-note`. Mobile-hide selector updated to `.row .row-flags`.

**Version: v1.05-test.17** (next.html). Live `browse.html` unchanged.

**v1.05-test.18 — bracketed flag slots + more headroom (Brandon).** Row-flags reworked into two `.rf-slot` bracket cells: very light mono `[ ]` (`::before/::after`, opacity .45 — applied to the pseudo-only so the icon stays crisp) framing a fixed-size `.rf-ico` (9×10). Empty rows read `[ ] [ ]`; marked = orange dot inside slot 1, note = teal page icon inside slot 2. `top:30→34px` for more space below the ID; gap 6→5px. Unmark delegate still matches `.rf-mark` (now nested); mobile-hide still `.row .row-flags`.

**Version: v1.05-test.18** (next.html). Live `browse.html` unchanged.

**v1.05-test.19 — seen/reviewed flag, info panel, keyboard scheme (Brandon).**
- *Seen/reviewed.* Third flag slot — an eye icon, `var(--muted)`, click to clear. Per-researcher localStorage `hhf_seen = { [pin]: [...] }` mirroring the marks infra (`seen` Set, `seenLoad/Save/Hydrate`, `toggleSeen`; hydrated with marks on boot + auth change). Shortcut **R**. Row class `seen`.
- *Flag strip now researcher-only.* `.row-flags` rendered only when `canMark()` (computed once per `renderList` as `flags`) — Public no longer sees empty bracket slots; the strip is a researcher workspace. Order: `[mark] [seen] [note]`, `.rf-ico` 9→10px.
- *Info panel.* `[?]` button in the Record bar (`.rec-info`, red attention colour, faint bracket motif). `#info-pane` overlays `#panel-right` entirely (absolute inset:0, like `#about-pane` but scoped to the record panel). `renderInfoPane()` is role-aware: base orientation + grouped shortcut tables always; a Researcher group + an `.ip-note` callout that differs for public / research / admin. Points to the wordmark for the deep colophon (no duplication). Open/close/toggle; `?` toggles, `Esc` closes (added to the Escape chain).
- *Keyboard scheme.* Added **F** fit, **T** turn/rotate, **Z** zen (hide panels — clicks `#zoom-fs`), **= / +** zoom in, **− / _** zoom out (click the zoom buttons so disabled-bounds are respected), **R** reviewed, **?** info. Existing kept: `/` search, `Esc`, `1` 1:1, `M` mark, ↑/↓ nav, Enter open item. Browser/OS fullscreen left on its header button by design (needs a user gesture; avoids Z confusion). All gated by `!inInput`.

**Version: v1.05-test.19** (next.html). Live `browse.html` unchanged.

**v1.05-test.20 — fix `/` search shortcut (scope bug).** Root cause: `openSearch()` is declared inside `main()`, but the global keydown handler lives in the sibling `wireControls()` — `openSearch` was never in scope there, so `/` threw a ReferenceError (pre-existing; surfaced now via shortcut testing). Fixed by inlining the DOM ops (`#search-input` add `.open` + focus) so the handler has no cross-scope dependency. Enter (open item page) untouched pending Brandon's call on a fullscreen binding.

**Version: v1.05-test.20** (next.html). Live `browse.html` unchanged.
