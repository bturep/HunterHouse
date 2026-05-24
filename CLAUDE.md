# CLAUDE.md — Hunter House Foundation session context
# Live working memory. Frozen archives (read-only, full historical detail; git also holds all of it):
#   • CLAUDE_archive_v1.07-audit.md — 2026-05-22 audit-response day, verbatim (freeze 2026-05-22)
#   • CLAUDE_archive_v1.07.md       — v1.06.00 promotion → v1.06.18 live, v1.07-test.01 → .22 staging (freeze 2026-05-21)
#   • CLAUDE_archive_v1.06.md       — v1.05.00 → v1.06.00 promotion (freeze 2026-05-20)
#   • CLAUDE_archive_v1.05.md       — v1.03.00 → v1.05.02 (freeze 2026-05-19)
#   • CLAUDE_archive_v1.02.md       — ≤ v1.02.18 (earliest freeze)

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
- **Built by / Designed by — cross-property entity search.** Mint affordance covers the "add a person not yet anywhere" case. Remaining gap: picking e.g. Q201 Hunter from the P140 picker when he's only currently registered under P80. Probably good enough; revisit if it bites.
- **EGC photograph ingest** — drawings DONE 2026-05-20 (30 items, Q505–Q534). The 36 photographs of Gesinger's built furniture (photographer **Mary McNeill Knowles**, now known) are awaiting a separate intake sheet — when Brandon issues it, batch into the same EGC collection (Q182). Pattern: copy `scripts/batch_ingest_egc.py`, set type=photograph (Q89), creator = Knowles (mint Q if missing), add P85/depicts → Q209 Eric Gesinger, P141/designed-by → Q201 Hunter.
- **Rotation Part 2** — maintenance bake script driven by P144 claims; rotates master+3 tiers on R2, clears the claim, purges CDN. Prerequisite: an automated Cloudflare cache-purge API token (still not wired). Also fixes the **mobile/lightbox rotation gap** — P144 is currently applied at the desktop image stage only.

**Deferred / structural:**
- **Wikibase revision-history cleanup** (later, when the archive settles). Iterating during dev has left noisy edit histories. Two paths: per-item `Special:RevisionDelete` (sysop, Brandon has it on his own Wikibase Cloud), or full instance reset via support. Revision history doesn't affect SPARQL or `browse.html`; psychological cleanup. **Don't tackle until canonical model settled** (post-RAD-alignment decision below).
- **Archival-standards alignment.** Current model uses ISAD(G) loosely; not formally RAD-compliant. Gaps: (1) fonds-level item in Wikibase; (2) series level encodes physical custody (HHC/CAA) rather than creator function — redefine or formally acknowledge as a custodial split; (3) Level of Description property (new P) needed for AtoM/LAC interop. Important before academic write-up or cross-institutional integration.
- **Wikidata items ready to submit.** Three drafted in `WIKIDATA_DRAFT.md` (Richard Hunter person; Canadian Architectural Archives institution; Richard Hunter fonds). Brandon needs a free Wikimedia account (2 min at `wikidata.org/wiki/Special:CreateAccount`); then QuickStatements copy-paste. After creation, add Q-numbers to P139 on Q201 (Hunter) and Q116 (CAA) in our Wikibase. **Prompt at session start.**
- **PWA splash reinstall on iPhone.** Manifest already has `start_url: browse.html` but the old install is cached with index.html. Remove HH Archive from home screen and re-add from `bturep.github.io/HunterHouse/browse.html`.
- **Renumber-script consolidation** (low priority). `renumber_caa.py` + `renumber_caa_25_32.py` are both one-shots completed and could move to `scripts/archived/` next time touched.

