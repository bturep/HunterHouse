# Hunter House Foundation Archive — architecture brief

For a software engineer inspecting the live site. Scope = what `https://bturep.github.io/HunterHouse/` actually serves today, plus the repository state behind it.

**Snapshot date:** 2026-05-22 (end-of-session). **Live:** `browse.html` `v1.06.31`. **Staging:** `next.html` `v1.07-test.54`.

---

## 1. TL;DR

A **single-page, zero-build static site** served from GitHub Pages. The catalogue browser is one ~280 KB HTML file (`browse.html`, ~5,520 lines) containing inline CSS and vanilla ES2020 JavaScript. It reads its data at runtime from a public **Wikibase Cloud** instance via **SPARQL over HTTPS**, and loads images from a public **Cloudflare R2** bucket (URLs are stored as values inside Wikibase, not hard-coded). There is no framework, no bundler, no package manager.

There is a small Python tooling fleet under `scripts/` for ingest, batch migrations, the local admin write-proxy, and the metadata-preservation pipeline. There is a one-job GitHub Actions workflow that validates every push (JS syntax + VERSION pattern + manifest JSON). There are three Playwright smoke tests under `tests/` for the maintainer's local use. Admin writes happen only on the maintainer's own laptop, via a Python HTTP proxy on `localhost:8731` that holds the Wikibase bot credentials server-side and authenticates with a per-startup random token.

The architecture is deliberately small. The complexity that exists is concentrated in (a) the single HTML file and (b) the data model in Wikibase.

---

## 2. Project at a glance

| | |
|---|---|
| Live URL | `https://bturep.github.io/HunterHouse/` (PWA `start_url` → `browse.html`) |
| Repo | `github.com/bturep/HunterHouse` (default branch `main`, **public**) |
| Hosting | GitHub Pages, default config — push to `main` ⇒ live in ~30 s |
| Languages | HTML, CSS, vanilla JS (no TypeScript, no JSX); Python 3 for offline scripts |
| Build / bundler | **None.** Files served verbatim. |
| Package manager | **None.** No `package.json`, no `node_modules`. |
| CI | One workflow: validate JS syntax + `VERSION` regex + manifests on every push (`.github/workflows/validate.yml`). Does not gate the push — emails on failure. |
| Tests | Dev-only Playwright smoke tests under `tests/` (3 tests). One-time setup; not in CI. |
| External runtime deps | Google Fonts (Inter Tight, JetBrains Mono); bundled PDF.js (vendored, not CDN) |
| Browser support target | Modern evergreen (uses CSS view transitions, `matchMedia`, ES2020); mobile = iOS Safari is the primary mobile target |
| PWA | Yes — minimal `manifest.json` + no-op `sw.js` (no offline cache) |
| Data backend | Wikibase Cloud SPARQL: `https://hunterhouse.wikibase.cloud/query/sparql` |
| Image / PDF / sidecar storage | Cloudflare R2, public bucket at `archive.hunterhousefoundation.com` |
| Author / contributors | Solo: `bturep` (579 of 579 commits) |

---

## 3. Repository layout (what's actually shipped)

### Live HTML pages

| File | Lines | Role |
|---|---|---|
| `index.html` | 28 | Thin JS+meta redirect to `browse.html` (preserves URL hash) |
| `browse.html` | **5,520** | **The archive browser.** Single-file SPA |
| `next.html` | 5,953 | Staging copy of `browse.html`; same origin, different filename, independent version line (`v1.07-test.NN`) |
| `richard-hunter.html` | ~190 | Biography page |
| `the-house.html` | ~230 | Narrative page |
| `archive.html` | ~230 | "How it's organised" page |
| `about.html` | ~210 | Mandate / people / contact |

### Top-level supporting files
- `manifest.json` + `manifest.next.json` — PWA manifests (live + staging variants)
- `sw.js` — no-op service worker (PWA install requirement)
- `README.md` — short project overview
- `WIKIBASE.md` — Wikibase property + QID reference (the data contract; updated as new properties are minted)
- `WIKIBASE_MAINPAGE.md` — working-notes file for the Wikibase Main Page wikitext
- `WIKIDATA_DRAFT.md` — three Wikidata items drafted for submission (Hunter person, CAA institution, Hunter fonds); pending
- `CLAUDE.md` + four `CLAUDE_archive_v1.0{2,5,6,7}.md` — solo-dev working memory + frozen historical logs (not loaded by any HTML; zero runtime cost)
- `EGC_intake.xlsx` — current intake spreadsheet for the Eric Gesinger Collection photographs (drawings already ingested)

