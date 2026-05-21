# CLAUDE.md — Hunter House Foundation session context
# Live working memory. Frozen archives (read-only, full historical detail; git also holds all of it):
#   • CLAUDE_archive_v1.06.md — v1.05.00 → v1.06.00 promotion (freeze 2026-05-20)
#   • CLAUDE_archive_v1.05.md — v1.03.00 → v1.05.02 (freeze 2026-05-19)
#   • CLAUDE_archive_v1.02.md — ≤ v1.02.18 (earliest freeze)

Load this file at the start of any Claude Code session.

---

## ⚑ Active working context — read FIRST, act accordingly

<!-- LINE-MARKER: the claude() launcher rewrites the next line. Keep it on its own line. -->
**LINE: NEXT**

- **LINE: NEXT** → all browse work goes in **`next.html`** only. Do **not** edit `browse.html` — including hotfixes. The bar for touching `browse.html` is "the live site is broken for real visitors and there is no other path"; if you're framing it as a hotfix to ship a new feature alongside, you're wrong, and it goes to `next.html` to wait for the next promotion. Version label: `next.html`'s `VERSION` constant is `v1.07-test.NN` — bump `NN` on every push, note it in the session log. Promotion to live = the documented Staging workflow.
- **LINE: LIVE** → work directly in `browse.html`; normal `v1.MAJOR.SESSION.PATCH` convention. `next.html` dormant.

At session start: announce which LINE is active and which file you'll be editing. If LINE and the user's stated intent disagree, ask before editing.

**Standing conventions:**
- **Preview convention** — any artifact Brandon needs to eyeball (PDF, image, export) is written to `~/Desktop` with a clear name and opened automatically.
- **Version-in-update convention** — every status message Brandon receives must explicitly state the next.html version (and live browse.html version when relevant) in the prose he reads — e.g. "Pushed (`abc123`, `next.html` v1.07-test.NN)".
- **Edit-proxy restart** — `python3 scripts/edit_proxy.py` each session (dies on Mac sleep; admin inline editing in next.html is inert without it).

---

## ⚑ Pending at next session start

**Open threads carried into v1.07:**
- **Curator Phase 2** — in-browser authoring + multi-curator polish + Wikibase promotion (Curation as first-class item w/ qualifiers; needs proxy `wbsetqualifier`). Phase 1 lens lives in next.html (curator JSON load commented out on live; all overlay/card/state code dormant, promotable by uncommenting one line).
- **Held by** — P94 (CAA/FUL) vs P79 (HHC) ambiguity; needs a rule for which to write before it's editable.
- **Phase rename** — distinct from "change phase" (P62, done). Renaming edits the shared Phase item's label → affects every item in that phase. Needs a confirm-guard. (`wbsetlabel` on `item.phaseQID`.)
- **Built by / Designed by** (P140/P141) — 0 vocabulary exists; needs a person/org entity-search picker (not the in-use-vocab pattern).
- **EGC photograph ingest** — drawings DONE 2026-05-20 (30 items, Q505–Q534). The 36 photographs of Gesinger's built furniture (photographer **Mary McNeill Knowles**, now known) are awaiting a separate intake sheet — when Brandon issues it, batch into the same EGC collection (Q182) and pair each photo to its phase (Q494–Q502 or Q499 Orphan) by furniture-piece column. Pattern: copy `scripts/batch_ingest_egc.py`, set type=photograph (Q89), creator = Knowles (mint Q if missing), add P85/depicts → Q209 Eric Gesinger, P141/designed-by → Q201 Hunter. Photos likely don't carry P88.
- **Rotation Part 2** — maintenance bake script driven by P144 claims; rotates master+3 tiers on R2, clears the claim, purges CDN. Prerequisite: an automated Cloudflare cache-purge API token (still not wired). Also fixes the **mobile/lightbox rotation gap** — P144 is currently applied at the desktop image stage only.

**Deferred / structural:**
- **Wikibase revision-history cleanup** (later, when the archive settles). Iterating during dev has left noisy edit histories on some items (label tweaks, claim re-saves, vocabulary churn). Two paths: (a) per-item revision deletion via `Special:RevisionDelete` — needs sysop privileges, which Brandon has on his own Wikibase Cloud instance; (b) full instance reset via Wikibase Cloud support, or spin up a new instance and re-import clean. Cleared/emptied items (`wbeditentity clear:1`, what we did to Q503) leave permanent Q-number gaps but no longer pollute SPARQL/browse — gaps don't matter so this is the cheap option for one-off mistakes. Revision history itself doesn't affect SPARQL or `browse.html`; this is psychological cleanup, not data-quality. **Don't tackle until the canonical model is settled** (post-RAD-alignment decision, see below).
- **R2 metadata sidecars** (preservation backup). For every archive item, also write a JSON sidecar to R2 alongside the image bytes — full Wikibase record (labels, descriptions, claims, references) per item. So R2 holds a self-contained, Wikibase-independent record of every item; if Wikibase ever needs reset or migration, the canonical data is already preserved alongside the images. Path pattern: `{collection}/metadata/{ARCH_ID}.json` (mirrors `intake/` sibling under each collection). Generate via `wbgetentities` per item; regenerate on each ingest. Plan: (1) write a one-time `scripts/backup_metadata.py` to dump the current state of every item under each collection prefix; (2) extend `ingest_item.py` / `ingest_publication.py` / `batch_ingest_egc.py` to write the sidecar at the end of each per-item ingest. **Do the one-time dump when the archive settles** (after rotation Part 2 bakes are done and metadata is stable).
- **Archival-standards alignment.** Current model uses ISAD(G) loosely; not formally RAD-compliant. Gaps: (1) fonds-level item in Wikibase; (2) series level encodes physical custody (HHC/CAA) rather than creator function — redefine or formally acknowledge as a custodial split; (3) Level of Description property (new P) needed for AtoM/LAC interop. Important before academic write-up or cross-institutional integration.
- **Wikidata items ready to submit.** Three drafted in `WIKIDATA_DRAFT.md` (Richard Hunter person; Canadian Architectural Archives institution; Richard Hunter fonds). Brandon needs a free Wikimedia account (2 min at `wikidata.org/wiki/Special:CreateAccount`); then QuickStatements copy-paste. After creation, add Q-numbers to P139 on Q201 (Hunter) and Q116 (CAA) in our Wikibase. **Prompt at session start.**
- **PWA splash reinstall on iPhone.** Manifest already has `start_url: browse.html` but the old install is cached with index.html. Remove HH Archive from home screen and re-add from `bturep.github.io/HunterHouse/browse.html`.

