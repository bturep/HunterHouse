# Hunter House Foundation Archive — architecture brief

For a software engineer inspecting the live site. Scope = what `https://bturep.github.io/HunterHouse/` actually serves today, plus the repository state behind it. Snapshot date: **2026-05-22**, live `browse.html` `v1.06.31`.

---

## 1. TL;DR

A **single-page, zero-build static site** served from GitHub Pages. The catalogue browser is one ~278 KB HTML file (`browse.html`, ~5,520 lines) containing inline CSS and vanilla ES2020 JavaScript. It reads its data at runtime from a public **Wikibase Cloud** instance via **SPARQL over HTTPS**, and loads images from a public **Cloudflare R2** bucket (URLs are stored as values inside Wikibase, not hard-coded). There is no backend, no build step, no framework, no bundler, no package manager, no test suite, and no CI. Admin writes happen only on the maintainer's own laptop, via a small Python HTTP proxy on `localhost:8731` that holds the Wikibase bot credentials server-side.

The architecture is deliberately small. The complexity that exists is concentrated in (a) the single HTML file and (b) the data model in Wikibase.

---

## 2. Project at a glance

| | |
|---|---|
| Live URL | `https://bturep.github.io/HunterHouse/` (PWA `start_url` → `browse.html`) |
| Repo | `github.com/bturep/HunterHouse` (default branch `main`) |
| Hosting | GitHub Pages, default config (no workflow files) — push to `main` ⇒ live in ~30 s |
| Languages | HTML, CSS, vanilla JS (no TypeScript, no JSX); Python 3 for offline scripts |
| Build / bundler | **None.** Files served verbatim. |
| Package manager | **None.** No `package.json`, no `node_modules`. |
| Tests | **None.** |
| CI | **None.** No `.github/workflows`. |
| External runtime deps | Google Fonts (Inter Tight, JetBrains Mono); bundled PDF.js (vendored, not CDN) |
| Browser support target | Modern evergreen (uses CSS view transitions, `matchMedia`, ES2020); mobile = iOS Safari is the primary mobile target |
| PWA | Yes — minimal `manifest.json` + no-op `sw.js` (no offline cache) |
| Data backend | Wikibase Cloud SPARQL: `https://hunterhouse.wikibase.cloud/query/sparql` |
| Image / PDF storage | Cloudflare R2, public bucket aliased at `archive.hunterhousefoundation.com` |
| Author / contributors | Solo: `bturep` (570 of 570 commits) |

---

## 3. Repository layout (what's actually shipped)

Live HTML pages served from repo root:

| File | Lines | Role |
|---|---|---|
| `index.html` | 28 | Thin JS+meta redirect to `browse.html` (preserves URL hash). |
| `browse.html` | **5,520** | **The archive browser.** Single-file SPA. |
| `next.html` | 5,667 | Staging copy of `browse.html`, deployed to the same origin under a different filename. Versioned independently (`v1.07-test.NN`). Real visitors don't reach it from the splash; it's accessible by direct URL. |
| `richard-hunter.html` | ~190 | Biography page (static content). |
| `the-house.html` | ~230 | Narrative page. |
| `archive.html` | ~230 | "How it's organised" page. |
| `about.html` | ~210 | Mandate / people / contact. |

Repo root also contains: `manifest.json` (PWA), `manifest.next.json` (staging PWA), `sw.js` (no-op service worker), several reference / draft documents (`README.md`, `WIKIBASE.md`, `WIKIBASE_MAINPAGE.md`, `WIKIDATA_DRAFT.md`, `Main_Page.wiki`), and four working-memory archives (`CLAUDE.md`, `CLAUDE_archive_v1.0{2,5,6,7}.md` — solo-dev notebook, not part of the runtime).

Three HTML files at the root are dormant / stub: `index-video.html`, `import-rn.html`, `swatches.html`. Not linked from the splash flow but reachable by URL.

### `assets/`

| Path | Size | Notes |
|---|---|---|
| `assets/verso.css` | 244 lines | Light design tokens + base styles. |
| `assets/inverse.css` | 255 lines | Dark-mode token overrides (toggled via `html.dark`). |
| `assets/pdfjs/` | **5.7 MB** | **Vendored Mozilla PDF.js v5.7.284** (pruned). One file is patched: `web/viewer.mjs` extends `HOSTED_VIEWER_ORIGINS` to allow `bturep.github.io` + `localhost` (re-apply on upgrade). One added file: `web/hh-pdfjs.css` hides everything outside the "Minimal" toolbar and themes the rest. |
| `assets/placeholders/` | 192 KB | 3 JPEG tiers (`thumb`/`prev`/`large`) for items missing a preview image. |
| `assets/icon-*.png`, `Hunter.png`, `hunter-mark.png` | 3.3 MB combined | PWA icons + the title-bar wordmark. |