**Resolved during the 2026-05-22 audit-response day** (full detail in `CLAUDE_archive_v1.07-audit.md`):
- §11.1 CRITICAL row fully closed (edit-proxy CSRF defences + per-startup token + paste UI).
- §11.1 HIGH row fully closed (preservation pipeline: `backup_metadata.py` + `sync_metadata_to_r2.py` + `sync_one_metadata.py` called fail-safe from each ingest script; 332 sidecars on R2; per-ingest writes from here on).
- §11.2 row fully closed (CI workflow `.github/workflows/validate.yml`; `scripts/_wikibase.py` shared helper; PIDs central dictionary; RN tooltip honesty; `.env`/`.gitignore` hygiene).
- §11.3 image integrity check (`scripts/verify_r2_links.py`) + same-day fix of 6 dead P95 URLs surfaced by the first run.
- Playwright smoke tests delivered under `tests/` (dev-only, one-time install).
- Six unused files deleted (`index-video.html`, `import-rn.html`, `swatches.html`, `GES_intake.xlsx`, `Main_Page.wiki`, `.DS_Store`); `scripts/make_ges_intake.py` archived; stale remote branch `refactor/browse-cleanup` deleted.
- ARCHITECTURE.md rewritten as a clean reviewer-facing doc.

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
│   ├── light.css           Light design system (all pages)
│   ├── dark.css         Dark design system (4 reading pages only)
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
- `light.css` — light (ink on paper). All pages, especially header.
- `dark.css` — dark (cream on near-black). 4 reading pages only.

**Key tokens — light.css**
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
| `_wikibase.py` | **Shared helper** — `load_env()` + `WikibaseSession` (login + CSRF + retry-on-stale-token). Import this in any new write-script (added 2026-05-22, §11.2 dedup) | Active |
| `edit_proxy.py` | Local admin Wikibase write proxy (`127.0.0.1:8731`, bot creds server-side). Per-startup random token (`secrets.token_urlsafe(24)`) printed on stdout; admin pastes into next.html's badge. Origin allowlist + JSON Content-Type required + constant-time secret compare (full CSRF defences, §11.1) | Active |
| `ingest_item.py` | Single-image item ingest: master TIF + 3 R2 tiers + Wikibase claims. Auto-resolves vocab. Dry-run default. Calls `sync_one_metadata.py` fail-safe at end | Active |
| `ingest_publication.py` | Multi-page publication ingest (masters byte-for-byte + SHA-256 manifest + cover tiers + access PDF → R2; Wikibase item). Calls `sync_one_metadata.py` fail-safe at end | Active |
| `batch_ingest_egc.py` | Workbook-driven batch ingest (used once for the 30 EGC drawings, 2026-05-20). Reads `EGC_intake.xlsx` + scans folder; mints phases + drawing-type vocab once. Calls `sync_one_metadata.py` fail-safe per item. Template for future collection batches | Active |
| `mint_property.py` | Mint (or find, idempotent) one Wikibase property: `--label --desc --datatype`. Migrated to `_wikibase.py` | Active |
| `patch_dates.py` | Add P82 date claims + update descriptions. Migrated to `_wikibase.py` | Active |
| `backup_metadata.py` | **Preservation** — read-only; dump every Wikibase item + referenced vocab + properties → `data/snapshots/wikibase_full_YYYYMMDD/` as raw `wbgetentities` JSON sidecars. No creds needed (§11.1 HIGH) | Active |
| `sync_metadata_to_r2.py` | **Preservation** — rclone-push the local snapshot up to R2 in `{collection-folder}/metadata/` + `_wikibase/items/` + `_wikibase/properties/` layout. Dry-run default; `--execute` writes (§11.1 HIGH) | Active |
| `sync_one_metadata.py` | **Preservation** — single-item sidecar write; called fail-safe from each ingest script at end of every successful per-item create. CLI + programmatic entry points (§11.1 HIGH) | Active |
| `verify_r2_links.py` | **Integrity** — SPARQL every URL claim (`P95`/`P96`/`P143`) AND every derived sidecar URL; HEAD-check each against R2. Read-only. `--no-sidecars` / `--sidecars-only` flags. Suggested cadence: before each session-end (§11.3) | Active |
| `regen_previews.py` | Regen preview/thumb/large from TIF masters | Active |
| `clean_titles.py` | Strip/rewrite bracketed annotations from labels | Active |
| `strip_counter_brackets.py` | Remove `[N/N]` counter patterns from labels | Active |
| `recolor_previews.py` | Convert R2 JPEGs from kip2300 ICC profile → sRGB. Idempotent. `--dry-run` / `--one KEY` / `--execute` | Active |
| `regen_icons.py`, `rotate_images.py`, `fix_caa_scheme_split.py`, `renumber_caa.py`, `renumber_caa_25_32.py` | One-shots that have already run; live in `scripts/` for reference but candidates for `scripts/archived/` next touch | Active (one-shot) |
| (`scripts/archived/`) | Completed one-time migrations (`rename_ids`, `renumber_hhc`, `migrate_p142_location`, `fix_p142_prose`, `fill_p142_missing`, `rotate_images`, `make_ges_intake_20260520`, `fix_p95_legacy_urls_20260522`, …) | Complete |

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
| v1.06.31 + audit | 2026-05-22 | **Audit-response day (no live promotion).** Browse.html unchanged at `v1.06.31`; staging line advanced through `v1.07-test.50 → .54` (Vellum + cognac curator reskins, narrow render-helper dedup, PROPERTIES central dict, RN tooltip honesty, per-startup-token paste UI). Behind the scenes: GitHub Actions validate workflow (`.github/workflows/validate.yml`), preservation pipeline end-to-end (`backup_metadata.py` + `sync_metadata_to_r2.py` + per-ingest `sync_one_metadata.py` → 332 sidecars on R2), image-pipeline integrity check (`verify_r2_links.py`) + same-day fix of 6 dead P95 URLs, Playwright smoke tests, `_wikibase.py` shared helper, edit-proxy CSRF hardened (per-startup secret + Origin allowlist + JSON Content-Type + constant-time compare). ARCHITECTURE.md rewritten clean for external review. Six unused files deleted. **Both highest-severity audit rows (CRITICAL + HIGH) fully closed.** 14 commits. |

