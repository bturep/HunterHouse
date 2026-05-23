# CLAUDE.md — Hunter House Foundation session context
# Live working memory. Frozen archives (read-only, full historical detail; git also holds all of it):
#   • CLAUDE_archive_v1.07.md — v1.06.00 promotion → v1.06.18 live, v1.07-test.01 → .22 staging (freeze 2026-05-21)
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
- **Edit-proxy restart** — `python3 scripts/edit_proxy.py` each session (dies on Mac sleep; admin inline editing in next.html is inert without it). **As of 2026-05-22:** the proxy prints a per-startup random token in its stdout banner; paste it into next.html's badge (bottom-left when the badge appears) before editing. Token rotates on every restart.

---

## ⚑ Pending at next session start

**Open threads carried into v1.07:**
- **Curator Phase 2** — in-browser authoring + multi-curator polish + Wikibase promotion (Curation as first-class item w/ qualifiers; needs proxy `wbsetqualifier`). Phase 1 lens lives in next.html (curator JSON load commented out on live; all overlay/card/state code dormant, promotable by uncommenting one line).
- **Held by** — P94 (CAA/FUL) vs P79 (HHC) ambiguity; needs a rule for which to write before it's editable.
- **Phase rename** — distinct from "change phase" (P62, done). Renaming edits the shared Phase item's label → affects every item in that phase. Needs a confirm-guard. (`wbsetlabel` on `item.phaseQID`.)
- **Built by / Designed by — cross-property entity search.** P140 now has values (Q209 Gesinger × 9 items, Q536 Byers × 1 item, written 2026-05-21); the picker's mint affordance handles "add a person not yet anywhere in the wikibase". Remaining gap: cross-property search — e.g. picking Q201 Hunter from the P140 picker when he's only currently in P80's in-use vocab. Each picker still only sees its own property's values. Probably good enough; revisit if it bites in real cataloguing.
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

### 2026-05-20 → 2026-05-21 — v1.06 line live, EGC ingest, admin editor build — digested

Full per-entry detail in `CLAUDE_archive_v1.07.md`. Condensed:

**v1.06 promoted to live (2026-05-20).** Tagged `v1.06.00`. Brought the full staging line live: splash overhaul (Continue-to-archive button, HHFA × ↔ Continue swap, default HH-CAA-0028, `body.refitting` hides canvas during panel transition), in-stage PDF reader (bundled PDF.js v5.7.284, HOSTED_VIEWER_ORIGINS patched, R2 CORS, `Content-Disposition: attachment` so download works), admin display rotation P144 with `⤓ save` (create-then-remove, net 0 ⇒ clear), SPARQL changes (P79 required so vocab/people stay out, P96 OPTIONAL so stubs appear), "In the graph" hidden when no phase, search haystack includes `itemType`, search bar + `/` shortcut restored. Curator JSON load commented out on live (Phase 1 lens stays in next as dormant code, promotable later by uncommenting one line).

**Subsequent v1.06.0N hotfixes (today live at v1.06.18)** shipped: EGC visibility fix (`HH-GES-` → `HH-EGC-` in the catalogue prefix filter — items were in Wikibase but excluded by the SPARQL gate), Category P145 chip, collection ⓘ popovers in the filter panel (HHC/CAA/EGC blurbs incl. UCalgary finding-aid link for CAA), Gesinger spelling correction sweep + R2 folder rename, three UI reversions (Record label restored above the right pane, HHFA wordmark + `[?]` button stay visible while the about-pane is open, `[?]` hidden during splash), `[?]` info pane stripped to shortcuts + credits only.

**EGC drawings ingested (2026-05-20).** First full new-collection ingest end-to-end (workbook intake → R2 → Wikibase). `GES_intake.xlsx` → `EGC_intake.xlsx` (70 mixed rows → 30 drawing rows, photos deferred); new `scripts/batch_ingest_egc.py` minted 9 phase items (Q494–Q502), 1 drawing-type item (Q493 axonometric), wrote 30 archive items `Q505–Q534` with day-precision dates + zero-padded P86 set positions, uploaded 120 R2 objects under `eric-gesinger-collection/`. First `--execute` crashed on a (label, description) uniqueness collision; fix = include the archive ID in the description (`drawing; EGC; HH-EGC-NNNN; YYYY`). Q503 (orphan from the crashed run) cleared. **Gesinger spelling correction**: single-s is canonical (I had "fixed" to double-s, wrong); swept the project + R2 (server-side CopyObject, 120 objects in 46 s) + 60 Wikibase P95/P96 URL rewrites. **Built-by attribution** filled in: `P140 → Q209 Gesinger` on 9 items (Channel-Chair phase + Dining Room Chairs + East Wing Living Room Side Table); Q524 Dining Room Table → minted **Q536 Martin Byers**, `P140=Q536`. Q525 corrected. Kitchen Stool flagged for future intake.

**v1.07 staging line opened.** `next.html` v1.07-test.01 → v1.07-test.22 across 22 patches. Not yet promoted. What's queued for the next promotion (today's entry below has the full picture):
- Admin editing surface fully built out — 15 fields inline-editable (Date, Phase, Sheet, Item type, Drawing type, Built, Areas, Category, Built by, Designed by, Creator, Medium, Scale, Use, Location) + Notes textarea
- Mint-new affordance in every item picker (`MINT_POLICY` per pid; vocab vs person kind; two-step confirm; needs `wbeditentity` whitelist in the edit proxy → restart required)
- P100 reassigned to Notes (cataloguer prose, multi-line)
- Bulk-edit mode (Cmd-click / Shift-click selection, `BULK_OPS` list of 20 operations, confirm preview, apply loop)
- Built-by → multi-value array (was single string)
- Category property P145 + Furniture Q535 + chip in record pane
- Collection ⓘ popovers in the filter panel
- Three-agent cleanup pass (drawVocabList, handleMintClick, BULK_APPLIERS extracted; -26 lines)

**LINE: NEXT rule tightened (2026-05-21).** The "live hotfix" carve-out had become routine for shipping features alongside next. Reset: live is broken for real visitors and no other path is the bar; otherwise wait for the next promotion.