### `curations/`
Two JSON files. `index.json` lists available curators (one entry today, `brandon-poole`); `brandon-poole.json` carries that curator's selection + bio + intro + per-item notes. The browser fetches these at runtime. On live `browse.html` the fetch is currently commented out (curator lens dormant on live; active in `next.html`).

### `scripts/`
Python tooling, **not shipped to the browser** — run from the maintainer's laptop against Wikibase + R2. 17 active scripts (one-shot ingest, batch ingest, ICC re-encode, renumber migrations, the local `edit_proxy.py`) plus an `archived/` subdir for retired migrations. Credentials are read from `~/Documents/hh-wikibase-migration/.env` (outside the repo).

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
| Researcher notes (private) | 2434–2645 | `rnLoad/Save/SyncRow`, `renderRN()`, two-step name→PIN auth, per-pin visibility model |
| Marks / seen flags | 2646–2760 | `marksLoad/Save/Hydrate`, `seenLoad/Save/Hydrate`, `renderMarkBar` — per-pin localStorage |
| Bulk-edit mode | 2761–3100 | `bulkSelectRow`, `openBulkEdit`, `confirmBulkApply`, `applyBulkOp` (~20 operations via `BULK_APPLIERS` table) |
| Mobile bottom-sheet | 3125–3287 | `switchMobileTab`, `renderMobSheet`, swipe pipeline (axis-locked) |
| Lightbox | 3288–3335 | `openLightbox`, `lbFit/Apply/Clamp` |
| Panels + pip | 3336–3367 | `togglePanel`, `updatePip` |
| SPARQL fetch + cache | 3368–3565 | `sparqlQuery`, `clearCache`, `processRows`, `loadFromWikibase`, splash-prefetch from sessionStorage |
| Curator lens (Phase 1) | 3451–3768 | `loadCurationIndex`, `getCuration`, `openCuratorPane`, `enterCuration`, `exitCuration`, `renderCurationCard`, `renderCuratorNote` — JSON load currently commented out on live |
| Filter + search | 3567–3604, 4475–4607 | `applyFilters`, `clearAllFilters`, `updateFilterBadge`, `renderFilterPanel` |
| Render: list | 3605–3845 | `renderListHead`, `renderList`, `typeMark`, `pillCls` |
| Render: image stage | 3847–3996 | `renderImage` (loads thumb + large in parallel, swaps), placeholder fallback |
| Pan / zoom / rotate | 3998–4160 | `initPanZoom`, `fitToFrame`, `applyTransform`, `setZoom`, `constrainPan`; rotation persists per-item via P144 |
| Render: record pane | 4161–4385 | `renderMeta`, `EDITABLE` map (15 inline-editable properties), pill rendering, footer links |
| Selection / navigation | 4386–4439 | `selectItem`, `selectAdjacent`, mobile-tab sync |
| Wire / events | 4646–5143 | `wireControls`, `wireDropdown`, dropdown close logic, keyboard shortcuts |
| About + info panes | 5144–5217 | `openAboutPane`, `openInfoPane`, etc. |
| Collection info popovers | 5218–5282 | `openCollectionInfo`, `closeCollectionInfo` |
| PDF reader integration | 5283–5350 | `openPdf`, `closePdf`, `syncFootPdfView` — opens bundled PDF.js viewer in `#pdf-frame` |

### 4.5 Caching strategy

- **SPARQL response** is cached in `localStorage` under `CACHE_KEY = "hhf_" + VERSION`. Bumping `VERSION` is the entire cache-busting story — there is no other invalidation path. On every push the maintainer manually bumps the patch in the `VERSION` constant.
- **Curator JSON** is fetched with `cache: "no-store"` and a `?v=${VERSION}` query string.
- The service worker (`sw.js`) does **not** cache anything; it exists only to satisfy the PWA installability requirement (it calls `skipWaiting` + `clients.claim`, nothing else).
- The maintainer relies on Cloudflare R2 + the CDN in front of it for image caching. R2 CORS is configured to allow `https://bturep.github.io`, `http://localhost`, `http://127.0.0.1` (GET/HEAD), 24 h max-age.

### 4.6 Theming

Two CSS surfaces:
- `verso.css` — light tokens, used everywhere.
- `inverse.css` — dark overrides, **loaded only by the four reading pages** (`richard-hunter.html`, `the-house.html`, `archive.html`, `about.html`). `browse.html` itself does its dark mode entirely from inline rules toggled by `html.dark`.

Theme persists via `localStorage["hhf_theme_v2"]`. Default is dark.

---

## 5. Data layer

### 5.1 Wikibase

The archive's source of truth is a **Wikibase Cloud** instance at `https://hunterhouse.wikibase.cloud`. The browser issues a single large `SELECT` to `/query/sparql` on load. The query reads ~25 properties per item (id, label, image URLs, three date predicates, phase / drawing-type / area / category / item-type vocab, source collection, creator / built-by / designed-by, scale / medium / use, built status, position-in-set, notes, rights, held-by, archive link, physical location, access copy URL, rotation). It is the only outbound application data fetch.