### `assets/`

| Path | Size | Notes |
|---|---|---|
| `assets/verso.css` | 244 lines | Light design tokens + base styles |
| `assets/inverse.css` | 255 lines | Dark-mode token overrides (used only by the four reading pages) |
| `assets/pdfjs/` | **5.7 MB** | **Vendored Mozilla PDF.js v5.7.284** (pruned). One file patched: `web/viewer.mjs` extends `HOSTED_VIEWER_ORIGINS` to allow `bturep.github.io` + `localhost` (re-apply on upgrade). One added file: `web/hh-pdfjs.css` themes the minimal toolbar |
| `assets/placeholders/` | 192 KB | 3 JPEG tiers (`thumb`/`prev`/`large`) for items missing a preview image |
| `assets/icon-*.png`, `Hunter.png`, `hunter-mark.png` | 3.3 MB combined | PWA icons + the title-bar wordmark + the bio-page portrait |

### `curations/`
Two JSON files. `index.json` lists available curators (one entry today, `brandon-poole`); `brandon-poole.json` carries the curator's selection + bio + intro + per-item notes. Browser fetches at runtime. The curator-lens code is dormant on live `browse.html` (JSON load commented out) and active in `next.html`.

### `scripts/` — Python tooling, not shipped to the browser

Run from the maintainer's laptop against Wikibase + R2. Credentials read from `~/Documents/hh-wikibase-migration/.env` (outside the repo).

**Shared infrastructure**
- `_wikibase.py` — `load_env()` + `WikibaseSession` class (login + CSRF + retry-on-stale-token). Used by every script that writes to Wikibase.

**Admin write proxy**
- `edit_proxy.py` — local HTTP server on `127.0.0.1:8731` for `next.html`'s admin inline editing. Per-startup random token; CSRF-defended (Origin allowlist, JSON Content-Type required, exact-match origin)

**Ingest**
- `ingest_item.py` — single-image archive item ingest (master TIF → 3 R2 tiers → Wikibase item)
- `ingest_publication.py` — multi-page publication ingest (PDF + byte-for-byte masters + SHA-256 manifest + cover tiers)
- `batch_ingest_egc.py` — workbook-driven batch ingest (used once for the 30 EGC drawings; pattern for future collection batches)
- `mint_property.py` — idempotent property minter (used to add P143 / P144 / P145)

**Preservation pipeline** (added 2026-05-22)
- `backup_metadata.py` — read-only; dumps every Wikibase item + referenced vocab + properties into `data/snapshots/wikibase_full_YYYYMMDD/`
- `sync_metadata_to_r2.py` — rclone-pushes a local snapshot to R2 under `{collection-folder}/metadata/` + `_wikibase/`
- `sync_one_metadata.py` — single-item version; called fail-safe from each ingest script at end of every successful create
- `verify_r2_links.py` — read-only; SPARQLs every image / PDF URL claim AND every derived sidecar URL, HEAD-checks each

**One-off maintenance**
- `patch_dates.py`, `clean_titles.py`, `strip_counter_brackets.py`, `recolor_previews.py`, `fix_caa_scheme_split.py`, `renumber_caa.py`, `renumber_caa_25_32.py`, `regen_previews.py`, `regen_icons.py`, `rotate_images.py`

**`scripts/archived/`** — completed one-shot migrations + the `make_ges_intake.py` superseded by `batch_ingest_egc.py`

### `tests/`
Three Playwright smoke tests + a session-scoped HTTP-server fixture + a README explaining the one-time install. Dev-only; not in CI.

### `.github/`
- `workflows/validate.yml` — runs on every push to `main` + PRs
- `scripts/validate.mjs` — the validator (JS syntax via `node --check` on each inline `<script>` block, `VERSION` regex per file, manifest JSON parse)

### `data/`
- `curations/` — old, now under `curations/` at root (this dir holds snapshot artifacts)
- `snapshots/` — gitignored; `wikibase_full_YYYYMMDD/` (metadata dumps) and `r2_verify_*.json` (verifier reports) land here for local preservation

---

## 4. The browser — `browse.html` architecture

### 4.1 Single-file SPA

Everything ships in one HTML document: head meta, two inline `<style>` blocks (one tiny paint-holdout, one large component sheet), `<body>` shell, and a single inline `<script>` block holding the entire application (~3,700 lines of JS, ~140 top-level functions, no modules, no classes, no framework).

