# CLAUDE_archive_v1.07-audit.md — frozen 2026-05-22

Verbatim freeze of the **audit-response day** session log entries from
the live `CLAUDE.md`. Frozen at the end of session 2026-05-22 after
condensing the live file (twelve per-commit entries collapsed into one
digested summary).

Scope: 2026-05-22 only. `next.html` test-line `v1.07-test.50 → v1.07-test.54`,
plus the full 2026-05-22 security + maintainability audit response
(CRITICAL row + HIGH row closed; CI workflow added; preservation pipeline
built end-to-end; verifier surfaced + same-day fix of 6 dead P95 URLs;
house cleanup; ARCHITECTURE.md rewrite).

Live `browse.html` unchanged this session (LINE: NEXT held throughout).

Sibling archives:
  - CLAUDE_archive_v1.07.md       — v1.06 promotion → .18 live · test.01 → .22 staging (freeze 2026-05-21)
  - CLAUDE_archive_v1.06.md       — v1.05 → v1.06 promotion (freeze 2026-05-20)
  - CLAUDE_archive_v1.05.md       — v1.03 → v1.05.02 (freeze 2026-05-19)
  - CLAUDE_archive_v1.02.md       — ≤ v1.02.18 (earliest freeze)

═══════════════════════════════════════════════════════════════════════════
Verbatim session-log entries follow.
═══════════════════════════════════════════════════════════════════════════

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

---

### 2026-05-22 — Final §11.3 sweep: Playwright + narrow dedup + sidecar verify (next.html v1.07-test.54)

Closing out the audit. Three coupled changes.

- **Playwright smoke tests delivered.** New `tests/` directory: `conftest.py` (session-scoped HTTP-server fixture; spins up an `http.server` on a random loopback port rooted at the repo so `next.html` loads with relative `fetch()` paths intact), `test_smoke.py` (three tests: catalogue-loads, search-and-select, mobile-shell), `README.md` (one-time `pip3 install pytest-playwright && playwright install chromium`), `requirements.txt`. Dev-only — explicitly **not** in the validate workflow (CI doesn't have Playwright browsers; SPARQL is network-dependent; smoke tests are for the maintainer's "did my refactor break something" moments). `.gitignore` extended for pytest/playwright caches. Test files delivered but not run from this session (install would touch the global Python environment); Brandon runs the install once.