Two guardrails inside the query:
- `?item wdt:P79 ?src` is **required** so the result set excludes vocabulary items, people, and institutions that happen to carry an HH archive ID.
- `?item wdt:P96 ?img` is **OPTIONAL** so stubs without a preview still appear in the list (rendered with a "No image yet" placeholder).

Item identifiers follow `HH-{COLLECTION}-{NNNN}` (e.g. `HH-HHC-0044`, `HH-CAA-0028`, `HH-EGC-0001`). Property IDs are catalogued in `WIKIBASE.md` and referenced by `P##` constants in the browser code.

### 5.2 Images — Cloudflare R2

Images live in a single R2 bucket (`hunter-house-archive`) fronted by the public hostname `archive.hunterhousefoundation.com`. The browser **does not know the R2 base URL** — every image URL is read out of the Wikibase response (`P96` preview URL, `P95` master URL). Per-item filenames carry the archive ID + label + date + tier suffix:

```
HH-HHC-0044_Label_Date_thumb.jpg     (600 px,  75 % q)
HH-HHC-0044_Label_Date_prev.jpg      (2000 px, 82 % q)
HH-HHC-0044_Label_Date_large.jpg     (3840 px, 85 % q)
HH-HHC-0044_Label_Date.tif           (master, preservation copy)
```

`renderImage()` loads `_thumb` and `_large` in parallel; the thumb paints first, the large fades in. Mobile lightbox + bottom sheet use `_prev`. ICC profile is baked sRGB at ingest (a Chrome-on-wide-gamut-Mac cyan-cast was triaged + fixed by re-encoding 254 existing JPEGs).

PDFs are uploaded with `Content-Disposition: attachment` so the foot-bar download link genuinely downloads rather than navigating in-tab.

### 5.3 Curations
Editorial overlays loaded as static JSON. Schema is documented in `curations/brandon-poole.json`. Selection, order, and per-item curator notes are encoded in the JSON; the browser merges them with the catalogue items at render time and locks sort/filter while a curation is active.

---

## 6. Write path — `scripts/edit_proxy.py`

Admin in-browser editing exists in `browse.html` (gated behind an admin PIN held in `RPINS`) but **only fires when a small local Python HTTP server is running**. This is the maintainer's design choice: bot credentials never touch the public page.

```
browser (admin role)              localhost:8731 (Python)              hunterhouse.wikibase.cloud
─────────────────────             ──────────────────────               ─────────────────────────
proxyEdit({action, ...})  ─POST→  edit_proxy.py
                                  - read bot creds from
                                    ~/Documents/hh-wikibase-migration/.env
                                  - assert action ∈ ALLOWED_ACTIONS
                                  - login, get CSRF, retry on badtoken
                                  - relay to MediaWiki action API  ──→  /w/api.php
                                  - return JSON
ui updates optimistically  ←JSON──
```

- **Listen**: `127.0.0.1:8731` (loopback only, never bound to LAN).
- **Allowed origins**: `https://bturep.github.io`, `http://localhost`, `http://127.0.0.1`.
- **Allowed Wikibase actions**: `wbsetlabel`, `wbsetdescription`, `wbsetaliases`, `wbcreateclaim`, `wbsetclaim`, `wbremoveclaims`, `wbeditentity`.
- **Auth**: per-request secret = admin PIN (or `EDIT_PROXY_SECRET` from `.env`).
- **Heartbeat**: the browser pings `/ping` every 10 s; if the proxy is offline the page shows "edit proxy offline" and disables write controls. Public visitors never see this UI.

A handful of one-shot Python scripts (`ingest_item.py`, `ingest_publication.py`, `batch_ingest_egc.py`, `patch_dates.py`, `renumber_caa.py`, `recolor_previews.py`, etc.) use the same credentials for offline batch work; they don't touch the browser.

---

## 7. Live runtime dependencies

Everything the browser fetches when a visitor opens the live site:

| Origin | What | Why | Critical? |
|---|---|---|---|
| `bturep.github.io` | `browse.html`, `assets/verso.css`, `assets/pdfjs/*`, icons, placeholders | The site itself | Yes |
| `hunterhouse.wikibase.cloud` | `/query/sparql` (catalogue + per-item write echo) | Data layer | Yes |
| `archive.hunterhousefoundation.com` (Cloudflare R2) | Image tiers + PDFs | Image & PDF bytes | Yes for media |
| `fonts.googleapis.com` + `fonts.gstatic.com` | Inter Tight + JetBrains Mono | Typography | Falls back to system fonts if blocked |

No analytics. No third-party JS. No advertising. No CDN-served JS libraries.

---

## 8. Git repository — current state