Loaded externally:
- `assets/verso.css` (the only render-blocking stylesheet)
- Google Fonts (Inter Tight, JetBrains Mono) via stylesheet `<link>`
- That's it.

### 4.2 First paint

A render-blocking `<style>` sets `html{background:#1a1816}` so visitors never see a white flash. A second pre-init `<script>` runs synchronously to detect desktop vs mobile via `matchMedia`; on desktop it sets `data-splash-init="1"` so the wordmark and topbar render in their splash positions from frame 1 (avoids a flash-then-fade as the main script catches up).

A CSS **view-transition** is wired (`@view-transition{navigation:auto}` + `.markid{view-transition-name:hh-mark}`) so the wordmark morphs smoothly from `index.html`'s splash to the corner of `browse.html`. Browsers without view-transition support degrade silently.

### 4.3 DOM shell

```
body
├── .site-top          (41 px top bar: HHFA wordmark · [?] · search · fullscreen)
├── .shell             (flex row)
│   ├── .panel-left    (~28 % wide, list pane; collapses to 41 px)
│   ├── .pane-image    (flex:1)
│   │   ├── #canvas    (image surface — zoom/pan/rotate)
│   │   ├── #pdf-frame (iframe → bundled PDF.js viewer; toggled by .pane-image.pdf-mode)
│   │   ├── .image-foot (status / view-PDF / download)
│   │   └── overlays   (#load-screen, #lightbox, #curator-pane "title wall", #curation-card)
│   └── .panel-right   (~28 % wide, record pane; collapses to 41 px)
└── modals             (#about-pane, #info-pane, #search-panel, #filter-panel, #mob-about, #mob-sheet)
```

Panel collapse is driven by `.panel-left.out` / `.panel-right.out` and an animated handle. A `body.refitting` class blanks the canvas during the 260 ms panel-width transition, then `setTimeout(280, fitToFrame)` re-fits the image so it doesn't visibly shrink.

### 4.4 Application JS — what's in there

The script section is laid out roughly in this order (line numbers from `browse.html` v1.06.31):

| Concern | Approx. lines | Key functions / state |
|---|---|---|
| Version + endpoint constants | 1772–1800 | `VERSION`, `VERSION_DISPLAY`, `WIKIBASE_URL`, `SPARQL_URL`, `CACHE_KEY` |
| Role / auth (researcher pins) | 1798–1822 | `RPINS` table, `rnRole()`, `canEditWikibase()`, `canMark()` — sessionStorage-keyed |
| Toast UI | 1835 | `hhToast()` |
| Local edit proxy client | 1843–1888 | `proxyEdit()`, `pingProxy()`, `proxyWatch()` (10 s heartbeat) |
| Wikibase write helpers | 1938–2014 | `vocabQuery`, `getVocab`, `setTimeClaim`, `setSingleItemClaim`, `setStringClaim`, `addMultiItem`, `removeMultiItem` |
| Field picker (inline editor) | 2016–2426 | `openFieldPicker`, `closeFieldPicker`, `canMintFor`, `mintNewVocab`, `mountMintConfirmUI`, `enterPhaseRename` |
| Researcher notes (private) | 2434–2645 | `rnLoad/Save/SyncRow`, `renderRN()` — two-step name→PIN auth, per-pin visibility |
| Marks / seen flags | 2646–2760 | `marksLoad/Save/Hydrate`, `seenLoad/Save/Hydrate`, `renderMarkBar` — per-pin localStorage |
| Bulk-edit mode | 2761–3100 | `bulkSelectRow`, `openBulkEdit`, `confirmBulkApply`, `applyBulkOp` (~20 operations via `BULK_APPLIERS` table) |
| Mobile bottom-sheet | 3125–3287 | `switchMobileTab`, `renderMobSheet`, swipe pipeline (axis-locked) |
| Lightbox | 3288–3335 | `openLightbox`, `lbFit/Apply/Clamp` |
| Panels + pip | 3336–3367 | `togglePanel`, `updatePip` |
| SPARQL fetch + cache | 3368–3565 | `sparqlQuery`, `clearCache`, `processRows`, `loadFromWikibase`, splash-prefetch from sessionStorage |
| Curator lens | 3451–3768 | `loadCurationIndex`, `getCuration`, `openCuratorPane`, `enterCuration`, `exitCuration` |
| Filter + search | 3567–3604, 4475–4607 | `applyFilters`, `clearAllFilters`, `updateFilterBadge`, `renderFilterPanel` |
| Render: list | 3605–3845 | `renderListHead`, `renderList`, `typeMark`, `pillCls` |
| Render: image stage | 3847–3996 | `renderImage` (loads thumb + large in parallel, swaps), placeholder fallback |
| Pan / zoom / rotate | 3998–4160 | `initPanZoom`, `fitToFrame`, `applyTransform`, `setZoom`, `constrainPan`; rotation persists per-item via P144 |
| Render: record pane | 4161–4385 | `renderMeta`, `EDITABLE` map (15 inline-editable properties), pill rendering, footer links |
| Selection / navigation | 4386–4439 | `selectItem`, `selectAdjacent`, mobile-tab sync |
| Wire / events | 4646–5143 | `wireControls`, `wireDropdown`, dropdown close logic, keyboard shortcuts |
| About + info panes | 5144–5217 | `openAboutPane`, `openInfoPane`, etc. |
| Collection info popovers | 5218–5282 | `openCollectionInfo`, `closeCollectionInfo` |
| PDF reader integration | 5283–5350 | `openPdf`, `closePdf`, `syncFootPdfView` |