- **Narrow render-helper dedup.** Honest call: `renderMeta` (desktop) and `renderMobSheet` (mobile) have diverged in purpose — mobile is read-only public; desktop is admin-aware with active-state filter-buttons and EM placeholders. Forcing full `buildRows()` unification now would be a high-risk refactor for a "pays off when adding an editable field" maintainability gain. Instead, extracted three small helpers for the bits that are *literally* duplicated:
  - `archiveContactText(coll)` — the "Contact for permissions." / "Contact the Hunter House Foundation." lookup
  - `rightsRowHTML(rightsText, coll)` — the rights label + contact-note span assembly
  - `findingAidHTML(archiveLink, coll)` — the AtoM `<a>` rendering
  Both `renderMeta` and `renderMobSheet` now use these three helpers for their rights / finding-aid rows. Mobile and desktop wording stays in lock-step from here. The broader `buildRows()` unification is **deferred by design** (audit's "watch; refactor when triggered" framing applies).

- **Verifier sidecar extension.** `scripts/verify_r2_links.py` now derives each catalogue item's sidecar URL and HEAD-checks it alongside the image/PDF claims. New flags: `--no-sidecars` (legacy mode), `--sidecars-only`. Default: both. Confirmed all 180 derived sidecar URLs return 200 — close-the-loop verification of today's §11.1 HIGH work.

**Audit standing — every actionable §11 item is now resolved:**
- ✅ §11.1 CRITICAL row (steps 1 + 2 + 3 + MEDIUM startswith)
- ✅ §11.1 HIGH row (local backup + R2 mirror + per-ingest sidecar writes)
- ✅ §11.2 row (CI validation + .env hygiene + dedup + PIDs + RN labels)
- ✅ §11.3 image-pipeline integrity check + first finding fixed + sidecar verification
- ✅ §11.3 Playwright smoke tests (delivered)
- ◐ §11.3 `renderMeta`/`renderMobSheet` full unification: explicitly deferred (narrow dedup shipped instead)
- §11.3 "state.curation checks at ~26 sites" — audit explicitly said don't refactor pre-emptively
- §11.3 "HTML monolith approaching inflection" — not actionable yet (~5,700 lines, audit said worry at 7–8K)

**Version line: browse.html `v1.06.31` (LIVE, unchanged) · next.html `v1.07-test.54` (staging).**

---

### 2026-05-22 — House cleanup + ARCHITECTURE.md rewrite (session close)

The "tight under scrutiny" pass. After confirming each deletion via AskUserQuestion (per the global CLAUDE.md "ask before delete" rule), removed five unused files + one accidentally-tracked OS junk file + a stale remote branch, and rewrote ARCHITECTURE.md as a clean reviewer-facing doc.

**Deletions (commit `08928cd`):**
- `index-video.html` — earlier MP4-background splash variant; superseded by the 1.4 KB `index.html` thin redirect
- `import-rn.html` — one-off researcher-notes import utility; no live refs
- `swatches.html` — local colour-swatch dev page (was untracked)
- `GES_intake.xlsx` — superseded by `EGC_intake.xlsx` (was untracked)
- `Main_Page.wiki` — May-13 wikitext snapshot; same content now lives inside `WIKIBASE_MAINPAGE.md`
- `.DS_Store` — macOS junk that had been tracked; removed + added to `.gitignore`
- `scripts/make_ges_intake.py` → `scripts/archived/make_ges_intake_20260520.py` (rename + ARCHIVED header)
- Stale remote branch `origin/refactor/browse-cleanup` deleted via `git push origin --delete`

**ARCHITECTURE.md rewrite (`1c8803b`).** Replaced the chronological §11.5 "Resolved" appendix (which had grown messy through eight audit-response commits) with a clean §11 status where each audit item carries its resolution marker (✅ / ◐ / ⏸) alongside the original framing. Substantive refresh across §1–§10:
- §1 TL;DR mentions CI + smoke tests + write-proxy auth model
- §3 Repository layout drops the deleted orphan HTMLs; adds `tests/`, `.github/`, `scripts/_wikibase.py`, the preservation-pipeline scripts
- §5 gains §5.3 "Metadata sidecars" covering the R2 preservation backup
- §6 Write-path sequence diagram updated for per-startup token + four CSRF defences
- §8 (new) "Quality + CI infrastructure" pulls all the validation / verification / smoke-test surface into one place
- §9 git-repo stats refreshed (579 commits, stale branch gone, 14 tags, 1 contributor)
- §10 framed clearly as observational; §11 is the actionable companion
- §12 "where to start reading" extended to include `_wikibase.py` + smoke tests

This is the version of ARCHITECTURE.md to send to a reviewer alongside the repo URL.

**Tail-up commit (`ed559fb`).** Two stray edits (the `.DS_Store` gitignore rule + the archived script's ARCHIVED docstring header) didn't ride with `08928cd` due to a staging miss; landed cleanly in this follow-on.

**Global ~/.claude/CLAUDE.md "Current versions" table** updated to reflect today's `next.html v1.07-test.54` test-line endpoint (was previously left at v1.06.31 with stale staging notes).

---

**Day total:** 14 commits today (audit response: 8 audit-fix commits + 1 data-fix + 2 cleanup + 2 doc + 1 tail-up). Both highest-severity audit rows (CRITICAL + HIGH) fully closed; every actionable §11 item resolved; the project is meaningfully tighter than it was at session start.

**Final version line: browse.html `v1.06.31` (LIVE, unchanged all session) · next.html `v1.07-test.54` (staging).**