| | |
|---|---|
| Commits on `main` | **566** |
| First commit | `2026-05-12` (`8261c57` "Add files via upload") |
| Latest commit | `2026-05-22` (`d1cca59` "next: reskin curator mode to Vellum palette") |
| Contributors | **1** — `bturep` (`brandonturepoole@gmail.com`) — 570/570 commits |
| Tags | 14 — `v0.6`, `v0.7`, `v1.0`, `v1.01.00`, `v1.1.1`, `v1.02.00`, `v1.02.18`, `v1.03.00`, `v1.03.01`, `v1.03.08`, `v1.03.28`, `v1.04.00`, `v1.05.00`, `v1.06.00` |
| Branches (local) | `main`, `v1.04` |
| Branches (remote) | `origin/main`, `origin/v1.04`, `origin/refactor/browse-cleanup` (stale) |
| Versioning scheme | `vMAJOR.SESSION.PATCH`, two-digit zero-padded. `SESSION` rolls per work-day; `PATCH` rolls per push. Tags pushed at session and major boundaries. |
| Working-copy size | 146 MB |
| `.git` size | **135 MB** (history is heavy with binary churn — TIF intake, PDFs, large PNGs committed over time) |
| `.gitignore` | Minimal — `__pycache__/`, `*.pyc`, `*.pyo`, Excel `~$*.xls{x}` lock files |
| Untracked at snapshot | `WIKIDATA_DRAFT.md` (modified), `GES_intake.xlsx`, `swatches.html` |
| Remote | `git@github.com:bturep/HunterHouse.git` (SSH key per-account) |
| Hosting | GitHub Pages, default config — no `.github/` directory exists; no Actions, no Pages workflow file. |

All 566 commits land in May 2026 — the project is one month old.

---

## 9. Audit — things a reviewer should know

These are observations from the codebase itself, not the maintainer's roadmap.