### 4.5 Caching strategy

- **SPARQL response** is cached in `localStorage` under `CACHE_KEY = "hhf_" + VERSION`. Bumping `VERSION` is the entire cache-busting story. On every push the maintainer manually bumps the patch in `VERSION`.
- **Curator JSON** is fetched with `cache: "no-store"` and a `?v=${VERSION}` query string.
- The service worker (`sw.js`) does **not** cache anything; it exists only to satisfy the PWA installability requirement.
- Image caching relies on Cloudflare R2 + its CDN in front. R2 CORS allows `https://bturep.github.io`, `http://localhost`, `http://127.0.0.1` (GET/HEAD), 24 h max-age.

### 4.6 Theming

Two CSS surfaces:
- `verso.css` — light tokens, used everywhere.
- `inverse.css` — dark overrides, **loaded only by the four reading pages**. `browse.html` itself does its dark mode entirely from inline rules toggled by `html.dark`.

Theme persists via `localStorage["hhf_theme_v2"]`. Default is dark.

---

## 5. Data layer

### 5.1 Wikibase

The archive's source of truth is a **Wikibase Cloud** instance at `https://hunterhouse.wikibase.cloud`. The browser issues a single large `SELECT` to `/query/sparql` on load. The query reads ~25 properties per item.

Two guardrails inside the query:
- `?item wdt:P79 ?src` is **required** so the result set excludes vocabulary items, people, and institutions that happen to carry an HH archive ID.
- `?item wdt:P96 ?img` is **OPTIONAL** so stubs without a preview still appear in the list (rendered with a "No image yet" placeholder).

Item identifiers follow `HH-{COLLECTION}-{NNNN}` (e.g. `HH-HHC-0044`, `HH-CAA-0028`, `HH-EGC-0001`). Property IDs are catalogued in `WIKIBASE.md`. As of `next.html` `v1.07-test.52`, all PIDs the JS uses are declared in a single top-of-script `PROPERTIES = {…}` constant — opportunistic migration in progress, the rest of the catalogue SPARQL body still uses `wdt:Pxx` literals inside a template string.

### 5.2 Images — Cloudflare R2

Images live in one R2 bucket (`hunter-house-archive`) fronted by `archive.hunterhousefoundation.com`. The browser **does not know the R2 base URL** — every image URL is read out of the Wikibase response (`P96` preview, `P95` master). Filenames carry the archive ID + label + date + tier suffix:

```
HH-HHC-0044_Label_Date_thumb.jpg     (600 px,  75 % q)
HH-HHC-0044_Label_Date_prev.jpg      (2000 px, 82 % q)
HH-HHC-0044_Label_Date_large.jpg     (3840 px, 85 % q)
HH-HHC-0044_Label_Date.tif           (master, preservation copy)
```

`renderImage()` loads `_thumb` and `_large` in parallel; thumb paints first, large fades in. Mobile lightbox + bottom sheet use `_prev`. ICC profile is baked sRGB at ingest.

PDFs are uploaded with `Content-Disposition: attachment` so the foot-bar download link genuinely downloads rather than navigating in-tab.