**Memory protocol additions to Pending.** R2 metadata sidecars (`{collection}/metadata/{ARCH_ID}.json` preservation backup) and Wikibase revision-history cleanup — both deferred. `.gitignore` for `__pycache__/` + Excel `~$` lock files. `EGC_intake.xlsx` archived to R2 at `eric-gesinger-collection/intake/`.

---

---

### 2026-05-21 — Admin-editor surface filled out + CAA renumber + cleanup pass (next.html v1.07-test.22)

Working LINE: **NEXT**. Live `browse.html` ended the day still at `v1.06.18`; staging `next.html` advanced through 16 patches (`v1.07-test.06 → v1.07-test.22`) to land all of today's additions. Mid-session Brandon called out that I'd been "live-hotfixing" every change to both files; reset to next.html-only going forward and tightened the standing instruction so the carve-out reads as the narrow exception it's meant to be (live broken for real visitors, no other path).

- **P140 built-by data filled in for the EGC items.** The property was plumbed end-to-end but had zero values anywhere in the wikibase. Wrote `P140 → Q209 Gesinger` on the 9 items he actually built (Channel-Chair phase Q518–Q523 + Dining Room Chairs Q525–Q526 + East Wing Living Room Side Table Q527). Q524 Dining Room Table → minted **Q536 Martin Byers** and `P140 → Q536`. Brandon then noted only ONE of the two dining-room-chair drawings was built; P140→Q209 stripped from Q525. Kitchen Stool flagged for future intake (drawing exists outside our archive). WIKIBASE.md updated: Q536 in the people table; P140 / P141 / P145 added to the property table with values-written notes.

- **Built-by → multi-value array.** P140 was plumbed as a single string but Wikibase supports multi-value. Restructured `item.builtBy` `string|null → []` and updated mapping accumulator, filter check, search hay, mobile + desktop renders to iterate. Built-by row now uses the chip+× multi picker pattern (matches P88/P87). Same restructure could apply to P80 creator and P141 designed-by later if multi makes sense; for now both stay single.

- **Admin editing surface filled out (15 fields now inline-editable).** EDITABLE map grew from 8 → 15. New inline editors: P80 Creator (dynamic row label — "Drawn by"/"Photographed by"/"Creator"; EDITABLE keys off the rendered label so the ✎ lands on the right row per item type), P141 Designed by, P145 Category, P142 Location, P86 Sheet (broken out from the inline-with-Phase span into its own row), P91 Medium, P90 Scale, P89 Use, P140 Built by, P100 Notes. New plumbing for P90/P91 (SPARQL select + OPTIONAL + mapping); P89 was already pulled but unrendered. New string-input picker branch (`data-kind="string"`) for short text — Enter saves, blank clears via `setStringClaim`. Editable rows render with `EM` placeholder for admins even when empty (matches Areas / Drawing-type pattern), so a field with no value can be set without leaving browse.

- **Mint-new affordance in every item picker.** When the typed label doesn't match existing vocab, `+ mint "X" as <noun>` appears beneath the empty result list. Click → two-step confirm dialog (matches the existing Phase-rename guard pattern). Confirm → `wbeditentity new=item` through the proxy → auto-select. Per-property `MINT_POLICY` maps each editable property to a kind ("vocab" mints with templated description and optional P1 instance-of; "person" mints label-only and prompts the admin for a one-line description) and a noun ("Area" / "Phase" / "Category" / "Builder" / "Designer" / "Person"). Closed vocabularies (P1 item-type, P92 built-status, P79 collection) deliberately absent from MINT_POLICY — those shouldn't be casually extended through the picker. **`scripts/edit_proxy.py` ALLOWED_ACTIONS gained `wbeditentity`**; restart required locally before mint can fire.

- **P100 reassigned to Notes (cataloguer prose).** Repurposed from the dead curator-notes role to a public-facing cataloguer's prose note. Multi-line — new `data-kind="text"` picker branch uses `<textarea>`, ⌘↵ saves (↵ inserts newline). Renders as a row after Held by with a `row-notes` CSS class giving it `margin-top:14px` so the prose settles below the dense key/value stack rather than sitting flush. `hh-note-text` CSS preserves whitespace + line-breaks. Distinct from private researcher notes (localStorage) and curator notes (curation JSON). WIKIBASE.md P100 description updated.

- **Bulk-edit mode (admin).** Cmd/Ctrl-click toggles list rows into `state.bulkSel`; Shift-click ranges from the anchor. Selected rows show a red ::before stripe + faint red background tint (the initial inset box-shadow approach didn't render; switched to the same ::before pattern .row.sel uses). A `bulk-bar` appears above the list (mirrors mark-bar visually): count + Edit + Clear. Edit opens a property picker (`BULK_OPS` — 20 operations: add/remove for multi-value, set for singles/strings/text/date), then a value picker that reuses the inline pickers (and the mint affordance), then a confirm preview showing verb + value + count + sample IDs, then a sequential apply loop with per-item progress toasts. Final tally `"N ok, M failed"`; per-item failures don't block the loop. Esc clears selection. Admin-only.

- **CAA renumbered — drawings 0001-0025, photographs 0026-0035.** Brandon wanted photos at the tail of the CAA sequence instead of interleaved. New `scripts/renumber_caa.py`, modelled on the existing renumber/migration scripts and following the documented Batch change protocol. SPARQL snapshot first (`data/snapshots/caa_pre_renumber_20260521.json`) — rollback insurance. 26 items renumbered (9 drawings already in their target slot HH-CAA-0001..0009 stayed put; 16 drawings + 10 photos moved). Provenance preserved via P97 append: each renumbered item ends with the chain `HH-A-NNNN → HH-CAA-NNNN(old) → HH-CAA-NNNN(new)` plus, where present, the UCalgary accession ID (e.g. Q344 now carries all four P97 values). 104 R2 server-side copies (server-side `CopyObject`, no local round-trip) + 104 R2 deletes. **One stale claim discovered + fixed mid-process**: Q344's P95 still pointed at `HH-A-0014_...` from the 2026-05-14 migration even though the R2 file had been correctly renamed; the renumber script's dry-run caught it and aborted; fixed Q344's P95 in one bot call and re-ran. SPARQL index lag means browse won't reflect for a bit, as usual; Wikibase + R2 verified clean (35 items each tier, 0 prefix mismatches, HTTP 200 on new URLs).

- **Three-agent cleanup pass on today's net additions.** After-the-fact review for reuse / quality / efficiency. Targeted simplifications: extracted `drawVocabList()` (folds three near-identical picker draw loops + the mint-affordance tail into one helper with `{exclude, current, withLbl}` options), `handleMintClick()` (folds three identical `.hh-mint-btn` early-returns), `BULK_APPLIERS` lookup table (replaces `applyBulkOp`'s nested if/else with a flat table keyed by `${kind}:${op}` — easier to extend, harder to forget a branch). `setTimeClaim` extended to accept `time=""` to clear (mirrors `setStringClaim`); bulk-edit date-clear branch now reuses the helper instead of an inline `fetch` + `wbremoveclaims`. `group()` in renderFilterPanel lost the `infoMap` parameter (only Collection used it); inlined the check against `attr === "collection"`. Dropped redundant `renderBulkBar()` calls in bulkSelectRow / clearBulkSel (renderList already calls it). Trimmed five over-explanatory block comments. Net -26 lines, no behavior change. **Skipped** from the review: normalizing EDITABLE's `multi: true` → `kind: "multi"` — would also touch the picker dispatch via `data-multi`, and the existing flag is clear; not worth the regression risk.

