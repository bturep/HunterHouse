# Scripts catalogue

Every script and piece of tooling in this repo, grouped by status. Written 2026-11-08. The prose description of each script, and how they fit together, is in `ARCHITECTURE.md` §3 ("`scripts/` -- Python tooling") and §8 ("Quality + CI infrastructure"); this file is the index by status. Scripts run from the maintainer's machine against Wikibase and R2; credentials are read from outside the repo (see `ARCHITECTURE.md` §3). Nothing in `scripts/` is shipped to the browser.

The site's own browser code (`sw.js`, `events-data.js`, `forms/*.js`, `assets/`) is not tooling and is not listed here; see `ARCHITECTURE.md` §3-4.

## 1. Live, scheduled

| # | Script | What it does | Run by | Writes to |
|---|---|---|---|---|
| 1 | `.github/scripts/validate.mjs` | Pre-push validation: inline `<script>` syntax, `VERSION` pattern and bump check, manifest JSON, promotion invariants | GitHub Actions `validate.yml`, on every push to `main` and on PRs (also by hand: `node .github/scripts/validate.mjs`) | Nothing; fails the run and emails the owner |
| 2 | `scripts/verify_r2_links.py` | HEAD-checks every image/PDF URL claim and every derived metadata sidecar URL against R2. Read-only | GitHub Actions `health.yml`, Mondays 7:00 am UTC; also by hand before session-end | The run log; by hand, `data/snapshots/r2_verify_*.json` (local, gitignored) |
| 3 | `scripts/rollup_analytics.py` | Snapshots one calendar month of Analytics Engine aggregates and rebuilds the monthly summary | GitHub Actions `rollup-analytics.yml`, 6:00 am UTC on the 1st of each month, or `workflow_dispatch` | `data/analytics/<YYYY-MM>.json`, `data/analytics/monthly-summary.csv` |

## 2. Live, by hand

| # | Script | What it does | Run by | Writes to |
|---|---|---|---|---|
| 1 | `scripts/build_catalogue_snapshot.py` | Builds the static catalogue snapshot the browser falls back to when SPARQL is down; reads `CATALOGUE_QUERY` from the page so it cannot drift. Dry-run default | Maintainer, `--execute` at session-end whenever catalogue data changed (manual by design: no R2 keys in CI) | R2 `/catalogue/` (`catalogue.json`, `catalogue.csv`) |
| 2 | `scripts/build_item_pages.py` | Generates the static permalink pages and `sitemap.xml`. Idempotent; `--one <ID>` for one page | Maintainer after any catalogue change; also called best-effort by the ingest scripts | `archive/<ID>.html`, `sitemap.xml` |
| 3 | `scripts/ingest_item.py` | Single-image item ingest: master TIF to R2, three JPEG tiers, Wikibase item create or overwrite. Dry-run default, `--execute` | Maintainer | R2, Wikibase, then sidecar + permalink page |
| 4 | `scripts/ingest_publication.py` | Multi-page publication ingest: byte-for-byte masters, PDF, SHA-256 manifest, cover tiers | Maintainer | R2, Wikibase |
| 5 | `scripts/batch_ingest_egc.py` | Workbook-driven batch ingest; used once for the EGC drawings and kept as the template for future collection batches | Maintainer | R2, Wikibase |
| 6 | `scripts/mint_property.py` | Mints (or finds, idempotent) one Wikibase property | Maintainer | Wikibase |
| 7 | `scripts/gen_public_page_tiers.py` | Per-page JPEG tiers for public multi-page objects (the `PUBLIC_PAGES` companion) | Maintainer, when a multi-page public item is added | R2 tiers |
| 8 | `scripts/backup_metadata.py` | Read-only dump of every catalogue item, referenced vocab/people and properties | Maintainer; also the restore point before any bulk Wikibase change | `data/snapshots/wikibase_full_YYYYMMDD/` (local, gitignored) |
| 9 | `scripts/sync_metadata_to_r2.py` | Pushes a local metadata snapshot to R2 | Maintainer, after #8 | R2 `{collection}/metadata/`, `_wikibase/` |
| 10 | `scripts/cf_purge.py` | Evicts stuck objects from the Cloudflare edge cache by URL (archive zone only) | Maintainer, after an R2 overwrite or delete | Cloudflare cache |
| 11 | `scripts/backup_r2.sh` | Mirrors the R2 archive bucket to a local disk | Maintainer | The local disk named on the command line |
| 12 | `scripts/build_doomsday.py` | Builds or refreshes the offline doomsday copy of the whole archive on an external drive (steps mirror/site/repo/wikibase/gated/tools/fixity/index); see `ARCHITECTURE.md` §5.6 | Maintainer, after any website change or ingest | The drive named on the command line |
| 13 | `scripts/doomsday/serve.py`, `scripts/doomsday/verify.py`, `START.bat`, `start.command`, `VERIFY.bat`, `verify.command`, `README-FIRST.txt` | The files `build_doomsday.py` places on the drive: an offline server standing in for R2, the Worker and SPARQL; a fixity check; launchers; a readme | Whoever opens the drive | Nothing (`verify.py` is read-only) |
| 14 | `scripts/edit_proxy.py` | Local admin write proxy on `127.0.0.1:8731` for inline editing. Inert until the admin entry is rebuilt | Maintainer, each session it is needed | Wikibase |
| 15 | `scripts/regen_previews.py` | Regenerates `_prev.jpg` tiers from the master TIFs (`--dry-run`, `--collection`) | Maintainer | R2 previews |
| 16 | `scripts/serve-nocache.py` | Static server with no-cache headers for iterating on mocks | Maintainer, `py -3 scripts/serve-nocache.py` | Nothing |
| 17 | `cloudflare/r2-browser/src/worker.js`, `cloudflare/r2-browser/src/gated-letters.js` | The Cloudflare Worker: read-only R2 folder listing, download and analytics events, and the token-checked gated endpoints | Deployed by hand with wrangler (`cloudflare/r2-browser/wrangler.toml`) | Analytics Engine |
| 18 | `cloudflare/r2-browser/analytics.sh` | Common read-only reports against the Analytics Engine dataset | Maintainer | Nothing |