### 5.3 Metadata sidecars — preservation backup on R2

Added 2026-05-22 in response to the audit's §11.1 HIGH item. Every Wikibase item's full `wbgetentities` JSON is mirrored to R2 as a sidecar:

```
{collection-folder}/metadata/{ARCH_ID}.json    catalogue items
_wikibase/items/{Qnnn}.json                    referenced vocab / people / institutions
_wikibase/properties/{Pnn}.json                property definitions
_wikibase/_manifest.json                       snapshot manifest
```

Two write paths feed it:
1. **Periodic full snapshot** — `backup_metadata.py` writes a local snapshot at `data/snapshots/wikibase_full_YYYYMMDD/`; `sync_metadata_to_r2.py` rclone-pushes that snapshot up. Run on demand, ideally before each session-end.
2. **Per-ingest** — `sync_one_metadata.py` is called fail-safe from each ingest script (`ingest_item.py`, `ingest_publication.py`, `batch_ingest_egc.py`) at the end of each successful per-item create. The catalogue and its R2 mirror stay in lock-step automatically.

If the Wikibase Cloud instance is ever lost, the entire archive is recoverable from the R2 sidecars via `wbeditentity`. The sidecars are also a useful general-purpose offline cache for the catalogue.

### 5.4 Curations
Editorial overlays loaded as static JSON from `/curations/`. Schema documented in `curations/brandon-poole.json`. Selection, order, and per-item notes are encoded in the JSON; the browser merges them with the catalogue items at render time and locks sort/filter while a curation is active.

---

## 6. Write path — `scripts/edit_proxy.py`

Admin in-browser editing exists in `next.html` (gated behind an admin PIN in `RPINS`) but **only fires when a small local Python HTTP server is running**. This is the maintainer's design choice: bot credentials never touch the public page.

```
browser (admin role)                localhost:8731 (Python)               hunterhouse.wikibase.cloud
─────────────────────               ──────────────────────                ─────────────────────────
proxyEdit({action, …,    ─POST→    edit_proxy.py
            secret: token})          - read bot creds from
                                       ~/Documents/hh-wikibase-migration/.env
                                     - assert action ∈ ALLOWED_ACTIONS
                                     - assert Origin ∈ ALLOWED (exact match)
                                     - assert Content-Type = application/json
                                     - assert secret (compare_digest, constant-time)
                                     - login, get CSRF, retry on badtoken
                                     - relay to MediaWiki action API     ──→  /w/api.php
                                     - return JSON
ui updates optimistically  ←JSON──
```

- **Listen**: `127.0.0.1:8731` (loopback only, never bound to LAN).
- **Allowed origins**: `https://bturep.github.io` (exact), `http(s)://localhost`, `http(s)://127.0.0.1` (any port).
- **Allowed Wikibase actions**: `wbsetlabel`, `wbsetdescription`, `wbsetaliases`, `wbcreateclaim`, `wbsetclaim`, `wbremoveclaims`, `wbeditentity`.
- **Auth**: **per-startup random token** (`secrets.token_urlsafe(24)`), printed to the proxy's stdout banner. The admin pastes it into `next.html`'s badge UI once per proxy-restart; `localStorage["hhf_proxy_token"]` carries it. `EDIT_PROXY_SECRET` in `.env` overrides for power users but loses the rotation benefit.
- **Token validation** via `/ping?secret=…` returns `{authenticated: bool}` so the browser can verify a pasted token without a real write.
- **Heartbeat**: the browser pings `/ping` every 10 s; missing token or bad token disables write controls and shows the paste form.

The other one-shot Python scripts in `scripts/` use the same credentials from `.env` for offline batch work; they don't touch the browser.

---

## 7. Live runtime dependencies

| Origin | What | Why | Critical? |
|---|---|---|---|
| `bturep.github.io` | `browse.html`, `assets/verso.css`, `assets/pdfjs/*`, icons, placeholders | The site itself | Yes |
| `hunterhouse.wikibase.cloud` | `/query/sparql` (catalogue + per-item write echo) | Data layer | Yes |
| `archive.hunterhousefoundation.com` (Cloudflare R2) | Image tiers + PDFs + metadata sidecars | Image / PDF bytes + preservation | Yes for media |
| `fonts.googleapis.com` + `fonts.gstatic.com` | Inter Tight + JetBrains Mono | Typography | Falls back to system fonts if blocked |

No analytics. No third-party JS. No advertising. No CDN-served JS libraries.