---

## Memory protocol

1. **On load** — read this file before anything else.
2. **After each major task** — append a dated entry to the Session log.
3. **Mid-session** — update relevant section immediately if general understanding changes.
4. **End of session** — consolidate, update version/status tables, write summary, commit and push.
5. **Never delete log entries.** Append only. Rotation = freeze a verbatim archive + condense here; the original is never destroyed.

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

**Credentials** in `/Users/brandonpoole/Documents/hh-wikibase-migration/.env` (`WIKIBASE_BOT_USER=MyBot@my-bot`, `WIKIBASE_BOT_PASSWORD`, `R2_PUBLIC_BASE=https://archive.hunterhousefoundation.com`). Bot has full write access; all scripts auto-load `.env`.

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
├── next.html               Staging copy of browse.html (v1.07-test.NN)
├── assets/
│   ├── verso.css           Light design system (all pages)
│   ├── inverse.css         Dark design system (4 reading pages only)
│   ├── pdfjs/              Bundled PDF.js v5.7.284 (~5.7 MB; in-stage PDF reader)
│   └── placeholders/       image-missing tiers for P96-less items
├── scripts/                Batch Wikibase + R2 scripts (see Scripts table)
├── curations/              Curated-lens JSON (index.json + <slug>.json)
├── WIKIBASE.md             Full property table, QIDs, SPARQL templates
├── WIKIDATA_DRAFT.md       Draft QuickStatements for 3 Wikidata items (not submitted)
└── CLAUDE_archive_v1.0{2,5,6}.md   Frozen historical session logs
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
Dark mode (`html.dark`) overrides: `--ink:#f0ede6`, `--bg:#1a1816`, `--soft:#26231e` (image-stage uses `#242220` — kept in sync with PDF.js theme).

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

**Panel collapse**: `.panel-left.out` / `.panel-right.out` sets `width:41px`. Edge handle (`.panel-handle`) is `position:absolute`, protrudes 5px into image area. Content hidden via `max-width:0` on `.panel-content` when `.out`. `togglePanel(side)`. `#info-pane` is a direct child of `#panel-right` (sibling of `.panel-content`); its collapse rule is `.panel-right.out #info-pane{display:none}`.

**Loading state**: `body.loading` applies `visibility:hidden` to list/rows/meta/foot. During loading, `.image-foot` overrides to `background:var(--soft)`. `body.refitting` hides `#canvas` during the 260ms panel-width transition (+ `setTimeout(280, fitToFrame)`) so the splash-fit image doesn't visibly shrink.

### Image tiers (R2)
- `_thumb.jpg` — 600px, 75% quality
- `_prev.jpg` — 2000px, 82% quality
- `_large.jpg` — 3840px, 85% quality (full-res download tier)

`renderImage()` loads thumb + large simultaneously; thumb shows first, large fades in.

### Key JS patterns
| Pattern | Detail |
|---|---|
| VERSION constant | Single source of truth — **must be bumped on every push**. `CACHE_KEY` derives from full `VERSION`. `VERSION_DISPLAY` strips the patch for public display unless label contains `-test`. |
| Dark mode | `html.dark` + `localStorage['hhf_theme_v2']` |
| SPARQL | GET with `encodeURIComponent` in browser; POST in Python scripts |
| Roles | `rnRole()` → `"admin"|"research"|"public"`; `canEditWikibase()` = admin; `canMark()` = not public. Single gate = researcher-notes unlock. Desktop only; mobile read-only. |
| Researcher notes | `localStorage["hhf_rn"]` keyed by archive ID, name→pin auth. `RPINS = { "203BTP": { name:"Brandon Poole", initials:"BP", qid:null, role:"admin" } }`. Notes private (viewer-aware `rnVisibleNotes`; admin `[mine]`/`[all]`). |
| Row flags | Per-researcher persistent: `hhf_marks` / `hhf_seen` keyed by pin, plus note-dot following `hhf_rn`. Researcher-only `.row-flags` register under the ID. |
| Admin inline edit | Click-to-edit on record pane → `proxyEdit()` → local `scripts/edit_proxy.py` (localhost:8731) → Wikibase. Create-then-remove claim safety; optimistic state update. |
| PDF reader | In-stage iframe + bundled PDF.js v5.7.284 at `assets/pdfjs/web/viewer.html?file=…&theme=…`. Minimal toolbar via `hh-pdfjs.css`. `HOSTED_VIEWER_ORIGINS` patched in `viewer.mjs` to allow `bturep.github.io` etc. (re-apply on PDF.js upgrade.) Foot-left: View PDF ↔ ✕ swap. Foot-right: `↓ PDF` (R2 PDFs carry `Content-Disposition: attachment` so the link truly downloads). Mobile: open-in-tab. |
| Rotation (P144) | `renderImage` seeds `zoomState.rotation` from stored P144 as **base orientation** (fit/transpose keyed off it). T = transient +90, no write. Admin-only `#zoom-rotsave` (`⤓ save`) shown when rotated-off-base, writes via `setStringClaim(qid, P144, net)` (create-then-remove; `net===0` ⇒ clears claim). Desktop image stage only — mobile sheet + lightbox still show unrotated file (Part 2 bake fixes for all). |
| Filter badge | Bracket style `[#]` (no border/bg). |
| Data footer | Wikibase / SPARQL / JSON links at bottom of record pane (`margin-top:auto`). |

### Mobile
`@media (max-width:767px)`: shell collapses to column, three tabs (List / Item / Record), panels full-width, handles hidden. `switchMobileTab(pane)`. Bottom sheet with unified swipe pipeline (axis-lock; horizontal = adjacent item, vertical = open/close). Mobile is **read-only**.

### Catalogue SPARQL
Fetches P2 archId, P96 img (OPTIONAL), rdfs:label, P95 master, P82/P64/P118 dates, P62 phase, P84 phase2, P88 drawType, P87 area, P1 itype, P79 src (REQUIRED — keeps vocab/people/institutions out), P80 creator, P140 builtBy, P141 designedBy, P89 use, P92 builtStatus, P86 setPos, P100 notes, P93 rights, P94 heldBy, P99 archiveLink, P142 location, P143 accessCopy, P144 rotation.

`firstDate()` reads P82 → P64 → P118. Never P83 (digitization date = 2026). `collectionOf(item) = item.heldBy || item.sourceCollection` (HHC carries collection via P79 only).

---

## Wikibase quick reference

See `WIKIBASE.md` for full property table, QIDs, and SPARQL templates.