Tags pushed: `v1.01.00` (fc98905), `v1.02.00` (2059cb7), `v1.02.18` (82065e6), `v1.03.00`, `v1.03.01`, `v1.03.08`, `v1.04.00`, `v1.05.00` (2026-05-19), `v1.06.00` (2026-05-20).

Full per-version detail: `CLAUDE_archive_v1.07-audit.md` (2026-05-22 audit day), `CLAUDE_archive_v1.07.md` (v1.06→test.22), `CLAUDE_archive_v1.06.md` (v1.05→v1.06), `CLAUDE_archive_v1.05.md` (v1.03→v1.05), `CLAUDE_archive_v1.02.md` (≤v1.02).

---

## Staging / test page

A live-stable + parallel-test setup, zero extra infra (plain GitHub Pages serves only `main`, so a git branch is **not** a separate URL — a duplicate file is).

| | |
|---|---|
| **Live** | `browse.html` → https://bturep.github.io/HunterHouse/browse.html — never edited during development |
| **Staging** | `next.html` → https://bturep.github.io/HunterHouse/next.html — break/iterate freely |

- Both on `main`. Pushing `next.html` redeploys but `browse.html` untouched, so **live visitors unaffected**.
- `next.html` `VERSION = "v1.07-test.NN"` → `CACHE_KEY` (`hhf_v1.07-test.NN`) isolated from live (`hhf_v1.06.00`).
- `next.html` must stay in repo root (relative `assets/…`). Shares `assets/light.css` — inline `<style>` changes isolated, but `light.css` edits leak to live. Fork to `assets/verso.next.css` only when a task needs CSS changes.
- `index.html` splash + manifest `start_url` point at `browse.html`; installed PWA shows live. Test new version in the **phone browser** at the `next.html` URL.

**Promotion (staging → live), when ready:**
1. `cp next.html browse.html`
2. In `browse.html`, set `VERSION` to the real version; update session log.
3. (If `light.css` was forked) `cp assets/verso.next.css assets/light.css`.
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