---

## 8. Quality + CI infrastructure

| Layer | What | Where |
|---|---|---|
| CI | One GitHub Actions workflow runs on every push to `main` and on PRs | `.github/workflows/validate.yml` |
| Validator | `node --check` on each inline `<script>` block in `browse.html` + `next.html`; `VERSION` regex match (live = `v\d+\.\d{2}\.\d{2}`, staging = `v\d+\.\d{2}-test\.\d{2}`); JSON parse on both manifests | `.github/scripts/validate.mjs` |
| Gate | **No** — does not block the push. Emails the owner on a failed run | (model: "alert, don't block") |
| Smoke tests | Three Playwright tests — catalogue loads via SPARQL, search→select→record-pane title renders, mobile shell at 375×812 | `tests/test_smoke.py` |
| Local server fixture | Session-scoped `http.server` on a random loopback port rooted at the repo (so relative `fetch()` paths work) | `tests/conftest.py` |
| Smoke-test cadence | Maintainer's local use; not in CI (would need Playwright browsers + tolerance for SPARQL flakiness) | `pytest tests/` |
| Integrity check | `scripts/verify_r2_links.py` — SPARQLs every URL claim (`P95` / `P96` / `P143`) AND every derived sidecar URL; HEAD-checks each. Read-only, no creds. Suggested cadence: before each session-end | |
| Pre-push validation locally | `node .github/scripts/validate.mjs` runs in ~1 s; same checks as CI | |

---

## 9. Git repository — current state

| | |
|---|---|
| Commits on `main` | **579** |
| First commit | `2026-05-12` (`8261c57` "Add files via upload") |
| Latest commit | `2026-05-22` end-of-session |
| Contributors | **1** — `bturep` (`brandonturepoole@gmail.com`) |
| Tags | 14 — `v0.6`, `v0.7`, `v1.0`, `v1.01.00`, `v1.1.1`, `v1.02.00`, `v1.02.18`, `v1.03.00`, `v1.03.01`, `v1.03.08`, `v1.03.28`, `v1.04.00`, `v1.05.00`, `v1.06.00` |
| Branches (local) | `main`, `v1.04` |
| Branches (remote) | `origin/main`, `origin/v1.04` (`origin/refactor/browse-cleanup` deleted 2026-05-22 as stale) |
| Versioning | `vMAJOR.SESSION.PATCH`, two-digit zero-padded. `SESSION` rolls per work-day; `PATCH` rolls per push |
| Working-copy size | 150 MB |
| `.git` size | 136 MB (history is heavy with binary churn — TIF intake, PDFs, large PNGs committed over time) |
| `.gitignore` | Excludes `__pycache__/`, `*.pyc`, Excel lock files, `.env*`, `data/snapshots/wikibase_full_*/`, `data/snapshots/r2_verify_*.json`, `.DS_Store`, pytest/playwright caches |
| Remote | `git@github.com:bturep/HunterHouse.git` |
| Hosting | GitHub Pages, default config. CI lives under `.github/`; no other workflow files |

---

## 10. Audit — observations + risks

These are observations from the codebase itself. The **actionable** items that arose from a deeper security + maintainability pass are catalogued separately in §11 below, along with their current resolution status.

### Architecture & maintainability
- **Single-file SPA, ~5,520 lines, ~140 top-level functions, no module boundaries.** Functions communicate through module-scope `let`s (`state`, `zoomState`, `_proxyOnline`, etc.). The script reads top-to-bottom; there is no entry-point indirection beyond `main()` and `wireControls()`. Comments are dense and current, but any one feature touches many call sites.
- **`next.html` is a near-duplicate of `browse.html`** (5,953 vs 5,520 lines). The staging strategy is "copy the file, version it, deploy alongside" rather than a branch / preview-env. It works on plain GitHub Pages with no extra infra, but doubles the surface area for the duration of a development cycle. `verso.css` is shared between live and staging.
- **No build step.** Easy to onboard, but no minification, no transpilation, no tree-shaking. The ~280 KB HTML payload is what visitors download (uncompressed; GitHub Pages serves it gzipped).
- **`localStorage` is the only persistence layer in the browser.** Cache key is `"hhf_" + VERSION`. There is no migration story for stored shapes — a `VERSION` bump simply orphans the previous cache entry.