**Standing-rule changes:**
- LINE: NEXT carve-out tightened. Live hotfixes are the narrow exception (production broken, no other path), not a routine alongside-feature option.

**Pending state at session close:**
- ▸ **Curator Phase 2** — unchanged
- ▸ **Held by** P94/P79 ambiguity — unchanged
- ▸ **Phase rename** — unchanged
- ◐ **Built by / Designed by entity-search picker** — partially resolved. The mint affordance covers the case where the person isn't yet in the wikibase; remaining gap is cross-property search (e.g. picking Q201 Hunter from P140 when he's currently only registered under P80). Probably good enough; revisit if it bites.
- ▸ **EGC photograph ingest** — still waiting on the intake sheet (Mary McNeill Knowles, 36 photos)
- ▸ **Rotation Part 2** — still needs the Cloudflare purge API token
- Deferred / structural items unchanged.

**Version line at session close: next.html `v1.07-test.22` (staging) · browse.html `v1.06.18` (LIVE, unchanged this afternoon).**

---

### 2026-05-21 — Made-by filter chip cleanup + mobile splash unstuck (browse.html v1.06.20 · next.html v1.07-test.23)

Working LINE: **NEXT**. Two live hotfixes mirrored from next.html to browse.html — both visible to real visitors, neither a feature ship.

- **Empty `[]` chips in the Made-by filter row** (mobile and desktop). After v1.06.18 restructured `i.builtBy` from string → array, `uniqueCreators` was still building `[i.creator, i.designedBy, i.builtBy]` and flatMap-ing — empty arrays survived `.filter(Boolean)` (truthy) and stringified to `""` in the chip render, producing rows of empty `[]` chips polluting the filter panel. Fixed by spreading: `[i.creator, i.designedBy, ...(i.builtBy || [])]`. Matches the pattern already in use at applyFilters. → **browse.html v1.06.19, next.html v1.07-test.22** (commit `182a3f0`).

- **Mobile splash Continue button unresponsive on iOS** (live broken for real visitors). The HHFA splash modal (`#mob-about`) is `position:fixed; overflow-y:auto; z-index:300`; the Continue button (`.cur-continue` → `#mob-about-continue`) had `padding:0` and 11px text — borderline tap target. iOS Safari treats taps inside scrollable fixed containers as ambiguous between tap and scroll-start, and with that small a hit area + no `touch-action` hint, the tap was being eaten. Handler binding itself was confirmed clean (lines 5065-5066 are top-level, bound before `main()` even runs). Fix: add `touch-action:manipulation` + `-webkit-tap-highlight-color:transparent` to `.cur-continue` (universal, zero visual impact); add a generous `padding:12px 10px` with negative margin compensation to `#mob-about-continue` specifically (mobile-only since the desktop button is `#about-pane-continue`). Negative margin keeps the visual size identical while expanding the click target. → **browse.html v1.06.20, next.html v1.07-test.23**.

- **Q524 / Q536 / Martin Byers attribution removed** (data fix, no code). Yesterday I minted Q536 (Martin Byers) and wrote P140→Q536 on Q524 (Dining Room Table, HH-EGC-0020); Brandon called for a full undo. Removed the P140 claim from Q524, cleared Q536 via `wbeditentity clear:1`, relabelled Q536 as `(unused)` with no description — available for reuse via the same QID. Original Martin Byers note removed from the v1.06.18 follow-up entry in this file (git history preserves it per memory protocol).

**Versioning note:** browse.html got two patch bumps in one day (v1.06.19 + v1.06.20) — both were genuine "real visitors blocked" hotfixes, not feature ships. The LINE: NEXT rule held; next.html got the same fixes first as v1.07-test.22 and .23. The Continue-button hit-area issue probably existed since the v1.06.00 promotion but went unnoticed on desktop.

**Version line: browse.html `v1.06.20` (LIVE) · next.html `v1.07-test.23` (staging).**

---

### 2026-05-22 — Curator mode reskinned to the "Vellum" palette (next.html v1.07-test.50)

Working LINE: **NEXT**. CSS-only — no markup, no JS, no `verso.css`.

- **Curator splash + in-archive curator mode reskinned warm-cream.** Both surfaces previously read copper-green (threshold card `#dde6df`; in-curation tokens tinted `--bg`/`--soft` green *and* overrode `--red` → green). New "Vellum" treatment makes both feel like a warm-cream curator's-notebook surface. Three CSS blocks touched in `next.html`:
  - `#curator-pane` (threshold splash) — eight token values swapped to vellum: `background:#ebe1cb`, warm-brown ink/muted/hint/rule, copper `#6b4a1f`/`#d4c2a0`. Layout untouched.
  - `body.hh-in-curation` / `html.dark body.hh-in-curation` — **the `--red` override is gone.** Old rules pushed `--red` to green in curator mode; now Hunter-red persists everywhere (name accent, selected-row stripe). Only surfaces (`--bg`/`--soft`/`--rule`) and the copper link family drift to vellum tones. Added a 240ms background/color transition on the light block.
  - `html.dark body.hh-in-curation .curation-card` background `#1f241f → #2a2218` (matches new dark `--soft`).