### Architecture & maintainability
- **Single-file SPA, ~5,520 lines, ~140 top-level functions, no module boundaries.** Functions communicate through module-scope `let`s (`state`, `zoomState`, `_proxyOnline`, etc.). The script reads top-to-bottom; there is no entry-point indirection beyond `main()` and `wireControls()`. Comments are dense and current, but any one feature touches many call sites.
- **`next.html` is a 284 KB near-duplicate of `browse.html`** (5,667 vs 5,520 lines). The staging strategy is "copy the file, version it, deploy alongside" rather than a branch / preview-env. It works on plain GitHub Pages with no extra infra, but doubles the surface area for the duration of a development cycle. `verso.css` is shared between live and staging (an inline-style change isolates to one file; a `verso.css` change touches both).
- **No tests, no linter, no formatter, no CI.** Quality control is entirely manual + the maintainer's own review loop. A regression is only discoverable by running the page.
- **No build step at all.** Easy to onboard, but no minification, no transpilation, no tree-shaking, no dead-code elimination. The 278 KB HTML payload is what visitors download (uncompressed; GitHub Pages serves it gzipped).
- **`localStorage` is the only persistence layer in the browser.** Cache key is `"hhf_" + VERSION`. There is no migration story for stored shapes — a `VERSION` bump simply orphans the previous cache entry (the code reads only the current key, doesn't garbage-collect old ones).

### Security
- **Public site is read-only.** No write path is exposed to the public — the admin PIN is checked only to unlock UI; actual writes require the local Python proxy on the maintainer's laptop, with bot credentials never leaving that machine.
- **No CSP header / meta tag** is set on `browse.html`. Site embeds Google Fonts and is itself the only script source, so impact is small, but a `Content-Security-Policy` would be cheap to add.
- **`RPINS` is shipped in cleartext** in the HTML (e.g. `"203BTP"` maps to admin). That's accepted because (a) it gates UI, not data, and (b) writes require the loopback proxy + the bot credentials in `.env` that aren't in the repo. Worth flagging because it looks like a secret at first glance and isn't.
- **Service worker is a no-op** — there's no offline cache, no stale-while-revalidate, no risk of stale-asset poisoning. The PWA installs but doesn't behave like one.
- **Edit proxy** is bound to `127.0.0.1` only and checks `Origin` against an allowlist; bot credentials read from a file outside the repo.

### Repository hygiene
- **`.git` is 135 MB on a 146 MB working tree.** History contains large binaries (Excel intake sheets, the 3 MB `Hunter.png`, the 5.7 MB PDF.js bundle, various reference PDFs). A reviewer cloning shallow is fine; full clones are heavier than the runtime surface suggests.
- **Stale remote branch** `origin/refactor/browse-cleanup` exists with no local tracking branch — could be pruned.
- **Three orphan HTML files** in repo root (`index-video.html`, `import-rn.html`, `swatches.html`) aren't linked from the splash flow but are reachable by URL on the live site. Worth confirming they're intentional.
- **Working memory committed to the repo** (`CLAUDE.md` + four `CLAUDE_archive_v1.0{2,5,6,7}.md` files, ~250 KB combined). They are not loaded by any HTML and have no runtime cost; they double as a per-session changelog and as context for a coding assistant.
- **Solo-author project**: no review pipeline, no `CODEOWNERS`, no PR template. Every push goes straight to `main`.

### Runtime risks
- **No retry / backoff** on the SPARQL fetch. If `hunterhouse.wikibase.cloud` is slow or down, the page renders an empty list (the splash overlay covers this gracefully but no error UI is shown beyond a toast). The cached SPARQL response in `localStorage` is the fallback.
- **Single SPARQL query loads the entire catalogue** (currently ~190 items). Fine at this scale; will need pagination or a per-collection split if it grows by ~1–2 orders of magnitude.
- **Manual cache-bust.** If the maintainer forgets to bump `VERSION` before pushing, returning visitors hit a stale localStorage cache and the new SPARQL shape may not render correctly. There is no defensive check that the cached row shape matches the current parser.
- **Patched PDF.js (`viewer.mjs`).** A PDF.js upgrade will silently re-introduce the CORS rejection unless the `HOSTED_VIEWER_ORIGINS` patch is re-applied. This is noted in code comments.
- **Google Fonts is the only third-party origin in the critical path.** If blocked, typography degrades to fallback; nothing functional breaks.

### Browser support
- Uses **CSS view transitions** (`@view-transition`), CSS custom properties, modern `flex/grid`, optional chaining, `async/await`. Safe on Chromium / Safari 17+ / Firefox 121+. No deliberate IE / legacy support.
- Mobile breakpoint is `(max-width:767px)`. Mobile is intentionally read-only (no admin UI, no PIN flow). iOS Safari is the primary mobile target; one known iOS-Safari fix is shipped (tap-target padding + `touch-action:manipulation` on the splash Continue button).

---

## 10. Where to start reading

For an engineer with ~1 hour:

1. **`browse.html` lines 1–250** — head, paint-holdout, inline CSS tokens.
2. **`browse.html` lines 1770–1830** — `VERSION`, endpoints, `RPINS`, role helpers.
3. **`browse.html` lines 3368–3565** — `sparqlQuery`, `CATALOGUE_QUERY`, `loadFromWikibase`, `processRows`. This is the data spine.
4. **`browse.html` lines 4161–4385** — `renderMeta` + `EDITABLE`. This is how the record pane is built and how inline editing is wired.
5. **`scripts/edit_proxy.py`** (~140 lines) — the entire write path.
6. **`WIKIBASE.md`** — property table + QID list; the Wikibase shape is the data contract.

Everything else is layered on those six points.

---

## 11. To do — from 2026-05-22 audit

Distinct from §9 (observational): these are actionable items from a deeper security + maintainability pass on 2026-05-22, prioritised by severity and effort. File:line references are against `next.html` at `v1.07-test.51` and `browse.html` at `v1.06.20` unless noted.

### 11.1 Now (security-meaningful; do this week)

- **[CRITICAL] Edit proxy is CSRF-exploitable in principle.** `scripts/edit_proxy.py` lines 34, 46, 85–126.
  - Three compounding facts: (a) the auth secret is the admin pin, which is hardcoded in public client code (`RPINS = {"203BTP": …}` at `next.html:1930`, `browse.html:1798`), and `edit_proxy.py:46` falls back to `"203BTP"` when `.env` lacks `EDIT_PROXY_SECRET`; (b) `_cors` at line 86–91 only *sets* the response ACAO header conditionally — `do_POST` never *rejects* mismatched origins before reading the body; (c) the proxy parses the body with `json.loads` without checking `Content-Type`, so a `text/plain` body bypasses CORS preflight as a "simple request" and the side-effect lands before the browser sees the (wrong) ACAO.
  - **Today's mitigation:** Chrome Private Network Access preflights cross-origin requests to `127.0.0.1` and the proxy doesn't return `Access-Control-Allow-Private-Network: true`, so the path is blocked in modern Chrome. Safari and older Firefox are not fully covered.
  - **Fix (~2 hours):**
    1. In `do_POST`, validate `self.headers.get("Origin")` against `ALLOWED_ORIGINS` (exact match, not `startswith`) *before* reading the body. Return 403 on mismatch.
    2. Reject any `Content-Type` other than `application/json`. This forces preflight and re-establishes CORS as a real check.
    3. Replace the fallback `"203BTP"` secret with a per-startup `secrets.token_urlsafe(24)` printed to the proxy stdout; require the admin to paste it once into a `localStorage["hhf_proxy_token"]` field in the unlock UI. The PIN stays as a UI affordance; the proxy secret leaves client code.

- **[HIGH] Wikibase metadata has no offsite backup.** Item-level claims, descriptions, dates, attributions, and locations live only in `hunterhouse.wikibase.cloud`. R2 holds the images; git holds code + curations. If the Wikibase Cloud instance is deleted, corrupted, or sunsets, the catalogue is unrecoverable as data. (CLAUDE.md "Pending" already flags this as deferred.)
  - **Fix (~half day):** write `scripts/backup_metadata.py` — one-time dump of every item under each collection prefix as JSON sidecars at `{collection}/metadata/{ARCH_ID}.json` in R2. Then patch the three ingest scripts (`ingest_item.py`, `ingest_publication.py`, `batch_ingest_egc.py`) to also write the sidecar on each ingest. Idempotent on re-run.

- **[MEDIUM] `ALLOWED_ORIGINS` uses `startswith`.** `scripts/edit_proxy.py:88`. `origin.startswith(o)` matches `https://bturep.github.io.attacker.com` against the `https://bturep.github.io` allowlist entry. Not currently exploitable (the proxy then sets ACAO to the allowlisted value, not the requesting origin, so the browser rejects the response), but it bites the moment the header is refactored to echo `origin` back. Replace with exact equality. Folds into the CRITICAL fix above.

### 11.2 Soon (operational hygiene; do this month)

- **[MEDIUM] No pre-push validation.** A JS syntax error or malformed `VERSION` constant in `browse.html` takes the live archive offline with nothing between keyboard and `bturep.github.io`. Add `.github/workflows/validate.yml` (or a local `.git/hooks/pre-push`) that, on every push: (a) `node --check` on each `<script>` block extracted from `browse.html` + `next.html`; (b) confirms the `VERSION` constant matches `v1.XX.NN` (live) / `v1.XX-test.NN` (staging); (c) parses `manifest.json` and `manifest.next.json`. Don't gate the push — email-alert on failure. ~1 hour.

- **[LOW] Python scripts share ~130 lines of Wikibase boilerplate.** `ingest_item.py`, `ingest_publication.py`, `batch_ingest_egc.py`, `patch_dates.py`, `renumber_caa.py` each re-implement `.env` loading + login + CSRF token handling + claim builders. Extract `scripts/_wikibase.py` with a `WikibaseSession` class. The existing code is correct; this is pure deduplication. ~30 minutes; payback on the next ingest.

- **[LOW] PIDs are scattered as string literals** in three places: the SPARQL query in `loadFromWikibase`, the `EDITABLE` map (`next.html:4432`), and inline `setStringClaim` / `setClaim` calls. No central dictionary. Renumbering a property is a three-place grep-and-replace and easy to miss one. Add a top-of-file `const PROPERTIES = {DATE: "P82", PHASE: "P62", …}` and migrate references opportunistically (not all at once). ~30 minutes initial, plus per-property migration.

- **[LOW] Researcher notes stored as plaintext in `localStorage`.** `next.html` ~`hhf_rn` localStorage key. The lock-icon UI implies privacy that isn't backed by encryption. Either soften the UI claim ("local notes; not encrypted") or derive a key from the pin + site salt and encrypt at rest. Low immediate impact; flagged for honesty.

- **[LOW] Rotate `.env` credentials + verify `.gitignore`.** Audit hygiene: confirm `.env` is in `.gitignore` (it lives outside the repo today at `~/Documents/hh-wikibase-migration/.env`, so this is belt-and-braces); rotate `WIKIBASE_BOT_PASSWORD` and R2 keys on any suspicion of exposure. ~15 minutes.

### 11.3 Bend before break (watch; refactor when triggered)

- **HTML monolith approaching the inflection point.** `next.html` 5,667 lines, `browse.html` 5,520. Each significant feature adds 150–300 lines. At 7–8 K lines, editor performance degrades, diffs become hostile to review, and merge conflicts get real. The lightest credible refactor is to fork `assets/verso.next.css` first (CLAUDE.md already documents this), then extract `curator.js` / `record.js` as `<script src=…>` modules. Plain GitHub Pages serves static files; no build step needed.

- **`renderMeta` / `renderMobSheet` duplication.** ~150 lines of near-identical row construction (the same `descRows` array, different HTML wrapping). Extract `function buildRows(item) → {descRows, archRows}`; both callers iterate. Pays off when adding an editable field (currently 15).

- **`state.curation` checks at ~26 sites.** Today this is fine — most are at function entry. A hypothetical second display mode ("exhibition mode") forces either 26 nested `if/else if` blocks or a refactor to a `state.mode` enum with mode-specific render branches. Don't refactor pre-emptively; do it *before* adding the second mode.

- **Image pipeline has no integrity check.** Ingest scripts upload to R2 via `rclone copy` then write the Wikibase P95/P96 URL. A silent `rclone` failure leaves a 404-pointing claim, with no canary. Add `scripts/verify_r2_links.py` that SPARQL-fetches every P95/P96 URL and HEADs it. Run before each session-end. Same script catches accidental R2 renames. ~1 hour.

- **No tests, not even smoke tests.** Given the complexity of three-pane shell + mobile sheet + zoom/pan + curator mode + admin editor, this is generous trust. Three Playwright smoke tests (~100 lines, dev-only, never deployed): load `next.html`, search "hunter", click an item, verify the title renders; toggle dark mode; mobile swipe. Worth doing the next time a refactor breaks something subtle.

### 11.4 Resolved on inspection (looked like issues; aren't)

- **Curator-name XSS path.** Reviewed `openCuratorPane` at `next.html:3795–3826`. `bioEscaped.split(name).join(nameSpan)` splits by the *escaped* name (`name = escapeHTML(rawName)` at line 3799), not the raw name. The byline and bio paths are correctly defended. **No action.**
- **Python scripts: no shell injection.** All `subprocess` calls use list args; no `shell=True`; no `os.system` with user input; no `eval`. `.env` loading is plain string parsing. **No action.**
- **PDF.js v5.7.284.** No known CVEs against this patch version as of audit. `viewer.mjs` HOSTED_VIEWER_ORIGINS patch is sensible and code-commented. On any future PDF.js upgrade, re-apply the patch and recheck the Mozilla CVE feed. **No action today.**
- **R2 CORS allows `http://localhost` + `http://127.0.0.1`.** Fine — public read-only assets, no write API exposed. **No action.**
- **GitHub Pages HTTPS.** Enforced by default. No `.env` / R2 keys / Wikibase password in git history (verified via `git log --all -p | grep -i 'PASS|TOKEN|SECRET'`). **No action.**

### 11.5 Resolved 2026-05-22 (post-audit, same day)

- **§11.1 CRITICAL steps 1 & 2 + §11.1 MEDIUM `startswith`.** `scripts/edit_proxy.py` hardened: `do_POST` now (a) validates `Origin` against an allowlist *before* reading the body and returns 403 on mismatch; (b) requires `Content-Type: application/json` (415 otherwise), which forces a CORS preflight and removes the text/plain "simple request" bypass; (c) `startswith` replaced with `urlparse`-based exact matching — production must be exactly `https://bturep.github.io`; localhost/127.0.0.1 still accepted on any port. 12-case unit test covers the original `bturep.github.io.attacker.com` attack, port-suffix attacks, subdomain attacks, the file:// `null` origin, and missing/garbage Origin. The browser side was already sending `application/json` (verified `proxyEdit` in both `browse.html:1843` and `next.html:1975`), so no client change required. **§11.1 CRITICAL step 3** (per-startup random secret) deliberately deferred — separate ~1–2 hr task touching the unlock UI.
- **§11.2 MEDIUM pre-push validation.** Added `.github/workflows/validate.yml` + `.github/scripts/validate.mjs`. On every push to `main` (and on PRs), the workflow checks: each inline `<script>` block in `browse.html` + `next.html` parses (`node --check`); the `VERSION` constants match `v\d+\.\d{2}\.\d{2}` (live) and `v\d+\.\d{2}-test\.\d{2}` (staging); `manifest.json` + `manifest.next.json` parse as JSON and carry `start_url`. Does **not** gate the push — GitHub emails the repo owner on a failed run, matching the audit's "alert, don't block" model. Verified on the current tree (pass) and with deliberate breakage (caught both a malformed `VERSION` and a `function broken( {` syntax error).
- **§11.2 LOW `.env` / `.gitignore` hygiene.** Added `.env`, `.env.*` (with a `!.env.example` allowance) and `data/snapshots/wikibase_full_*/` to `.gitignore`. The actual credential file lives outside the repo at `~/Documents/hh-wikibase-migration/.env` — these entries are belt-and-braces in case a copy is ever placed in the repo root. History audit (`git log --all -p | grep -iE '(WIKIBASE_BOT_PASSWORD|R2_SECRET|R2_ACCESS|EDIT_PROXY_SECRET).*=.{8,}'`) returns zero hits; the only matches are `<in .env>` placeholders inside markdown.
- **§11.2 LOW Python boilerplate dedup.** New `scripts/_wikibase.py` providing `load_env()` and a `WikibaseSession` class (login, CSRF, `.post(action, **params)` with auto-retry on stale token, `.get()` for read endpoints). Migrated the two smallest write-scripts (`patch_dates.py`, `mint_property.py`) as proof; the bigger scripts (`ingest_item.py`, `ingest_publication.py`, `batch_ingest_egc.py`) are left untouched on the principle of "don't disturb working code without reason — payback is on the next ingest." Smoke-tested: helper imports cleanly, both migrated scripts compile, `mint_property.py --help` still works.
- **§11.1 HIGH (partial)** — local-only Wikibase metadata backup. New `scripts/backup_metadata.py` (read-only; no credentials needed) dumps every catalogue item + every referenced vocab / person / institution + every property in use, as raw `wbgetentities` JSON, into `data/snapshots/wikibase_full_YYYYMMDD/`. First run on 2026-05-22: **180 catalogue items** (HHC 115 · CAA 35 · EGC 30) + 123 referenced + 29 properties = **332 entities · 3.0 MB**. Snapshot directory is gitignored — commit selectively if you want a snapshot pinned to history.
- **§11.1 HIGH (R2 mirror — part 2a).** New `scripts/sync_metadata_to_r2.py` uploads the local snapshot to R2, layered alongside the image bytes. Layout: `{collection-folder}/metadata/{ARCH_ID}.json` for catalogue items (matches the existing `intake/` sibling pattern), `_wikibase/items/{Qnnn}.json` for referenced items, `_wikibase/properties/{Pnn}.json` for properties, `_wikibase/_manifest.json` for the snapshot manifest. Dry-run default; `--execute` writes; `--checksum` for paranoid mode. Idempotent (rclone size+mtime, or hash with `--checksum`). First run on 2026-05-22 pushed all 333 sidecars in 6 rclone jobs, all reachable via the public CDN at `https://archive.hunterhousefoundation.com/`. Per-ingest sidecar writes (the remaining piece of §11.1 HIGH) are still pending.
- **§11.3 image pipeline integrity check.** New `scripts/verify_r2_links.py` (read-only, no credentials needed) SPARQL-fetches every URL claim (`P95`, `P96`, `P143`) and HEAD-requests each against R2. First run found **6 dead `P95` master-image URLs** — silent legacy from the 2026-05-14 HH-A → HH-HHC rename migration: the R2 files were renamed, but the `P95` claims on items `HH-HHC-0036`–`0040` and `HH-HHC-0066` still point at the old `HH-A-NNNN_*.tif` filenames. The masters exist on R2 under their correct new names; only the Wikibase claims need to be rewritten. **Fixed same-day** by `scripts/archived/fix_p95_legacy_urls_20260522.py` (dry-run-first; pre-flight HEAD-check on every proposed new URL refused to write unless reachable; one accidental duplicate on Q425 from SPARQL planning lag cleaned up manually). Post-fix verifier: **354 / 354 URLs at 200**. Suggested cadence: run `verify_r2_links.py` before each session-end. JSON reports written under `data/snapshots/r2_verify_*.json` (gitignored).
- **§11.2 LOW researcher-notes label honesty.** Lock-icon tooltips updated in `next.html` to drop the implicit privacy claim. "Unlock to add notes" → "Sign in to add a note (stored locally on this device, not encrypted)". "Lock" → "Sign out (notes stay on this device)". `localStorage` storage shape unchanged; just the surface honesty.
- **§11.2 LOW PIDs central dictionary (opportunistic migration).** New `PROPERTIES` constant near the top of `next.html` declares all 27 PIDs the application uses, with category groupings and inline comments. Migrated: the `EDITABLE` map (16 entries — every inline-editable property), the `ACCESS_COPY` + `DISPLAY_ROTATION` call sites, and the two SPARQL `OPTIONAL` lines for those two. Deliberately **not** migrated: the rest of the catalogue SPARQL body (~25 `wdt:Pxx` literals inside a template string). The audit explicitly recommended opportunistic migration over a big-bang rewrite; the new constant is the central registry; future SPARQL touches can substitute in `${PROPERTIES.X}` as they're already string-templated. The two prior single-PID constants (`ACCESS_PID`, `ROTATE_PID`) removed in favour of `PROPERTIES.ACCESS_COPY` and `PROPERTIES.DISPLAY_ROTATION`. `next.html` bumped to `v1.07-test.52`.
- **§11.1 CRITICAL step 3 — per-startup random secret.** Final piece of the CSRF row. `scripts/edit_proxy.py` now generates `secrets.token_urlsafe(24)` at startup (32-char URL-safe random) and prints it inside a small banner on stdout. The prior `"203BTP"` fallback (the admin PIN, also visible in client code as `RPINS["203BTP"]`) is gone; `EDIT_PROXY_SECRET` in `.env` still overrides for power-user / testing flows but loses the rotation benefit. `/ping` now accepts an optional `?secret=…` query and returns `{ok, user, authenticated}` so the browser can validate a pasted token without a real write; comparison uses `secrets.compare_digest()` (constant-time, no length-leak). `next.html` (v1.07-test.53) stores the token in `localStorage["hhf_proxy_token"]`, sends it as the `secret` field on `/edit`, and renders an inline paste form inside the existing `#hh-proxy-badge` when the proxy is online but unauthenticated. On HTTP 403 "bad secret" the token is cleared and the paste form re-appears (this is what an admin sees the first time after a proxy restart — paste the new token, save, edits resume). End-to-end smoke-tested: all four defences (Origin, Content-Type, exact-match origin, per-startup secret) layer correctly. **Caveat:** `browse.html` (LIVE) still uses the old "send the PIN as secret" pattern — but admin editing on live was never the intended workflow per the LINE: NEXT rule, so the mismatch is benign until the next promotion (which brings the new flow with it). **§11.1 CRITICAL row is now fully closed.**