### Security
- **Public site is read-only.** No write path is exposed to the public.
- **Admin writes** route through the local proxy with bot credentials never leaving the maintainer's machine. CSRF defences: per-startup random token, exact-match Origin allowlist, JSON-only Content-Type.
- **No CSP header / meta tag** is set on `browse.html`. The site embeds Google Fonts and is itself the only script source, so impact is small, but a `Content-Security-Policy` would be cheap to add.
- **`RPINS` is shipped in cleartext** in the HTML (e.g. `"203BTP"` maps to admin). That's accepted because (a) it gates UI, not data, and (b) writes require the loopback proxy + the per-startup token + the bot credentials in `.env` that aren't in the repo. Worth flagging because it looks like a secret at first glance and isn't.

### Repository hygiene
- **`.git` is 136 MB on a 150 MB working tree.** History contains large binaries (early TIF intake, PDFs, large PNGs). A reviewer cloning shallow is fine; full clones are heavier than the runtime surface suggests.
- **Solo-author project**: no review pipeline, no `CODEOWNERS`, no PR template. Every push goes straight to `main`. The validate workflow + Playwright smoke tests are the only programmatic safety nets.

### Runtime risks
- **No retry / backoff** on the SPARQL fetch. If `hunterhouse.wikibase.cloud` is slow or down, the page renders an empty list (the splash overlay covers this gracefully). The cached SPARQL response in `localStorage` is the fallback.
- **Single SPARQL query loads the entire catalogue** (currently ~180 items). Fine at this scale; will need pagination if it grows by ~1–2 orders of magnitude.
- **Manual cache-bust.** If the maintainer forgets to bump `VERSION` before pushing, returning visitors hit a stale localStorage cache and the new SPARQL shape may not render correctly. Validate workflow catches `VERSION` shape but not "did you bump it".
- **Patched PDF.js (`viewer.mjs`).** A PDF.js upgrade will silently re-introduce the CORS rejection unless the `HOSTED_VIEWER_ORIGINS` patch is re-applied. Noted in code comments.

### Browser support
- Uses **CSS view transitions**, CSS custom properties, modern `flex/grid`, optional chaining, `async/await`. Safe on Chromium / Safari 17+ / Firefox 121+.
- Mobile breakpoint is `(max-width:767px)`. Mobile is intentionally read-only (no admin UI, no PIN flow). iOS Safari is the primary mobile target.

---

## 11. Targeted security + maintainability pass (2026-05-22) — status

A deeper pass over the codebase on 2026-05-22 produced an actionable to-do list with three severity tiers. Almost everything in tiers Now / Soon has been resolved within the same day. Tier "Bend before break" is by-design a watch-list — items there are deliberately deferred until triggered.

File:line references below were originally captured against `next.html` `v1.07-test.51` and `browse.html` `v1.06.20`; live `browse.html` is now still at `v1.06.31` (the work was on `next.html`), and `next.html` is at `v1.07-test.54`.

### 11.1 Now (security-meaningful) — **complete**

- ✅ **CSRF + auth on edit proxy (steps 1, 2, 3 + MEDIUM `startswith`).** `scripts/edit_proxy.py` now validates `Origin` against an exact-match allowlist before reading the body, requires `Content-Type: application/json`, uses `urlparse`-based hostname matching, and authenticates with a per-startup random `secrets.token_urlsafe(24)` token validated via constant-time `compare_digest`. The browser stores the pasted token in `localStorage["hhf_proxy_token"]` and revalidates on every `/ping`; an inline paste form appears in the bottom-left badge when the token is missing or stale. The hardcoded `"203BTP"` fallback is gone. See §6 for the full sequence diagram.

- ✅ **Wikibase metadata has an offsite backup.** The local catalogue is mirrored to R2 as JSON sidecars (`{collection-folder}/metadata/{ARCH_ID}.json` + `_wikibase/items/Qnnn.json` + `_wikibase/properties/Pnn.json` + a manifest). Three scripts: `backup_metadata.py` (dump local), `sync_metadata_to_r2.py` (rclone push), `sync_one_metadata.py` (per-item, called fail-safe from each ingest script). Initial run mirrored 332 entities = 3.0 MB. From now on every new item produces a sidecar at ingest time. See §5.3.

### 11.2 Soon (operational hygiene) — **complete**

- ✅ **Pre-push validation in CI.** `.github/workflows/validate.yml` runs on every push and PR — `node --check` per inline `<script>` block, `VERSION` regex per file, manifest JSON parse. Does not gate the push (alerts via email on failure). See §8.