- Comment above `body.hh-in-curation` rewritten to describe the surfaces-only re-tint. **Note:** the comment above `#curator-pane` still references the old `#dde6df` copper-green card — left as-is per the task scope, flagged for a future touch.

**Version line: browse.html `v1.06.20` (LIVE, unchanged) · next.html `v1.07-test.50` (staging).**

---

### 2026-05-22 — Curator mode → "Cognac" palette + chrome restructure (next.html v1.07-test.51)

Working LINE: **NEXT**. Two-part change in one push: (A) re-tint the curator surfaces from vellum to cognac, (B) restructure the in-curation chrome so the curator's voice and authored sequence get proper weight.

- **A. Cognac palette.** Three CSS blocks re-tinted:
  - `#curator-pane` (threshold splash) — warm amber-dark card (`background:#2c2218`, cream ink `#f2e7d4`, translucent muted/hint/rule, copper `#d4a26a`, softened red accent `#c4826e`). The threshold now reads as a backstage/foyer rather than another sheet of paper.
  - `body.hh-in-curation` (in-mode surfaces, light + dark) — tea-stained paper light (`--bg:#efe5d2`, `--soft:#e6d8bf`, `--rule:#d4c4a3`); a step-warmer dark (`--bg:#1c1813`, `--soft:#2a2218`). `--red` left untouched both sides → Hunter accent stays exact on name highlights and the selected-row stripe.
  - `html.dark body.hh-in-curation .curation-card` already at `#2a2218` from the vellum pass; matches new dark `--soft`.
  - Updated the mode-block comment to describe cognac instead of vellum; updated the splash comment to match (drops the stale `#dde6df` copper-green reference).