## 3. Library

| # | Script | What it does | Imported by | Writes to |
|---|---|---|---|---|
| 1 | `scripts/_wikibase.py` | `load_env()` + `WikibaseSession` (login, CSRF, retry on a stale token) | Any script that writes to Wikibase (`patch_dates.py`, `mint_property.py`, newer scripts) | Nothing itself |
| 2 | `scripts/sync_one_metadata.py` | Writes one item's metadata sidecar to R2; also has a CLI | The ingest scripts, fail-safe after each create | R2 `{collection}/metadata/` |

## 4. One-off, done

Kept as the record of what was run. Each is marked **one-off, done?** for the maintainer to confirm before any move to `scripts/archived/`; none was moved in this pass, because Pages serves every tracked file and a move changes its URL.

| # | Script | What it did | Run by | Wrote to |
|---|---|---|---|---|
| 1 | `scripts/patch_dates.py` | Added P82 dates and descriptions to 18 undated items. Still the named model for bulk Python writes | Maintainer, once | Wikibase |
| 2 | `scripts/clean_titles.py` | Cleaned bracketed annotations from item labels in one pass | Maintainer, once | Wikibase |
| 3 | `scripts/strip_counter_brackets.py` | Stripped `[N/N]` counters from item labels | Maintainer, once | Wikibase |
| 4 | `scripts/recolor_previews.py` | Converted R2 JPEG tiers from the scanner ICC profile to sRGB (the Chrome cyan-cast fix) | Maintainer, once | R2 tiers |
| 5 | `scripts/batch_ingest_frh_keep.py` | Ingested the 2026-07-19 Keep/ batch (six public items) | Maintainer, once | R2, Wikibase |
| 6 | `scripts/hosting_policy_2026.py` | Brought the Wikibase into line with the Wikibase Cloud hosting policy (2026-09-30). Idempotent | Maintainer, once | Wikibase |

## 5. Retired

This repo's retired scripts live in `scripts/archived/` (the folder predates the estate's `_retired/` name and is kept, since moving it would change public URLs). Completed one-shot migrations, kept for reference; none is called by anything.

| # | Script | What it did |
|---|---|---|
| 1 | `batch_ingest_egc_photos_20260630.py` | EGC photograph batch ingest |
| 2 | `batch_ingest_frh_photos_20260719.py` | FRH 41-photograph batch ingest |
| 3 | `batch_ingest_ihc_20260525.py` | IHC 45-photograph batch ingest |
| 4 | `build_labs_20260714.py` | Generated the UI-lab variants from `next.html` |
| 5 | `cleanup_caa_descriptions.py` | CAA description cleanup (P91, P100) |
| 6 | `egc_cachebust_reupload_20260630.py` | EGC re-upload under new filenames after a stale CDN cache |
| 7 | `egc_reupload_affected_20260630.py` | Repaired three EGC images overwritten during the renumber |
| 8 | `fill_p142_missing.py` | Wrote P142 for 15 CAA items that had none |
| 9 | `fix_caa_scheme_split_20260630.py` | Tidied phase, title and P86 after the CAA 0020/0022 swap and Scheme I/II split |
| 10 | `fix_p142_prose.py` | Removed prose mixed into P142 archival paths |
| 11 | `fix_p95_legacy_urls_20260522.py` | Rewrote six dead P95 URLs from an earlier rename |
| 12 | `ingest_frh_public_20260702.py` | First FRH public-object ingest |
| 13 | `ingest_frh_sketchbooks_20260715.py` | FRH sketchbook ingest |
| 14 | `make_ges_intake_20260520.py` | Generated the old GES intake workbook; superseded by `batch_ingest_egc.py` |
| 15 | `migrate_p142_location.py` | Moved CAA archival paths from P100 into P142 |
| 16 | `r2_cleanup.sh` | Deleted stale R2 files after the ID renames |
| 17 | `regen_icons_20260719.py` | Regenerated the PWA icons |
| 18 | `remove_caa_use_q70_20260630.py` | Removed the misapplied P89 = Q70 claim from CAA drawings |
| 19 | `rename_ids.py` | The HH-A to HH-HHC / HH-CAA ID rename |
| 20 | `rename_ivh_to_ihc_20260525.py` | IVH to IHC rename |
| 21 | `renumber_caa_20260521.py` | CAA renumber, drawings first |
| 22 | `renumber_caa_25_32_20260520.py` | CAA renumber: rotation of 0025 to 0028 and swap of 0029 and 0032 |
| 23 | `renumber_egc_photos_20260630.py` | EGC photograph renumber |
| 24 | `renumber_frh_generic_20260719.py` | FRH renumber to the generic series |
| 25 | `renumber_hhc.py` | HHC renumber |
| 26 | `renumber_hhc_r2.sh` | R2 side of the HHC renumber |
| 27 | `revert_hhc_renumber.py` | Revert script for the HHC renumber |
| 28 | `revert_ids.py` | Revert script for the ID rename |
| 29 | `rotate_images_20260611.py` | Rotated archive images in place on R2; retired because it re-encoded masters (P144 display rotation replaced it) |