- ✅ **Python boilerplate dedup.** `scripts/_wikibase.py` extracted `load_env()` + `WikibaseSession` (login + CSRF + retry-on-stale-token) from the copy-pasted boilerplate that lived in 11 scripts. Two scripts (`patch_dates.py`, `mint_property.py`) migrated as proof; the rest will follow opportunistically as they're touched.

- ✅ **PIDs central dictionary.** `next.html` declares a top-of-script `PROPERTIES = {…}` constant for all 27 PIDs the application uses. The `EDITABLE` map, the `ACCESS_COPY` + `DISPLAY_ROTATION` call sites, and the SPARQL `OPTIONAL` lines for those two are migrated. The rest of the catalogue SPARQL body still uses bare `wdt:Pxx` literals — deferred-by-design (opportunistic, not big-bang).

- ✅ **Researcher-notes label honesty.** Lock-icon tooltips in `next.html` re-worded to stop implying encryption. `localStorage` storage shape unchanged.

- ✅ **`.env` / `.gitignore` hygiene.** `.env`, `.env.*` (with a `!.env.example` allowance), and the per-run snapshot directories are gitignored. History audit clean: no credentials in commit log.

### 11.3 Bend before break (watch; refactor when triggered)

- ✅ **Image pipeline integrity check.** `scripts/verify_r2_links.py` SPARQL-fetches every URL claim (`P95` / `P96` / `P143`) AND every derived metadata sidecar URL, HEAD-checks each against R2. First run surfaced six dead `P95` URLs from the 2026-05-14 HH-A → HH-HHC rename migration; **fixed same-day** by `scripts/archived/fix_p95_legacy_urls_20260522.py`. All 354 URL claims + 180 sidecar URLs now return 200.

- ✅ **Smoke tests.** Three Playwright tests under `tests/` (catalogue-loads / search-and-select / mobile-shell). Dev-only; explicitly not in CI. See §8.

- ◐ **`renderMeta` / `renderMobSheet` duplication.** Honest reassessment: the two functions have diverged in purpose (mobile = read-only public; desktop = admin-aware with active-state filter-buttons + EM placeholders). The literally-duplicated bits (the rights "Contact for…" prose, the finding-aid `<a>` rendering) have been extracted into three shared helpers (`archiveContactText`, `rightsRowHTML`, `findingAidHTML`). The full `buildRows()` unification the audit suggested is **deferred by design** — forcing it now would be a high-risk refactor for a "pays off when adding an editable field" maintainability gain. Revisit when triggered.

- ⏸ **HTML monolith approaching the inflection point.** `next.html` is now at ~5,950 lines. The audit's "worry around 7–8 K" trigger hasn't fired; no action today.

- ⏸ **`state.curation` checks at ~26 sites.** Audit explicitly recommended not refactoring pre-emptively. No action.

### 11.4 Resolved on inspection (looked like issues; aren't)

- **Curator-name XSS path.** `bioEscaped.split(name).join(nameSpan)` splits by the *escaped* name, not raw — defended.
- **Python scripts: no shell injection.** All `subprocess` calls use list args; no `shell=True`.
- **PDF.js v5.7.284.** No known CVEs against this patch version as of audit. Re-check on upgrade.
- **R2 CORS allows `http://localhost` + `http://127.0.0.1`.** Fine — public read-only assets.
- **GitHub Pages HTTPS.** Enforced by default. No `.env` / R2 keys / Wikibase password in git history.

---

## 12. Where to start reading

For an engineer with ~1 hour:

1. **`browse.html` lines 1–250** — head, paint-holdout, inline CSS tokens.
2. **`browse.html` lines 1770–1830** — `VERSION`, endpoints, `RPINS`, role helpers.
3. **`browse.html` lines 3368–3565** — `sparqlQuery`, `CATALOGUE_QUERY`, `loadFromWikibase`, `processRows`. The data spine.
4. **`browse.html` lines 4161–4385** — `renderMeta` + `EDITABLE`. The record pane + inline editing.
5. **`scripts/edit_proxy.py`** — ~200 lines; the entire write path + CSRF defences.
6. **`scripts/_wikibase.py`** — ~140 lines; the shared Wikibase client used by every write-script.
7. **`WIKIBASE.md`** — property table + QID list; the data contract.
8. **`tests/test_smoke.py`** — three smoke tests; useful as a worked example of what to expect functionally.

Everything else is layered on those eight points.