### 2026-05-22 — Audit-response day (next.html v1.07-test.50 → v1.07-test.54) — digested

Full per-commit detail in `CLAUDE_archive_v1.07-audit.md` (12 verbatim entries, frozen at session end). Condensed:

Twelve commits across one day. Browse.html (LIVE) untouched throughout (LINE: NEXT held). Staging line advanced `v1.07-test.49 → v1.07-test.54`. Vellum curator-mode reskin landed early (Brandon then did the cognac palette + curator-chrome restructure on his own). The bulk of the day was a top-to-bottom security + maintainability audit response triggered by `ARCHITECTURE.md §11` (added that same day to the doc Brandon shipped to an external software-engineer reviewer).

**Audit rows resolved end-to-end:**

- **§11.1 CRITICAL — edit-proxy CSRF + per-startup token.** `scripts/edit_proxy.py` now validates `Origin` against an exact-match allowlist *before* reading the body (403 on mismatch), requires `Content-Type: application/json` (415 otherwise — forces a real CORS preflight), uses `urlparse`-based hostname matching (production `https://bturep.github.io` exact; localhost any port), and authenticates with a per-startup random `secrets.token_urlsafe(24)` token printed in an ASCII-frame stdout banner. `/ping?secret=…` returns `{authenticated}` via constant-time `compare_digest`. Browser stores token in `localStorage["hhf_proxy_token"]`; new tri-state `#hh-proxy-badge` (offline / needs-token / ready) renders an inline paste form auto-focusing the input on first appearance; 403 from `/edit` clears the token and re-shows the form. The hardcoded `"203BTP"` fallback is gone.

- **§11.1 HIGH — preservation backup, both halves.** `scripts/backup_metadata.py` (read-only; no creds) dumps every catalogue item + every referenced vocab/person/institution + every property in use as raw `wbgetentities` JSON to `data/snapshots/wikibase_full_YYYYMMDD/`. `scripts/sync_metadata_to_r2.py` rclone-pushes that local snapshot up to R2 in the layout `{collection-folder}/metadata/{ARCH_ID}.json` + `_wikibase/items/{Qnnn}.json` + `_wikibase/properties/{Pnn}.json` + `_wikibase/_manifest.json` (HHC → `hunter-house-collection`, CAA → `canadian-architectural-archive`, EGC → `eric-gesinger-collection`). First run pushed 332 sidecars in 6 jobs; all HEAD-200 via the CDN. `scripts/sync_one_metadata.py` is the single-item version; each ingest script (`ingest_item.py`, `ingest_publication.py`, `batch_ingest_egc.py`) gained a fail-safe `subprocess.run(...)` tail that calls it after every successful per-item create — sidecar glitches never break an ingest. From here on, the R2 mirror stays in lock-step automatically.

- **§11.2 — operational hygiene, all five items.** New GitHub Actions workflow `.github/workflows/validate.yml` + `.github/scripts/validate.mjs` runs on every push to `main` (and PRs): `node --check` per inline `<script>` block in `browse.html` + `next.html`, `VERSION` regex per file, manifest JSON parse. Does not gate the push — emails on failure. CI green on every push today. `scripts/_wikibase.py` extracts the `load_env()` + `WikibaseSession` (login + CSRF + retry-on-stale-token) boilerplate that was copy-pasted across 11 scripts; migrated `patch_dates.py` + `mint_property.py` as proof. `PROPERTIES = {…}` constant added at top of next.html declaring all 27 PIDs the JS uses; `EDITABLE` map + `ACCESS_COPY`/`DISPLAY_ROTATION` call sites migrated (catalogue SPARQL body deliberately deferred — opportunistic, not big-bang). RN lock-icon tooltips re-worded to drop the implicit encryption claim. `.env`, `.env.*`, snapshot dirs, `.DS_Store`, pytest/playwright caches all gitignored; history audit clean.