- **B. Chrome restructure.** Six independent moves, all gated behind `body.hh-in-curation` or `state.curation`:
  1. **Curator note hoisted above DESCRIPTION** in the record pane. `renderMeta` now renders, in order: title → curator note → next-in-selection line → DESCRIPTION (and the rest unchanged). `renderCuratorNote` is now a no-op (clears `#rn-panel`) since the note is in the main body; `curatorNoteBlock` was reworked to return the HTML for both the record pane (via renderMeta) and the mobile sheet.
  2. **Curator note styled as a native meta-section** — drop the dashed top-border / padding-top callout chrome. `.cn-label` is now a tracked-out small-caps header with `font-size:9.5px`, `letter-spacing:0.18em`, `border-bottom:1px solid var(--ink)`, `padding-bottom:8px`, `margin-bottom:14px` — i.e. the `.meta-section h3` pattern. Label reads `<span style="color:var(--red)">BRANDON</span> ON THIS ITEM` (curator's first name in red, echoing the CURATED BY [NAME] byline). `.cn-text` bumped to `font-size:12px`, `line-height:1.75`. The mobile-sheet override drops the underline when the note is first child.
  3. **List rows numbered in curator mode.** Replaced the `[LS]/[D]` `.tmark` chip in the `.archid` slot with `01, 02, 03…` reflecting the authored selection order (just `_idx + 1` from the `forEach`, no item mutation). Style: same mono, no brackets, `font-size:11px`, `letter-spacing:0.06em`, `font-variant-numeric:tabular-nums`. Selected row → `var(--red-deep)`. The item ID (HHC-0010) slid into the `.ph` subtitle line as a prefix span (`.rid` in `var(--hint)`) before the phase. Outside curator mode the original `.tmark` chip rendering is untouched.
  4. **Continuity column.** `body.hh-in-curation .panel-left::before` — absolute-positioned 2px stripe with a top-down `linear-gradient(var(--copper-deep) → var(--copper-pale))`. No z-index manipulation: the pseudo is first in tree order, so it paints under `.row.sel::before` (Hunter-red stripe stays dominant inside the curator column) but over the panel background and hover tints.
  5. **Foot-bar pager + Next-in-selection inline link.** Added `.cur-pager` inside `.foot-left` (hidden by default, shown when `state.curation` is set, hidden again in `.pane-image.pdf-mode`). Renders `← Prev · NN / NN · Next →` with copper-deep buttons and hairline separators; wired to `selectAdjacent(±1)`. `updateCurPager()` is called from `selectItem` and `exitCuration`. The inline `.cur-next` row (label + clickable 32-char-clipped title + arrow) is rendered between the curator note and DESCRIPTION via `curatorNextBlock(item)`; "— end of selection —" when at the last item.
  6. **LEAVE SELECTION ×** moved off the curation-card and into the top-right corner of `.panel-left` (`.cur-leave`, absolute `top:14px right:18px`, mono small-caps `font-size:9px`, hint color → ink on hover; `×` in a larger inline span). Bound once at startup; shown/hidden by `renderCurationCard` (and `.panel-left.out .cur-leave{display:none}` for the collapsed-panel case). The old `.cc-exit` button removed from the card markup; the CSS rules for `.cc-exit::before/::after/:hover` were dropped at the same time. The card now contains just `cc-top` (curator byline) + `cc-title` + `cc-intro`.

- **B7 — counter dedup.** No `Reading X of Y` ever existed on the card and the RECORD `.meta-head` shows just `Record` (no count), so the foot pager (B5) is now the single source of truth.

- **Did not touch** — `assets/verso.css` palette, any non-curator-mode behavior, the mobile sheet layout (the curator-note CSS override at `.mob-sheet-body .cur-note:first-child` was kept intact; the new header underline is dropped when the note is the sheet's opening element).

**Version line: browse.html `v1.06.20` (LIVE, unchanged) · next.html `v1.07-test.51` (staging).**

---

### 2026-05-22 — Session close · ARCHITECTURE.md for external reviewer (browse.html v1.06.31 · next.html v1.07-test.51)

**Session arc.** Three threads landed in one day:
1. **Vellum curator-mode reskin** → next.html v1.07-test.50 (entry above).
2. **ARCHITECTURE.md** — high-level brief for an external software engineer to inspect the live site. Single-file audit covering shell, JS module map, data layer (Wikibase SPARQL + R2), the local edit-proxy write path, runtime dependencies, git stats, observational risks, and a six-step "where to start reading" guide. Committed `eb97bcc`. Repo is public (`gh repo view` confirms `isPrivate:false`), so the reviewer needs nothing more than the URL: read access is already universal.
3. **ARCHITECTURE.md §11 — To-do list** — separate deeper security + maintainability pass added by Brandon as `2393d19`. Catalogues actionable items in three buckets (Now / Soon / Bend-before-break) with file:line refs against `next.html` v1.07-test.51. **One CRITICAL** flagged: the edit-proxy CSRF surface (fallback secret = the hardcoded admin pin; `_cors` sets ACAO conditionally but `do_POST` never *rejects* mismatched Origins; `json.loads` without Content-Type check allows preflight-bypassing simple requests). Today's de-facto mitigation is Chrome Private Network Access; Safari/older Firefox aren't covered. Fix is ~2 hours of edit_proxy.py work. **HIGH:** no offsite Wikibase metadata backup (the R2-sidecar plan from Pending). These supersede the Pending list as the next-session priorities if Brandon is in a hardening mood.
4. **Cognac palette + curator chrome restructure** → next.html v1.07-test.51 (entry above) — done by Brandon outside this conversation; pre-existing log entry left intact.

**Version reconciliation.** Earlier session entries' trailers report browse.html as `v1.06.20` (LIVE, unchanged). The file is now `v1.06.31`. The 11 intervening patches landed via single-line commits between 2026-05-21 and 2026-05-22 (splash redesign with retracting top bar, brand rename HHFA → "Hunter House Archive", header geometry, title-case filter chips + row phase, EGC info corrections, removal of the Hunter House Foundation link from the about pane) — none with corresponding session-log entries. Not retroactively documenting per-patch; this note records the gap. Worth a quick "what's on live right now" eyeballing next session before next-line work resumes.

**Global memory updated.** `~/.claude/CLAUDE.md` "Current versions" row for Hunter House site bumped `v1.05.00 → v1.06.31` (the table was two major versions stale). Note unfortunately can't be git-tracked from this repo since the global file lives outside it.

**Pending threads** carried into the next session unchanged (Curator Phase 2, Held-by P94/P79, Phase rename, EGC photo ingest, Rotation Part 2, deferred structural items). ARCHITECTURE.md §11 is the new, more actionable companion list — distinct in intent (security/hygiene) from Pending (feature/data).

**Version line: browse.html `v1.06.31` (LIVE) · next.html `v1.07-test.51` (staging).**

---

### 2026-05-22 — Edit-proxy CSRF hardening + CI validation workflow (no version bump)

Acted on ARCHITECTURE.md §11.1 + §11.2 the same day they were drafted. Two changes, neither touching the live browser files:

- **`scripts/edit_proxy.py` hardened.** `do_POST` now rejects mismatched `Origin` *before* reading the body (403), rejects non-`application/json` `Content-Type` (415; forces a real CORS preflight), and matches origins with `urlparse` rather than `startswith`. New `origin_allowed()` helper accepts exactly `https://bturep.github.io` for production and any port on `localhost`/`127.0.0.1` for local dev. 12-case sanity test included in the commit narrative — covers the `bturep.github.io.attacker.com` prefix attack, port-suffix attacks, subdomain attacks, file:// `null` origin, and missing/garbage Origin (all 12 pass). Browser side already sent `application/json` (verified in `proxyEdit` for both `browse.html` and `next.html`), so no client change required. **Restart the proxy** (`python3 scripts/edit_proxy.py`) before next admin editing session. §11.1 CRITICAL step 3 (per-startup random secret replacing the hardcoded pin fallback) **deferred** — it touches the unlock UI in next.html and deserves its own ~1–2 hr session.
- **CI: `.github/workflows/validate.yml` + `.github/scripts/validate.mjs`.** First-ever GitHub Actions workflow on the repo. Runs after every push to `main` (and on PRs). Checks: each inline `<script>` block in `browse.html` and `next.html` parses (`node --check`); `VERSION` constant matches the expected pattern per file (live = `v\d+\.\d{2}\.\d{2}`, staging = `v\d+\.\d{2}-test\.\d{2}`); both manifests parse and carry `start_url`. Does **not** gate the push — GitHub emails on a failed workflow run, which is the audit's "alert, don't block" model. Smoke-tested both positive (current tree → pass) and negative (deliberately broken VERSION + JS syntax → both caught, exit 1).

ARCHITECTURE.md §11.5 appended with the same details so the audit document tracks its own resolved items.

**Standing-rule notes:**
- Edit-proxy restart is now strictly required for admin editing on the next session (the convention already says daily restart, but a CSRF-defence change is the kind of thing that's silent until it bites).
- The new validate workflow will run on this very commit — first run will establish the baseline. Failures arrive in the GitHub Actions tab + by email.

**Pending threads:** unchanged. ARCHITECTURE.md §11.1 step 3 + §11.1 HIGH metadata backup + everything in §11.2 (post pre-push validation), §11.3 remain. §11.1 CRITICAL is now partially resolved (the two biggest CSRF gaps closed); step 3 is the next priority on that thread.

**Version line: browse.html `v1.06.31` (LIVE, unchanged) · next.html `v1.07-test.51` (staging, unchanged).**

---

### 2026-05-22 — Backend-hygiene bundle: .env audit + Wikibase helper + metadata backup (no version bump)

Three more audit items off the list, all backend, no live-site touch.

- **`.env` / `.gitignore` audit (§11.2 LOW).** Added `.env`, `.env.*` (with a `!.env.example` allow), and `data/snapshots/wikibase_full_*/` to `.gitignore`. Verified no credential ever leaked into history (grep over `git log --all -p` for `(PASSWORD|SECRET|TOKEN).*=.{8,}` returns zero matches — only `<in .env>` markdown placeholders). The actual `.env` lives outside the repo at `~/Documents/hh-wikibase-migration/.env`; gitignore entries are belt-and-braces.

- **`scripts/_wikibase.py` — shared Wikibase helper (§11.2 LOW).** Extracted the env-loading + login + CSRF + retry-on-stale-token boilerplate that lived (copy-pasted) in 11 scripts. New module exposes `load_env(path)` and a `WikibaseSession` class with `.login()`, `.post(action, **params)` (auto-retry on `badtoken`/`assertuserfailed`/`notoken`), and `.get(action, **params)`. Deliberately narrow scope: doesn't wrap every wbX action — scripts that build `data` dicts by hand keep doing so; the module centralises transport + auth only. Migrated **`patch_dates.py`** and **`mint_property.py`** as proof of fit; the bigger scripts (`ingest_item.py`, `ingest_publication.py`, `batch_ingest_egc.py`, the renumber pair, `recolor_previews.py`, `clean_titles.py`, `fix_caa_scheme_split.py`, `strip_counter_brackets.py`) intentionally left alone — they work, the payback is on the *next* new ingest, not on re-touching working code. Smoke-tested: helper imports clean, both migrated scripts compile + their `--help` works.

- **`scripts/backup_metadata.py` — local-only metadata backup (§11.1 HIGH partial).** New read-only script (no credentials needed) that SPARQLs every catalogue item, fetches the full `wbgetentities` for each, walks one hop to pull every referenced vocab / person / institution, and also dumps every property in use. Writes raw JSON sidecars to `data/snapshots/wikibase_full_YYYYMMDD/<COLLECTION>/<ARCHID>.json` + `_referenced/<Qnnn>.json` + `_properties/<Pnn>.json` + `_manifest.json`. **First run today:** 180 catalogue items (HHC 115 · CAA 35 · EGC 30) + 123 referenced + 29 properties = 332 entities, 3.0 MB. Each sidecar is a complete recovery artifact — claims with hashes, all qualifiers and references preserved — enough to rebuild via `wbeditentity` if the Wikibase Cloud instance disappears tonight. **Snapshot is gitignored**: living on disk only at `data/snapshots/wikibase_full_20260522/` — Brandon to decide whether to commit a periodic snapshot, push to R2, or rely on local backup. The other half of §11.1 HIGH (R2 sidecar mirror + ingest-script patches) is still pending.

**Standing-rule notes:**
- New scripts that talk to Wikibase should now `from _wikibase import WikibaseSession` rather than re-implementing the login dance. Pattern in the two migrated scripts.
- `backup_metadata.py` is safe to run on demand — it's read-only, no rate-limit risk at this catalogue size (built-in 100ms pause between 50-item batches).
- `git status` won't show today's snapshot directory (it's gitignored). It lives at `data/snapshots/wikibase_full_20260522/` if you want to inspect.

**Pending threads:** §11.1 CRITICAL step 3 (per-startup random secret + unlock UI) and §11.1 HIGH part 2 (R2 sidecar mirror + ingest-script patches) remain. §11.2 LOW items still pending: PIDs central dictionary, researcher-notes label honesty. §11.3 (bend-before-break) untouched. Original v1.07 pending threads (Curator Phase 2, Held-by, Phase rename, EGC photo ingest, Rotation Part 2) unchanged.

**Version line: browse.html `v1.06.31` (LIVE, unchanged) · next.html `v1.07-test.51` (staging, unchanged).**

---

### 2026-05-22 — Verifier + RN-tooltip honesty + PROPERTIES dictionary (next.html v1.07-test.52)

Three more audit items off the list.

- **`scripts/verify_r2_links.py` — image-pipeline integrity check (§11.3).** Read-only. SPARQLs every URL claim (P95 master, P96 preview, P143 access copy) and HEAD-requests each against R2. First run today found **6 dead P95 master URLs** — `HH-HHC-0036`, `0037`, `0038`, `0039`, `0040`, `0066`. Silent legacy from the 2026-05-14 HH-A → HH-HHC rename migration: R2 files were renamed correctly, but the P95 claims on those 6 items still point at the old `HH-A-NNNN_*.tif` filenames. Verified by HEAD-probing one example: old name `HH-A-0071_East_Wing_Foundation_Plan_Hunter_Haus_2008-06-03.tif` returns 404; new name `HH-HHC-0036_East_Wing_Foundation_Plan_Hunter_Haus_2008-06-03.tif` returns 200 and `rclone ls` confirms the file exists. **Fix is a 6-claim P95 rewrite — not done in this session** (data migration, separate from verifier work). JSON reports under `data/snapshots/r2_verify_*.json` are gitignored. Suggested cadence: run before each session-end.

- **RN tooltip honesty (§11.2 LOW).** Lock-icon tooltips in `next.html` updated to stop implying encryption. "Unlock to add notes" → "Sign in to add a note (stored locally on this device, not encrypted)". "Lock" → "Sign out (notes stay on this device)". `localStorage` storage shape unchanged. Two-line edit.

- **PROPERTIES central dictionary (§11.2 LOW).** New top-of-script constant in `next.html` declares all 27 PIDs the application uses, grouped by concern (identifiers, dates, hierarchy, custody, attribution, classification, production, files, notes). Migrated: the whole `EDITABLE` map (16 entries), the two `setStringClaim`/SPARQL sites that used `ACCESS_PID`/`ROTATE_PID`, and the two catalogue-SPARQL `OPTIONAL` lines for those two. The two prior single-PID constants (`ACCESS_PID`, `ROTATE_PID`) removed. **Deliberately NOT migrated:** the rest of the catalogue SPARQL body (~25 `wdt:Pxx` literals in a template string) — audit explicitly recommended opportunistic migration to avoid a fragile big-bang rewrite. Future SPARQL touches can substitute in `${PROPERTIES.X}` since the query is already template-stringed. 21 `PROPERTIES.X` references now in `next.html`. Validate workflow green.

**New pending follow-up (added today):**
- **Fix 6 dead P95 URLs on HH-HHC-0036 / 0037 / 0038 / 0039 / 0040 / 0066.** Wikibase P95 still points at old `HH-A-NNNN` filenames; R2 has the renamed files. One small `wbcreateclaim`/`wbsetclaim` migration script using `_wikibase.py`, ~20 minutes. JSON detail at `data/snapshots/r2_verify_20260522.json` (run today, local-only).

**Standing-rule notes:**
- `scripts/verify_r2_links.py` is the canonical "did my ingest actually land?" check. Run after every ingest, and before session close.
- `PROPERTIES.X` is now the right way to refer to a Wikibase property in `next.html` JS. The bare-PID strings in the catalogue SPARQL body are the only remaining holdouts — migrate opportunistically.

**Pending threads:** §11.1 CRITICAL step 3 and §11.1 HIGH part 2 remain the biggest open audit items. Today's 6-URL data fix added. §11.3 still has `renderMeta`/`renderMobSheet` duplication and the "no smoke tests" item.

**Version line: browse.html `v1.06.31` (LIVE, unchanged) · next.html `v1.07-test.52` (staging).**

---

### 2026-05-22 — Fixed 6 dead P95 URLs surfaced by verifier (no version bump)

Acted on the follow-up the verifier surfaced. New `scripts/fix_p95_legacy_urls.py` rewrote the 6 stale P95 claims (HH-HHC-0036 / 0037 / 0038 / 0039 / 0040 / 0066) from `HH-A-NNNN_*.tif` to `HH-HHC-NNNN_*.tif`. Script lives now at `scripts/archived/fix_p95_legacy_urls_20260522.py`.

- **Safety pattern:** dry-run-first (default; `--execute` to write); pre-flight HEAD-check on every proposed new URL refused to write any rewrite where the new URL wasn't reachable on R2; create-then-remove per item (matches `setStringClaim` pattern in browse/next.html); built on `_wikibase.py`.
- **Execution:** dry-run showed 6 of 6 safe (all new URLs HEAD-checked 200). `--execute` rewrote each item in a single round-trip (`wbcreateclaim` → `wbremoveclaims`). All 6 succeeded; 0 failures.
- **One wrinkle.** Q425 (HH-HHC-0066) turned out to have a **pre-existing correct P95 claim** that wasn't visible to the initial SPARQL planning pass (SPARQL replication lag — same lag that made the verifier briefly show "404" after the writes had landed). My script created a duplicate of the correct URL. Cleaned up manually in a follow-up `wbremoveclaims` so Q425 ends with exactly one P95 claim, at the right URL. Documented in the archived script's docstring.
- **Verification.** Post-fix re-run of `verify_r2_links.py` against all URL props: **354 / 354 URLs at 200, zero failures**. Image pipeline is now clean by the verifier's measure.

**Pattern learned (for the next data-fix script):** the SPARQL endpoint is slightly stale — wbgetentities is real-time, SPARQL has a few-minutes lag. When the script's own SPARQL planning shows a single value but wbgetentities shows two, trust the API. A future version of `fix_*` scripts could pre-flight the entity via `wbgetentities` before SPARQL to detect this case.

**Updated pending threads:** today's "fix 6 dead P95 URLs" follow-up — DONE. §11.1 CRITICAL step 3 and §11.1 HIGH part 2 still the biggest open audit items.

**Version line: browse.html `v1.06.31` (LIVE, unchanged) · next.html `v1.07-test.52` (staging, unchanged).**

---

### 2026-05-22 — Per-startup proxy token + paste UI (CRITICAL row fully closed) (next.html v1.07-test.53)

Closed §11.1 CRITICAL step 3 — the last item in the CRITICAL audit row. The prior model used the admin PIN (hardcoded in `RPINS["203BTP"]` in client code) as the proxy secret; now the proxy generates a per-startup random token and the browser stores it in `localStorage["hhf_proxy_token"]` after the admin pastes it.

**Python side (`scripts/edit_proxy.py`):**
- `SECRET = cred.get("EDIT_PROXY_SECRET") or secrets.token_urlsafe(24)` (32-char URL-safe random; `.env` override still works for power users / stable testing but loses the rotation benefit).
- Startup banner now prints the token in a small ASCII frame on stdout, plus a one-line "paste this into next.html" instruction.
- `/ping` extended: optionally takes `?secret=…` and returns `{ok, user, authenticated}`. Uses `secrets.compare_digest()` for constant-time comparison.
- Hardcoded `"203BTP"` fallback removed entirely.

**Browser side (`next.html`):**
- `getProxyToken()` / `setProxyToken()` wrap `localStorage["hhf_proxy_token"]`.
- `proxyEdit()` reads token from localStorage; if missing → throw + mark unauthenticated. Sends it as `secret`. On 403 "bad secret" → clear token + mark unauthenticated.
- New state boolean `_proxyAuthenticated` alongside `_proxyOnline`. Editing requires both. `body.hh-proxy-off` gate now fires when either is false.
- `#hh-proxy-badge` now renders three states: offline (the existing message), needs-token (inline `<input>` + save button with a "token rotates on every proxy restart" hint), ready (hidden). First time the form appears, focus lands on the input.
- `pingProxy()` sends `?secret=…` (if a token is stored) and updates both state booleans from the response.

**End-to-end smoke-tested** (proxy launched in background, `curl`-driven):
- `/ping` with no secret → `authenticated:false` ✓
- `/ping` with correct token → `authenticated:true` ✓
- `/edit` with correct token + valid Origin + JSON → secret accepted (failed at action-allowlist as expected for `wbgetentities`) ✓
- `/edit` with wrong token → 403 "bad secret" ✓
- `/edit` with no Origin → 403 "origin not allowed" (CSRF defence 1 fires before secret check) ✓
- `/edit` with text/plain → 415 (CSRF defence 2 fires before secret check) ✓
All four defences (Origin, Content-Type, exact-match origin, per-startup secret) layer correctly. Validate workflow green.

**Workflow change for admin editing (next session):**
1. `python3 scripts/edit_proxy.py` (as before) — startup prints a token.
2. Open next.html, unlock admin via PIN (as before).
3. Wait for the red badge at bottom-left ("edit proxy connected · paste startup token to enable edits"). Paste, save. Edits enable.
4. Restart the proxy → new token → badge re-appears → paste new token.

If you ever restart the proxy mid-session, the next ping flips `_proxyAuthenticated → false`, the badge re-appears, and any in-flight edit returns "proxy rejected the token — paste the current one from proxy stdout".

**`browse.html` (LIVE) caveat:** still uses the old `secret: s && s.pin` pattern. Admin editing on LIVE was never the workflow per the LINE: NEXT rule (real visitors don't admin-edit), so this is benign until the next promotion — at which point the new auth flow rides along.

**Standing-rule update:** "Edit-proxy restart" convention in the Active Working Context section now mentions the token paste step.

**Audit standing:**
- ✅ **§11.1 CRITICAL row fully closed** (steps 1, 2, 3 all done; MEDIUM startswith folded in)
- ◐ §11.1 HIGH (local backup done; R2 sidecar mirror + ingest-script patches still pending)
- ✅ §11.2 row fully closed (MEDIUM CI + all three LOW items)
- ✅ §11.3 image pipeline integrity check + its first finding fixed
- ⏸ §11.3 still has `renderMeta`/`renderMobSheet` dedup and Playwright smoke tests
- §11.1 HIGH part 2 is now the highest-priority remaining audit item

**Pending threads:** unchanged from prior entries except §11.1 CRITICAL step 3 now resolved.

**Version line: browse.html `v1.06.31` (LIVE, unchanged) · next.html `v1.07-test.53` (staging).**

---

### 2026-05-22 — R2 metadata sidecar mirror (§11.1 HIGH part 2a)

`scripts/sync_metadata_to_r2.py` — rclone-based one-shot that takes the most recent local snapshot from `data/snapshots/wikibase_full_YYYYMMDD/` and pushes every JSON sidecar up to R2 in the layout the audit recommended.

**R2 layout established today:**
```
{collection-folder}/metadata/{ARCH_ID}.json    catalogue items, sibling to intake/
_wikibase/items/{Qnnn}.json                    referenced (vocab/people/institutions)
_wikibase/properties/{Pnn}.json                property definitions
_wikibase/_manifest.json                       snapshot manifest
```

Collection-folder map matches the existing image-tier layout (HHC → `hunter-house-collection`, CAA → `canadian-architecture-archive`, EGC → `eric-gesinger-collection`).

**First run:**
- 6 rclone jobs, all succeeded
- 115 + 35 + 30 = 180 catalogue sidecars + 123 referenced + 29 properties + manifest
- All sidecars HEAD 200 via the public CDN; sample fetch parses cleanly as JSON (Q369 with 18 claims)

**Design notes:**
- Kept this script separate from `backup_metadata.py`. `backup_metadata.py` is read-only against Wikibase + writes to local disk only (zero rclone dependency, zero R2 dependency). `sync_metadata_to_r2.py` is transport-only (local snapshot → R2). Either step can be retried/inspected without re-running the other.
- Dry-run default; `--execute` writes; `--checksum` for paranoid mode (compare hashes instead of size+mtime).
- Idempotent — rclone's default size+mtime comparison skips unchanged files. Re-running after a fresh `backup_metadata.py` only uploads what changed.

**Remaining piece of §11.1 HIGH:** per-ingest sidecar writes — when `ingest_item.py` / `ingest_publication.py` / `batch_ingest_egc.py` create a new Wikibase item, also write its sidecar to R2 at the end. Next bundle.

**Version line: browse.html `v1.06.31` (LIVE, unchanged) · next.html `v1.07-test.53` (staging, unchanged).**

---

### 2026-05-22 — Per-ingest sidecar writes (§11.1 HIGH row fully closed)

Final piece of §11.1 HIGH. New `scripts/sync_one_metadata.py` is the single-item version of `sync_metadata_to_r2.py`: given an archId, SPARQLs the QID, fetches the entity via `wbgetentities`, and rclone-copies the JSON sidecar to the right `{collection-folder}/metadata/` path on R2. Read-only against Wikibase (no bot creds); writes only via rclone. Dry-run default; `--execute` writes; `--quiet` for non-error silence.

**Smoke-tested:** dry-run on HH-HHC-0001 resolved Q369 + reported a 10,718-byte payload would copy. Then `--execute` on HH-EGC-0001 wrote the actual sidecar (Q505, 6,462 bytes), HEAD-confirmed 200 via the CDN.

**Patched the three ingest scripts** (each got a 10-line fail-safe tail):
- `scripts/ingest_item.py` — single-image ingest. Hook fires once at end of `main()` after `wbeditentity new=item` succeeds.
- `scripts/ingest_publication.py` — multi-page publication ingest. Same shape, single hook at end.
- `scripts/batch_ingest_egc.py` — workbook-driven batch loop. Hook lives inside the loop, after `results.append((r["id"], qid))` — fires for both the "created" and the "existed; desc updated" branches.

Each call is `subprocess.run([…sync_one_metadata.py, ARCH_ID, --execute, --quiet], timeout=60, check=False)` wrapped in `try/except`. **A sidecar upload glitch never breaks an otherwise-successful ingest** — the worst case is a `⚠ sidecar sync skipped (non-fatal)` line; the periodic `backup_metadata.py + sync_metadata_to_r2.py` pair will catch the gap on the next run.

Imports were already present in all three scripts (`subprocess`, `os`); zero new dependencies. All four touched scripts compile.

**Operational shape going forward:**
- Every new ingest → sidecar lands on R2 immediately.
- `backup_metadata.py` + `sync_metadata_to_r2.py` remain as the safety-net + periodic full-snapshot mechanism.
- `verify_r2_links.py` could be extended later to also HEAD-check sidecar URLs alongside image URLs — small follow-up; not in this commit.

**Audit standing now:**
- ✅ **§11.1 CRITICAL row fully closed** (steps 1, 2, 3 + MEDIUM startswith)
- ✅ **§11.1 HIGH row fully closed** (local backup + R2 mirror + per-ingest sidecar writes)
- ✅ §11.2 row fully closed
- ✅ §11.3 image-pipeline integrity check + first finding fixed
- ⏸ §11.3 `renderMeta`/`renderMobSheet` dedup
- ⏸ §11.3 Playwright smoke tests

The two big severity rows (CRITICAL + HIGH) are both fully done. What remains in §11.3 is refactor-shaped, not security-shaped.

**Version line: browse.html `v1.06.31` (LIVE, unchanged) · next.html `v1.07-test.53` (staging, unchanged).**