### Most-used properties
| PID | Label | Notes |
|---|---|---|
| P1 | instance of | Q88=drawing, Q2=phase, Q91=publication, Q488=land survey |
| P2 | HH archive ID | `HH-HHC-####` / `HH-CAA-####` |
| P62 | part of | project phase QID |
| P79 | source collection | Q180=HHC, Q116=CAA |
| P80 | creator | Q201=Richard Hunter |
| P82 | date created | year precision `/9` |
| P88 | drawing type | Q98=plan, Q99=elevation, etc. |
| P92 | built status | Q51=built |
| P96 | preview image | URL — OPTIONAL in catalogue SPARQL (stubs appear) |
| P97 | legacy ID | old HH-A-XXXX IDs |
| P99 | archive link | AtoM item-level URL (CAA items) |
| P100 | notes | (no longer rendered — slated for reassignment) |
| P139 | Wikidata QID | external-id, not yet populated |
| P142 | Physical location | archival path, e.g. "S0004, SS0001, SSS0018, FL0003" |
| P143 | access copy | URL — publication PDF; drives PDF reader |
| P144 | display rotation | String `90`/`180`/`270` CW; applied at render (desktop stage) |

**Next available IDs: HH-HHC-0116, HH-CAA-0036, HH-EGC-0031.** (HH-HHC-0115 = Q490, the 1986 Hunter portfolio publication; HH-HHC-0112 = Q463, Covenant Site Plan; HH-EGC-0001..0030 = Q505..Q534, the Eric Gesinger Collection drawings ingested 2026-05-20.)

### Wikibase editing paths
- **Small (1–5 items):** QuickStatements at `/tools/quickstatements` (sometimes unreliable — fall back to Python).
- **Bulk:** Python script modelled on `scripts/patch_dates.py`. Login: GET logintoken → POST login → GET csrftoken → write.
- **Admin inline (browse/next.html):** click-to-edit on record pane → local edit proxy → Wikibase API. Desktop + admin only.
- **SPARQL:** browser at `hunterhouse.wikibase.cloud/query`, or POST in Python (`Content-Type: application/sparql-query`). GET with URL encoding fails in Python.
- **Single-item ingest:** `scripts/ingest_item.py` (config block at top; auto-resolves/creates vocab by *label + instance-of*; `QID_OVERWRITE` repurposes a stub via `wbeditentity clear:1`; dry-run default, `--execute` to write).
- **Publication ingest:** `scripts/ingest_publication.py` (masters byte-for-byte + SHA-256 manifest + cover tiers + access PDF; uploads PDF with `Content-Disposition: attachment`).

---

## Image pipeline — Cloudflare R2

`rclone` remote `hh-r2:hunter-house-archive`. Credentials in `.env` (object-scope; bucket-config ops like CORS need an admin token).

```bash
rclone ls hh-r2:hunter-house-archive
rclone copy local.jpg hh-r2:hunter-house-archive
```

Filename: `HH-HHC-0044_Label_Date_prev.jpg` (also `_thumb.jpg`, `_large.jpg`).

R2 folder structure per collection: `hunter-house-collection/{masters,previews,thumbs,large,pdf}/` and `canadian-architecture-archive/{masters,previews,thumbs,large}/`.

**R2 CORS** is configured (allows `https://bturep.github.io`, `http://localhost`, `http://127.0.0.1`; GET/HEAD; exposes Content-Length/Type/Disposition; 24h max-age) so PDF.js can cross-origin fetch.

**ICC profile rule:** ingest/regen scripts (`regen_previews.py`, `ingest_item.py`, `ingest_publication.py`) pass `-m /System/Library/ColorSync/Profiles/sRGB Profile.icc` to sips, so all output JPEGs bake sRGB. Prevents Chrome's wide-gamut-Mac cyan-cast on the scanner's `kip2300-v6-` profile. **Master TIFs untouched** (preservation copies keep capture-device profile). `scripts/recolor_previews.py` is the idempotent retro-fix for already-uploaded files.

---

## Batch change protocol (summary)