- **§11.3 — bend-before-break.** `scripts/verify_r2_links.py` SPARQL-fetches every URL claim (`P95`/`P96`/`P143`) AND every derived sidecar URL, HEAD-checks each. First run surfaced **6 dead P95 master URLs** from the 2026-05-14 HH-A → HH-HHC rename migration (R2 files were renamed, Wikibase claims weren't). `scripts/archived/fix_p95_legacy_urls_20260522.py` rewrote all 6 via create-then-remove; post-fix re-verify: **354/354 URL claims + 180/180 sidecar URLs all return 200**. Three Playwright smoke tests delivered under `tests/` (dev-only, not in CI; one-time `pip3 install pytest-playwright && playwright install chromium`). Three small render-helpers (`archiveContactText`, `rightsRowHTML`, `findingAidHTML`) extracted for bits literally duplicated between `renderMeta` and `renderMobSheet`; the broader `buildRows()` unification is **deferred by design** — the two functions have diverged in purpose (mobile read-only public, desktop admin-aware) and forcing it now would be high-risk for a "pays off when adding an editable field" maintainability win.

**House cleanup (end of day).** Six files removed: `index-video.html`, `import-rn.html`, `swatches.html`, `GES_intake.xlsx`, `Main_Page.wiki`, `.DS_Store`. `scripts/make_ges_intake.py` renamed to `scripts/archived/make_ges_intake_20260520.py`. Stale remote branch `origin/refactor/browse-cleanup` deleted. ARCHITECTURE.md fully rewritten — replaced the chronological §11.5 "Resolved" appendix with a clean §11 status (each audit item carries its resolution marker ✅/◐/⏸ alongside the original framing); §1–§10 refreshed for the new infrastructure; this is the version to send a reviewer.

**Standing-rule changes that survive into tomorrow:**
- **Edit-proxy workflow** now has a token-paste step: start proxy → copy token from its stdout banner → paste into next.html's bottom-left badge → edits enable. Token rotates on every proxy restart.
- **Validate workflow** runs on every push to main; check the GitHub Actions tab if you ever see an unexpected email from GitHub.
- **`verify_r2_links.py`** is the canonical "did everything actually land?" check — run before session-end.
- **New scripts that talk to Wikibase** should `from _wikibase import WikibaseSession` rather than re-implementing the login dance.
- **Per-item metadata sidecars** are now auto-written by every ingest script via the fail-safe `subprocess.run(...)` tail; no action needed on Brandon's part.

**Version line at session close: browse.html `v1.06.31` (LIVE, unchanged all session) · next.html `v1.07-test.54` (staging).**

---

### 2026-05-24 — v1.07 promoted to live + post-cold-read remediation (browse.html v1.07.00 · next.html v1.08-test.01)

**v1.07 promoted.** The full researcher-tools surface that had been accreting on the staging line for ~50 patches is now live. Compose mode (eyeball in the Item-record bar). Researcher `?` help pane (sibling overlay to the global `?`). Marks as an ordered candidate-list with drag-handle + nudge arrows in `[only]` mode + the "marks first" sort. Per-researcher Markdown export / import below the notes panel with same-vs-other-researcher merge semantics. Dirty-changes counter as a small red badge next to the researcher `?`. Admin "edit affordances off" pencil toggle (admin-only). `Aa` text-size toggle in the top-right cluster (`html.text-lg` keys ~196 generated `+1px` CSS overrides). Click-to-confirm in place of the old press-and-hold for `[clear]` and `×` deletes. Olivia Jol added as a second researcher PIN (`203OJ`). Full accessibility surface (`:focus-visible`, ARIA labels on icon buttons, semantic landmarks, skip-to-catalogue link, toast live region, modal focus management + Tab/Shift-Tab trap, `prefers-reduced-motion`). `CATALOGUE_QUERY` interpolation from the `PROPERTIES` central dict completed.

**Curator lens held back from live.** The Phase 1 lens is dormant on `browse.html` — the `await loadCurationIndex();` line in `main()` is commented out with a one-line note. Overlay / chip / threshold-card code is all present and inert. Active in `next.html` for the pilot researchers to experience as a "what's coming" preview. Promotable later by uncommenting one line.

**Live hotfixes that landed on browse before promotion** (so they're now subsumed): v1.06.32 mobile splash Continue handler bound before SPARQL (was inert on slow mobile); v1.06.33 `.row:hover` gated to real pointer devices (was sticking on touch). Both folded into the v1.07.00 surface.

**Post-cold-read remediation** before the promotion: ARCHITECTURE.md commissioned an external-AI "cold read" of the doc, which surfaced a punch-list of audit-grade items. Closed 1–5 in priority order:
1. CI VERSION-bump guard — `.github/scripts/validate.mjs` now refuses pushes that change `browse.html` or `next.html` without bumping `VERSION`. Compares working tree against `HH_PREVIOUS_SHA` (set in CI from `github.event.before` / `pull_request.base.sha`) and falls back to `HEAD~1` locally. Workflow checkout now uses `fetch-depth: 2`.
2. SPARQL retry + stale-cache fallback — one retry with 800 ms backoff; if both attempts fail, `loadFromWikibase()` falls back to any cached items in `localStorage` regardless of the 2-hour freshness window.
3. CSP via `<meta http-equiv>` on both HTMLs — `'unsafe-inline'` retained for script/style (single-file SPA constraint), but `connect-src` whitelisted to Wikibase Cloud + loopback, `img-src` to the R2 host, `object-src 'none'`. Validator updated to strip HTML comments before scanning for `<script>` (the CSP doc comment contained the literal string).
4. `PROPERTIES → CATALOGUE_QUERY` migration finished in staging (the SPARQL body had still been using bare `wdt:Pxx` literals).
5. a11y pass in three stages — A: `:focus-visible` + ARIA labels on icon-only buttons + `prefers-reduced-motion`. B: skip-to-catalogue link + semantic landmarks (`<header role="banner">`, `<main>`, `<section aria-label>`) + toast `aria-live` + modal `modalOnOpen` / `modalOnClose` open/close focus management. B+: focus trap inside modals on Tab / Shift-Tab. Explicit non-goal per Brandon: no font / colour / contrast changes; visual design treated as architect-specified constraint.

**Documentation refresh.** ARCHITECTURE.md §10 audit bullets rewritten to reflect current state (no CSP → CSP-with-`'unsafe-inline'`; no retry → one-retry-plus-stale-fallback; manual cache-bust → CI-enforced); new §10 Accessibility subsection. New top-level **HANDOFF.md** drafted as a continuity-of-operations document with 35 `[TO COMPLETE]` placeholders for maintainer-only knowledge (vendor account specifics, recovery emails, secondary admins, contact list). §6.2 Wikibase-loss recovery procedure explicitly flagged as "not rehearsed end-to-end" with a TODO to dry-run it on a throwaway instance.

**Aesthetic cleanup.** `assets/verso.css` → `assets/light.css`; `assets/inverse.css` → `assets/dark.css`. The bookbinding-conceit naming pair was honest at v1.0 but had become noise (only `verso` is print-shop vocabulary; pairing it with `inverse` was a hybrid that wasn't quite either metaphor). Light / dark are what the files are; the rename trims the metaphor without changing the styling. All HTML references + active docs updated; frozen `CLAUDE_archive_*.md` left intact.

**Pilot phase framing** added to README, ARCHITECTURE §2, and HANDOFF §9: 3-month researcher-only pilot, not yet public-facing, building archive + curator lenses. Deliberately not added to this session log — it's standing context, not timeline.

**Standing-rule changes that survive into v1.08:**
- LINE: NEXT resumes on `next.html` v1.08-test.NN. Bump on every push, as usual.
- Curator load remains commented out on `browse.html`. Don't uncomment without explicit decision.
- HANDOFF.md placeholders will be filled in as Brandon gets to them; no auto-prompts.

**Version line at session close: browse.html `v1.07.00` (LIVE, just promoted) · next.html `v1.08-test.01` (staging, at parity, v1.08 line opening).**