For any bulk P2/P96/P95 change: (1) export SPARQL snapshot to `data/snapshots/`, (2) create branch, (3) write mapping TSV, (4) write P97 legacy ID before changing P2, (5) R2 copy to new name (don't delete old), (6) update Wikibase, (7) verify, (8) delete old R2 files, (9) merge + tag.

Full protocol in `CLAUDE_archive_v1.02.md` §"Batch change protocol".

**Completed migrations:** HH-A → HH-HHC/CAA rename (2026-05-14) · HH-HHC-0036–0149 → 0001–0114 renumber (2026-05-14) · R2 cleanup of 510 stale files (2026-05-14) · P142 migration from P100 (2026-05-15) · 254 R2 JPEGs recolored kip2300 → sRGB (2026-05-19).

---

## Scripts

| Script | Purpose | Status |
|---|---|---|
| `patch_dates.py` | Add P82 date claims + update descriptions | Active |
| `regen_previews.py` | Regen preview/thumb/large from TIF masters | Active |
| `clean_titles.py` | Strip/rewrite bracketed annotations from labels | Active |
| `strip_counter_brackets.py` | Remove `[N/N]` counter patterns from labels | Active |
| `edit_proxy.py` | Local admin Wikibase write proxy (localhost:8731, bot creds server-side) | Active |
| `make_ges_intake.py` | Generate the GES collection intake workbook | Active |
| `mint_property.py` | Mint (or find, idempotent) one Wikibase property: `--label --desc --datatype` | Active |
| `ingest_item.py` | Ingest single-image item: master TIF + 3 R2 tiers + Wikibase claims. Auto-resolves vocab. Dry-run default | Active |
| `ingest_publication.py` | Ingest multi-page publication (masters byte-for-byte + SHA-256 manifest + cover tiers + access PDF → R2; create Wikibase item). Dry-run default | Active |
| `batch_ingest_egc.py` | Workbook-driven batch ingest for the EGC drawings (30 items, 2026-05-20). Reads `EGC_intake.xlsx` + scans folder; mints phases + missing drawing-type vocab once; per-row tiers→R2 + Wikibase item. Dry-run default; `--execute` writes. Template for the EGC photo intake and future collection batches | Active (used once for EGC drawings) |
| `recolor_previews.py` | Convert R2 JPEGs from kip2300 ICC profile → sRGB. Idempotent. `--dry-run` / `--one KEY` / `--execute` | Active |
| (`scripts/archived/`) | Completed one-time migrations (rename_ids, renumber_hhc, migrate_p142_location, fix_p142_prose, fill_p142_missing, rotate_images, …) | Complete |

---

## Cataloguing status (May 2026)

| Collection | Catalogued | Images | Notes |
|---|---|---|---|
| HHC | ~115 items | partial (3 tiers) | Primary collection. Stubs without P96 now appear in list. |
| CAA | 35 | partial (3 tiers) | All have P142. Drawings + photos. |
| FUL | 9 | partial | Fulker photographs |
| EGC | 30 drawings | complete (3 tiers + master) | Hunter furniture drawings for Gesinger commissions; ingested 2026-05-20 (Q505–Q534). 36 photos pending separate intake. |
| FRH | 0 | none | Frances Hunter materials; pending |
| IVH | 0 | none | Ivan Hunter photographs; pending |

---

## Version history (milestones)

| Version | Date | Notes |
|---|---|---|
| v1.01.00 | 2026-05-14 | Three-level versioning adopted; mobile responsiveness; dark design system; Wikibase date patching |
| v1.02.00–.18 | 2026-05-15 | Splash redesign, P142, progressive loading, 3840px tiers, researcher notes, dim border system, typography consolidation |
| v1.03.00–.28 | 2026-05-15 → -16 | Collapsible panels, mark feature, mobile bottom sheet + lightbox, image rotation batch, portrait lock, splash removed from PWA |
| v1.04.00–.02 | 2026-05-16 → -17 | UI colour overhaul, about pane redesign, filter system, panel↔fullscreen interlink fix, mobile sheet swipe nav, Staging system established (next.html + LINE marker) |
| v1.05.00 | 2026-05-19 | **Promotion of v1.05 line.** Role system (Admin/Research/Public), local edit proxy, admin inline Wikibase editing (title/date/phase/item-type/built/drawing-type/areas), mark/seen/note row flags, info panel, keyboard scheme. |
| v1.05.02 | 2026-05-19 | Live hotfixes: info panel hidden when right panel collapsed; public version display drops patch number (`VERSION_DISPLAY`). |
| v1.06.00 | 2026-05-20 | **Promotion of v1.06 line.** Splash overhaul (Continue-to-archive button, HHFA × ↔ Continue swap by `body.hh-splash`, default landing HH-CAA-0028, `body.refitting`), in-stage PDF reader + bundled PDF.js (P143), admin display rotation P144 with ⤓ save, SPARQL P79 required / P96 OPTIONAL, "In the graph" hidden when no phase, search matches item type, search bar + `/` restored. **Curated lens hidden on live** (dormant in browse, active in next; promotable by uncommenting one line). |

Tags pushed: `v1.01.00` (fc98905), `v1.02.00` (2059cb7), `v1.02.18` (82065e6), `v1.03.00`, `v1.03.01`, `v1.03.08`, `v1.04.00`, `v1.05.00` (2026-05-19), `v1.06.00` (2026-05-20).

Full per-version detail: `CLAUDE_archive_v1.06.md` (v1.05→v1.06), `CLAUDE_archive_v1.05.md` (v1.03→v1.05), `CLAUDE_archive_v1.02.md` (≤v1.02).

---

## Staging / test page

A live-stable + parallel-test setup, zero extra infra (plain GitHub Pages serves only `main`, so a git branch is **not** a separate URL — a duplicate file is).

| | |
|---|---|
| **Live** | `browse.html` → https://bturep.github.io/HunterHouse/browse.html — never edited during development |
| **Staging** | `next.html` → https://bturep.github.io/HunterHouse/next.html — break/iterate freely |

- Both on `main`. Pushing `next.html` redeploys but `browse.html` untouched, so **live visitors unaffected**.
- `next.html` `VERSION = "v1.07-test.NN"` → `CACHE_KEY` (`hhf_v1.07-test.NN`) isolated from live (`hhf_v1.06.00`).
- `next.html` must stay in repo root (relative `assets/…`). Shares `assets/verso.css` — inline `<style>` changes isolated, but `verso.css` edits leak to live. Fork to `assets/verso.next.css` only when a task needs CSS changes.
- `index.html` splash + manifest `start_url` point at `browse.html`; installed PWA shows live. Test new version in the **phone browser** at the `next.html` URL.

**Promotion (staging → live), when ready:**
1. `cp next.html browse.html`
2. In `browse.html`, set `VERSION` to the real version; update session log.
3. (If `verso.css` was forked) `cp assets/verso.next.css assets/verso.css`.
4. Commit, `git tag vX.NN.00 && git push --tags`, push.
5. Re-sync `next.html` from the new `browse.html` for the next cycle (bump VERSION to `vX.NN+1-test.01`).

**⚠ Prefetch-sync at promotion:** if `next.html`'s `CATALOGUE_QUERY` changed, also sync `index.html`'s prefetch copy. (Currently `index.html` is a thin redirect with no SPARQL prefetch — the "must stay in sync" warning is moot for now; code paths kept in case prefetch returns.)

**Hotfixing live mid-cycle:** edit `browse.html` directly, push. Then port into `next.html` so it isn't lost at next promotion.

---

## CCA Digital Archives reference (condensed)

CCA's ISAD(G) hierarchy maps directly to our Wikibase: fonds = Richard Hunter fonds, series = collection (P79), file = project phase (P62), item = archive item. Core principle: invest description effort at the file/phase level, not the individual item. Full notes in `CLAUDE_archive_v1.02.md`.

---

## Session log

> Entries before the v1.06 promotion are **frozen** in `CLAUDE_archive_v1.06.md`
> (v1.05→v1.06), `CLAUDE_archive_v1.05.md` (v1.03→v1.05), `CLAUDE_archive_v1.02.md`
> (≤v1.02). Append new entries below; rotate by freezing a new archive at the next
> major promotion. Never delete.

---

### Sessions through v1.05.02 — frozen

See `CLAUDE_archive_v1.05.md` (and earlier `CLAUDE_archive_v1.02.md`). Built: full mobile-responsive design system; browse.html three-pane shell with progressive image loading, zoom/pan/rotate, researcher notes, dark mode, filter system; mobile bottom sheet with swipe nav; UI colour overhaul to bracket-style; staging system (next.html + LINE marker); v1.05 line — role system (Admin/Research/Public), local edit proxy, admin inline Wikibase editing, per-researcher row flags (mark/seen/note), info panel, keyboard scheme.

### v1.06 development line (test.01 → .58) — digested

Full per-test-version detail in `CLAUDE_archive_v1.06.md`. The whole v1.06 line was built and tested on `next.html` only; `browse.html` stayed at v1.05.02 throughout.

- **Publication ingest.** First multi-page publication added — `HH-HHC-0115` (Q490, 1986 Hunter portfolio). New `scripts/ingest_publication.py` (byte-for-byte masters + SHA-256 fixity manifest + 3 cover tiers + access PDF; dry-run default). New property **P143 "access copy" (url)** minted via new reusable `scripts/mint_property.py`.
- **PDF reader.** Started as native-iframe overlay, reworked into in-stage `pdf-mode` (canvas hides, PDF shows, foot bar repurposes), then switched to **bundled PDF.js v5.7.284** at `assets/pdfjs/` (~5.7 MB, pruned aggressively). `hh-pdfjs.css` hides everything outside the Minimal toolbar (page nav + zoom + zoom-mode) and themes the rest to match the foot bar. `viewer.mjs` patched: `HOSTED_VIEWER_ORIGINS` extended to allow `bturep.github.io`/`localhost` (re-apply on PDF.js upgrade). R2 CORS configured. PDFs uploaded with `Content-Disposition: attachment` so foot `↓ PDF` truly downloads. Foot-left: View PDF ↔ ✕ swap; foot-right: `↓ PDF` always when item has one.
- **Rotation persistence Part 1.** Property **P144 "display rotation"** (string) minted. `renderImage` seeds `zoomState.rotation` from stored value as base orientation. T-key stays casual (transient +90, no write). Admin-only `#zoom-rotsave` (`⤓ save`) writes net via `setStringClaim` (create-then-remove; net 0 ⇒ clear). Desktop image stage only; mobile/lightbox gap deferred to Part 2 bake.
- **Curated mode / exhibition lens Phase 1.** Static-JSON store (`curations/index.json` + `curations/<slug>.json` schema with `curator{name,role,affiliation,qid,bio,url,url_label}`, `slug`, `title`, `intro`, `items:[{id,pos,note}]`). Filter-panel "Curators" row (chips styled `pc-indigo`). Threshold overlay `#curator-pane` (about-pane pattern; `LENS_BLURB` + bio + link + "Enter exhibition →" CTA = confirm). `state.curation` drives `applyFilters` early-return (authored membership, `pos` order, sort+filter locked with toast). `#curation-card` intro card with exit button. Record pane swaps `renderRN → renderCuratorNote`. Index seeded to one curator (Brandon Poole) — placeholder JSON content pending real items/intro/notes. Esc cancels threshold overlay but does NOT exit active curation (card's exit is the way out). All gated behind `state.curation`/file presence — zero behaviour change when absent.
- **Catalogue SPARQL tightened.** P96 loosened required → OPTIONAL so stubs appear in list (hotfix immediately required: P79 made required so vocab/people/institutions don't pollute). Search haystack now includes `itemType` (typing "drawings"/"photographs" surfaces all of that type). "In the graph" section omitted when item has no phase.
- **Splash overhaul.** "Continue to archive" button replaces "Refresh archive data" in HHFA pane (styled `.cur-continue`, right of credits row). HHFA `×` ↔ Continue swap driven by `body.hh-splash`. Default landing item HH-CAA-0028. `body.refitting` hides `#canvas` during the 260ms panel-width transition + `setTimeout(280, fitToFrame)` so the splash-fit image doesn't visibly shrink. Search bar (`#search-toggle` magnifier + `.tr-sep`) + `/` shortcut restored next to fullscreen.
- **Repurposed Q463 (HH-HHC-0112) for Covenant Site Plan with Annotations.** Resolution of the 0112/0115 duplicate. Q463 wiped (`wbeditentity clear:1`), new claims written via `scripts/ingest_item.py`. Two new vocab items: Q491 (area "Kinhin Trail"), Q492 (phase "Covenant"). Bug caught mid-execute: vocab resolver was matching by label only — patched to require P1 instance-of match.
- **Cyan-cast JPEGs fixed.** Chrome-on-wide-gamut-Mac mishandled the `kip2300-v6-` scanner ICC profile (Safari/Firefox handled cleanly). Chased a false lead on `<meta color-scheme>` first. Resolved via `scripts/recolor_previews.py`: 254/441 R2 JPEGs converted kip2300 → sRGB; 183 had no profile (Chrome-safe); 0 errors. Three ingest/regen scripts patched with `-m sRGB Profile.icc` so this can't recur. Master TIFs untouched.
- **Placeholder asset** `assets/placeholders/image-missing_{thumb,prev,large}.jpg` (600/2000/3840 px, dark warm-near-black, `[ PREVIEW PENDING ]` text) for stub items whose P96 you want set to *something* visible.

Staging line ended this era at **next.html v1.06-test.58**, ready for promotion.

---

### 2026-05-20 — v1.06 promoted to live; v1.07 staging line opened (browse.html v1.06.00 · next.html v1.07-test.01)

**Promotion (documented Staging → Live cycle).** The full v1.06 line — built/tested across `next.html` v1.06-test.01→.58 — went live.

- Pre-promotion tidy on next.html (v1.06-test.58): default landing item HHC-0028 → **HH-CAA-0028** (original intent before mid-session complexity revert); pruned the 26-line ARCHIVED-2026-05-19 commented-out HTML block in the HHFA pane (Archive/Rights/Endpoints, superseded by the Wikibase Main Page link); updated two stale comments around the prefetch path (index.html is currently a thin redirect with no SPARQL prefetch, so the "must stay in sync" warning is moot — the code paths stay in case prefetch returns later). All visible behaviour unchanged.
- Promoted: `cp next.html browse.html`; `browse.html` `VERSION` → **`v1.06.00`**, browser tab title restored to "Browse Archive — Hunter House Foundation"; the curator JSON load on boot (`await loadCurationIndex()`) is **commented out** as the only structural divergence from next — `state.curations` stays empty, the curator row in `renderFilterPanel` is gated on `.length` and renders nothing, all the overlay/card/state code stays in place as dormant, **promotable later by uncommenting one line**. Tagged `v1.06.00` and pushed with `--tags`. `CACHE_KEY` auto-derives `hhf_v1.06.00`. Researcher data (`hhf_rn`, `hhf_marks`, `hhf_seen`) uses stable non-versioned keys — **no user data wiped**.
- `next.html` `VERSION` → **`v1.07-test.01`** (LINE: NEXT continues). next is byte-identical to the new live except VERSION and the curator JSON-load line.

**What is now live on the public site (v1.06.00):** splash overhaul (Continue-to-archive button, HHFA × ↔ Continue swap by `body.hh-splash`, default landing HH-CAA-0028, `body.refitting` hides `#canvas` during panel transition); in-stage PDF reader with bundled PDF.js v5.7.284 (`?file=…&theme=…&v=…`; minimal toolbar via `hh-pdfjs.css`; HOSTED_VIEWER_ORIGINS patched; R2 CORS allows `bturep.github.io` etc.; PDF objects carry `Content-Disposition: attachment`); admin display rotation **P144** with `⤓ save` (create-then-remove, net 0 ⇒ clear); SPARQL changes (P79 required, P96 OPTIONAL); "In the graph" section omitted when item has no phase; search haystack includes `itemType`; search bar + `/` shortcut restored. Browser tab "Browse Archive — Hunter House Foundation".

**Versioning note.** SESSION-level promotion milestone for the v1.06 line; tagged `v1.06.00` (not a MAJOR bump — git tag only, no GitHub Release per the snapshot rule).

**Version: browse.html `v1.06.00` (LIVE, tagged) · next.html `v1.07-test.01` (staging).**

---

### 2026-05-20 — Working memory rotated (CLAUDE_archive_v1.06.md frozen)

CLAUDE.md compacted at the v1.06 promotion line. The full file at browse.html v1.06.00 / next.html v1.07-test.01 was frozen verbatim to **`CLAUDE_archive_v1.06.md`** (FROZEN banner; covers v1.05.00 → v1.06.00 promotion). This file rewritten: every living-reference section + the ⚑ Active-context marker + the open-threads Pending block carried forward; completed Pending items (Rotation Part 1 BUILT, Curated Phase 1 BUILT, Cyan-cast FIXED) dropped — they're facts now, archive holds the detail; the v1.06 dev log (test.01→.58) collapsed to a single digest section; the v1.06 promotion entry kept in full as current live-state context; SPARQL query examples and other archive-already-covered detail trimmed. No code or version change — `browse.html` v1.06.00 and `next.html` v1.07-test.01 untouched. LINE stays **NEXT**.

---

### 2026-05-20 — Eric Gesinger Collection (EGC) drawings ingested (30 items, Q505–Q534)

Working LINE: **NEXT**. First full new-collection ingest end-to-end: workbook intake → R2 → Wikibase. Live `browse.html` untouched.

- **Intake workbook restructured.** Original `GES_intake.xlsx` (70 rows, mixed drawings + photos) collapsed to `EGC_intake.xlsx` (30 drawing rows): dropped 3 DUPLICATE-REMOVE rows, 36 photographs (separate intake later), and 1 invoice that wasn't a drawing. Renumbered HH-GES-####→HH-EGC-#### sequentially, ordered by phase (earliest-dated phase first) then by set# / date within phase. Resequenced Dining Room Table and Chairs set#s by date (the workbook had them numbered before I noticed the dates were out-of-order). Trimmed whitespace, merged "Living Room Chair Sketches" into "Living Room Sketches", renamed "Unknown" set → "Orphan", normalised drawing-type strings to canonical `plan; elevation; section; detail; axonometric` order. Date precision forced to `day` on all 25 dated rows; n.d. / n.d. on 5 undated. Phase names reconciled with Brandon's source folder names ("Channel Chair and Ottoman" not "Channel Chair", "Dining Room Table and Chairs" plural). Workbook saved + opened from `~/Desktop/` per the standing preview convention.
- **Folder ↔ workbook cross-check** against `/Users/brandonpoole/Downloads/237659_…_Scans_14May26`: 31 TIFs on disk vs 30 workbook rows (delta = invoice scan kept on disk, intentional drop). Expected-deleted dups (Scans 14/24/28) all absent. The 7 files Brandon sorted out of "Misc." all landed in real phases (Studio Table ×2, Living Room Sketches ×4, Orphan ×1). Every workbook row matched to a source TIF.
- **Built `scripts/batch_ingest_egc.py`** — workbook-driven batch driver modelled on `scripts/ingest_item.py`. Per row: build 3 sRGB-baked JPEG tiers via `sips -m sRGB`, master byte-for-byte + tiers to R2, Wikibase item with claims. Mints phases (P1=Q2) + missing drawing-type vocab (axonometric) once up-front. Phase lookup idempotent by label + P1; drawing-type vocab via hard-coded QID map.
- **First `--execute` crashed** on item 2 (Wikibase rejects duplicate (label, description) pairs in the same language): `Studio Table Sketch` / `drawing; EGC; 2005` already taken by Q503. Fix: include the archive ID in the description (`drawing; EGC; HH-EGC-0001; 2005`) — guarantees uniqueness across the collection. Also added a P2-based existence check before per-item creates so a partial-run can resume; but the check used `wbsearchentities` (label/desc index), which doesn't see arbitrary claim values like P2, so it failed to catch Q503 — Q503 ended up an orphan duplicate of HH-EGC-0001 (now Q505). **Q503 cleared via `wbeditentity clear:1`** and relabelled `(superseded duplicate of Q505)` with no claims — won't surface in browse.
- **Second `--execute` succeeded.** Outcome: 30 archive items `Q505..Q534` sequential, 9 phase items `Q494..Q502`, 1 new drawing-type item `Q493 axonometric`, R2 paths under `eric-gesinger-collection/{masters,previews,thumbs,large}/` = 120 objects (30 byte-for-byte masters + 90 sRGB JPEGs). Per-item claims: P1=Q88 drawing, P2 archive ID, P62 phase, P79=Q182, P80=Q201, P82 day precision /11 (skipped for n.d.), P86 zero-padded `NN of NN` where set#, P88 multi-value drawing types incl. Q493, P95/P96 R2 URLs.
- **Q182 mid-run mishap + the `Gesinger` spelling correction.** I "fixed" the Q182 label from `Eric Gesinger Collection` to `Eric Gessinger Collection`, assuming the single-s was a typo. Brandon corrected: single-s is canonical. Reverted Q182, swept Q493–Q534 for stray double-s in label/desc (none — items use the `EGC` abbreviation, never the surname), and bulk-replaced `Gessinger`→`Gesinger` in `about.html`, `archive.html`, `WIKIBASE.md`, `CLAUDE.md`, `scripts/batch_ingest_egc.py`, `scripts/make_ges_intake.py`, and `EGC_intake.xlsx` Reference sheet (existing files had been carrying the typo unnoticed). **R2 folder renamed `eric-gessinger-collection/` → `eric-gesinger-collection/`** via `rclone copy` (server-side CopyObject, 120 objects @ 2.305 GiB in 46 s, no local round-trip); then `wbsetclaimvalue` rewrote P95+P96 on Q505–Q534 (60 claim updates, 0 errors); then `rclone purge` deleted the old folder. New URLs spot-check HTTP 200.
- **Known: SPARQL index lag.** Wikibase Cloud's SPARQL endpoint indexes new items asynchronously (same lag as Q490 last session). browse/next won't surface EGC items in the catalogue until the index catches up — minutes to hours. Wikibase API direct lookups (`wbgetentities`) return everything correctly already.

**Open EGC threads:**
- 36 photographs (Mary McNeill Knowles) — separate intake later.
- Per-item `Notes` (P100), `Medium` (P91), `Physical location` (P142), `Scale` (P90), `Dimensions`, `Built status` (P92) all empty on the workbook (Brandon's archive pass).
- A few drawings may need rotation (T-key in next.html to preview; ⤓ save writes P144).

**Versioning:** no change — `browse.html` v1.06.00 / `next.html` v1.07-test.01 untouched (pure data + R2 + scripts/docs).

---

### 2026-05-20 — EGC live in browse + collection ⓘ popovers (browse.html v1.06.12 · next.html v1.07-test.13)

Working LINE: **NEXT**. The morning's EGC ingest (above) was R2+Wikibase only; this session wired browse to actually surface the items and added per-collection ⓘ popovers. Also a Gesinger spelling correction that cascaded across R2, Wikibase claims, and source files.

- **EGC visibility fix on live (live hotfix).** After yesterday's ingest the EGC items were in Wikibase but not appearing in `browse.html` / `next.html` — the catalogue `ARCHIVE_PFX` constant and SPARQL `FILTER(STRSTARTS…)` still listed `HH-GES-`, not `HH-EGC-`, so the prefix gate excluded all 30 items. `archiveAbbrev` map also missed `"eric gesinger": "EGC"`. Three edits per file (browse + next mirror); EGC items + EGC collection chip immediately surfaced. **v1.06.06 / v1.07-test.07**.
- **Furniture category — new property P145.** Minted **P145** "category" (wikibase-item, multi-value) + **Q535** "Furniture"; wrote `P145→Q535` on all 30 Q505–Q534 EGC items. Added P145 to the catalogue SPARQL SELECT + OPTIONAL, mapping into `state.items[].categories`, and renders as a `Category: [Furniture]` chip row (indigo `pc-indigo`) in both `renderMeta` (desktop) and `renderMobSheet` (mobile). Static spans for v1 — not wired as a filter button (skip-if-not-needed; trivial to add later via `state.filterCategory`). Chosen over piggy-backing on P87 (depicts area) because mixing "Furniture" with site-area values like "Living Room" / "Studio" would semantically muddy that vocabulary. **v1.06.07 / v1.07-test.08**.
- **Gesinger spelling correction across the project.** Yesterday I "fixed" Q182's label `Eric Gesinger Collection` → `Eric Gessinger Collection`, assuming the single-s was a typo. Brandon corrected: single-s is canonical (the Q209 person item was already correctly `Eric Gesinger`). Reverted Q182 (label/desc back to single-s, kept the `EGC` + `GES` aliases I'd added). Then a full sweep: `Gessinger`→`Gesinger` in `about.html`, `archive.html`, `WIKIBASE.md`, `CLAUDE.md`, `scripts/batch_ingest_egc.py`, `scripts/make_ges_intake.py`, and the `EGC_intake.xlsx` Reference sheet — existing files had been carrying the typo unnoticed. **R2 folder also renamed**: `eric-gessinger-collection/` → `eric-gesinger-collection/` via `rclone copy` (server-side S3 CopyObject, 120 objects / 2.305 GiB / 46 s, no local round-trip); then `wbsetclaimvalue` rewrote P95+P96 on Q505–Q534 (60 claim updates, 0 errors); then `rclone purge` deleted the old folder.
- **Three UI reversions** (small live hotfix). (a) "Record" label restored above the right pane — was emptied in `next.html` v1.06-test.48 when the [?] button moved to the top bar; re-added `<span class="l">Record</span>` in `.meta-head`. (b) HHFA wordmark no longer fades to opacity:0 when the about-pane opens; clicking it again just closes the pane. (c) [?] info button no longer hidden when the about-pane opens. Kept the `html[data-splash-init="1"]` pre-paint guard for both. **v1.06.08 / v1.07-test.09**.
- **[?] hidden during splash.** Mirrors the `#search-toggle` hide rule — while `body.hh-splash` is set there's no archive context to explain yet, so the affordance is dead weight. Adds `body.hh-splash #rec-info{display:none}` next to the search hide. **v1.06.09 / v1.07-test.10**.
- **[?] info pane stripped to shortcuts + credits.** Dropped the title "Hunter House Archive", the descriptive paragraph (site doesn't need to describe itself), the self-referential `? — This panel` entry, and the `.ip-note` callout-box for researcher tools (broke the panel's visual rhythm). Kept: Navigate keys, View keys, Researcher keys (only when unlocked), and the wordmark credits footer. **v1.06.10 / v1.07-test.11**.
- **Collection ⓘ popovers in the filter panel.** Decision discussion: per-collection info (HHC/CAA/EGC blurbs) doesn't belong in the per-item record pane — same text repeats on every item of that collection, which IS the saturation. Settled on a small ⓘ button next to each collection chip in the filter panel (the surface where users are already "thinking about collections"). Click chip = filter (unchanged); click ⓘ = popover anchored below it with title + blurb + Q-number (linked to Wikibase) + stats + custodian + optional external URL. Esc / outside-click / re-click closes. Implemented via a new `COLLECTION_INFO` JS const + an `infoMap` parameter on the `group()` chip-row helper (Collection passes it; other rows opt in later). CAA description pulled from `searcharchives.ucalgary.ca/richard-hunter-accession` (344 drawings + 62 photographs at UCalgary, donations 2019 + 2021, predominantly 1955–2010). HHC + EGC drafted from Brandon's prose; FUL placeholder pending content. **v1.06.11 / v1.07-test.12**. Then a content correction: Gesinger only built the East Wing Dining Room Chairs, not the Owl Chairs (Owl Chairs in EGC are Hunter drawings; the build attribution belongs elsewhere). **v1.06.12 / v1.07-test.13**.
- **Memory protocol additions** to the Pending block: (a) Wikibase revision-history cleanup as a future option (per-item `Special:RevisionDelete` via sysop, or instance reset); (b) R2 metadata sidecars — write a per-item JSON sidecar at `{collection}/metadata/{ARCH_ID}.json` so R2 holds a self-contained, Wikibase-independent backup. Both flagged "do when the archive settles".
- **Housekeeping shipped**: `.gitignore` added (`__pycache__/`, Excel `~$` lock files); `EGC_intake.xlsx` archived to R2 at `eric-gesinger-collection/intake/EGC_intake.xlsx` as a working-state snapshot (will be regenerated when canonical entries are populated in the next intake cycle); confirmed HHC + CAA have no equivalent intake files (predate the workbook workflow).

**Version line at session close: browse.html `v1.06.12` (LIVE) · next.html `v1.07-test.13` (staging).**

#### Follow-up after session-close — built-by data + inline category edit (v1.06.13 / v1.07-test.14)

Brandon logged back in to wrap two loose ends from the design discussion:

- **P140 built-by writes** — the property was plumbed end-to-end in browse/next but had zero values anywhere in the wikibase. Filled in for the EGC pieces Gesinger actually built: P140 → Q209 (Gesinger) on the 9 Channel-Chair-phase items (HH-EGC-0014..0019) + Dining Room Chairs (0021, 0022) + East Wing Living Room Side Table (0023). The Dining Room Table (HH-EGC-0020), Owl Chairs, and the rest of EGC have no built-by attribution (pre-Gesinger, unbuilt, or unknown). **Kitchen Stool** flagged as not-yet-in-archive (drawing exists per Brandon; future intake).
- **Designer (P141) deferred.** Hunter designed all the EGC pieces, so a separate designer tag isn't relevant yet; Pending block already carries the entity-search-picker task for when P140/P141 need to surface persons not yet in vocab.
- **P145 Category inline-editable.** Added `"Category": { pid: "P145", key: "categories", multi: true }` to the EDITABLE map in renderMeta; the existing generic multi-value picker (P88/P87 pattern) handles add/remove with no other changes. Category row now renders for admins even when empty (matches the Areas / Drawing-type fallback). One limitation: `getVocab(P145)` returns only in-use values, so the picker currently shows just "Furniture" — minting a new category (e.g. Architecture) still needs the bot. The Pending entity-search-picker task covers the eventual fix for P140/P141/P145 all at once.

**Final state: browse.html `v1.06.13` (LIVE) · next.html `v1.07-test.14` (staging).** Time already logged (HH-T-34, 6.0h Research, batch HH03) — this follow-up rolled into that block.

#### Follow-up #2 — admin editing surface filled out (v1.06.18 / v1.07-test.19)

Brandon's afternoon ask: "is there functionality I'm missing for such a direct interface with the wikibase?" Took a pass at the four gaps that mattered most:

- **More fields editable inline.** EDITABLE map expanded from 8 → 15 entries. Newly editable: P80 Creator (row label is dynamic — "Drawn by" / "Photographed by" / "Creator" — and EDITABLE keys off the rendered label so the ✎ button shows up correctly per item-type), P141 Designed by, P140 Built by (now a multi-value array — see below), P145 Category, P142 Location, P86 Sheet (broken out from the inline-with-Phase span into its own row), P91 Medium, P90 Scale, P89 Use. New plumbing for P90/P91 (SPARQL select + OPTIONAL + mapping); P89 was already pulled but unrendered. New string-input picker branch in openFieldPicker (`data-kind="string"`) for the prose-y short fields — Enter saves, blank clears. Editable rows render with `EM` placeholder for admins even when empty (matches Areas / Drawing type pattern), so a field with no value can be set without leaving browse.
- **Built by → multi-value array.** P140 was plumbed as single string but Wikibase supports multi-value. Restructured: `item.builtBy: string|null` → `item.builtBy: []`; mapping accumulator, filter check, search hay, mobile + desktop renders all updated to iterate. The chip+× multi-value picker (P88/P87 pattern) now handles add/remove cleanly. Same restructure could apply to P80 creator and P141 designed-by later if the data model needs multi (e.g. multiple photographers); for now both stay single-valued.
- **Mint-new affordance in the picker.** When the typed text doesn't match any existing vocab, `+ mint "X" as <noun>` appears beneath the empty list. Click → two-step confirm dialog (matches the existing Phase-rename guard pattern). Confirm → `wbeditentity new=item` through the proxy → auto-select. Per-property `MINT_POLICY` maps each editable property to a kind ("vocab" mints with templated description and optional P1 instance-of; "person" mints label-only and prompts admin for a one-line description) and a noun ("Area", "Phase", "Category", "Builder", "Designer", "Person"). Closed vocabularies (P1 item-type, P92 built-status, P79 collection) deliberately absent — those shouldn't be casually extended. **`scripts/edit_proxy.py` ALLOWED_ACTIONS gained `wbeditentity`**; restart required before mint will work locally.
- **Notes (P100) reassigned.** Repurposed from the dead curator-notes role to a public-facing cataloguer's prose note. Multi-line — new `data-kind="text"` branch in openFieldPicker that uses `<textarea>`, ⌘↵ saves (↵ inserts newline). Renders as the first row above Date, with `.hh-note-text` CSS that preserves whitespace and line-breaks. Distinct from private researcher notes (localStorage) and curator notes (curation JSON).
- **Bulk-edit mode.** Cmd/Ctrl-click toggles individual list rows into `state.bulkSel`; Shift-click does range from the anchor. Selected rows get a red left-edge inset stripe. A `bulk-bar` (mirrors the mark-bar pattern) appears above the list when selection is non-empty: "N selected · edit ▾ · clear". Edit opens a popover with a property list (`BULK_OPS` — 20 operations: add/remove multi, set single, set string, set text, set date), then a value picker that re-uses the same patterns as inline editing (chip search, string input, textarea, date input — all with mint affordance where applicable), then a confirm preview ("Add Furniture on 12 items?" with a sample list of IDs), then sequential application with per-item progress toasts. Errors surface in the final toast (`Done · N ok, M failed`) and per-item failures don't block the loop. Esc clears selection. Admin-only.

**Caveats / honest limits of what shipped:**
- The mint-new and bulk-edit paths both call the proxy serially per item. For 30+ items, the apply loop takes a few seconds and the toast progresses — fine, but not parallelised. Wikibase's API rate limits are generous enough that this isn't urgent.
- `getVocab(pid)` caches per-property; on mint we invalidate that cache. Cached vocab is per-page-load so the new item shows up the next time the picker opens that property.
- Single-value pickers (Creator, Designed by) still don't have a "clear" affordance — they replace only. Add via mint, switch via picker, but to actually unset you'd need to use the bot. Could add an explicit `× clear` button to the single-value picker later.
- Confirmed mint policy excludes P1 item-type and P92 built-status (closed vocabs) by leaving them out of `MINT_POLICY`. The mint affordance never appears for those rows even if the typed text doesn't match — by design.

**Version line: browse.html `v1.06.18` (LIVE) · next.html `v1.07-test.19` (staging).**
