# Hunter House Foundation Archive — operational handoff

> **Status: DRAFT, in development.** Captures operational continuity as of 2026-05-24. The archive itself is still being built — see `ARCHITECTURE.md` (system architecture) and `CLAUDE.md` (session log) for the development state.
>
> Sections marked **[TO COMPLETE]** require maintainer-only knowledge (recovery emails, account-specific URLs, billing contacts, secondary admins). Everything else is reconstructable from the public artifacts and this document.

---

## 1. What this document is

A **continuity-of-operations** record for the Hunter House Foundation Archive — the credentials, vendor accounts, recovery paths, and operational procedures a successor maintainer would need to keep the system alive. Deliberately separate from `ARCHITECTURE.md`, which describes *what the system is* but assumes the maintainer's silent operational knowledge.

Written for, in order:
1. **A successor maintainer** if Brandon Poole becomes unavailable.
2. **The foundation** if it decides to transfer operations.
3. **Brandon himself**, as the canonical written record of credentials + recovery paths he otherwise carries silently.

**Companion docs in this repo:**
- `ARCHITECTURE.md` — what the system is and how it works.
- `CLAUDE.md` — day-to-day working memory + session log.
- `WIKIBASE.md` — data contract (properties + Q-numbers).
- `README.md` — short project overview.

---

## 2. The system, at one glance

A static GitHub Pages site that reads its data from a Wikibase Cloud instance at runtime, with images on Cloudflare R2.

| Component | Where it lives | Owner |
|---|---|---|
| Code | `github.com/bturep/HunterHouse` (public) | bturep (GitHub) |
| Catalogue data | `hunterhouse.wikibase.cloud` (Wikibase Cloud) | [TO COMPLETE — Wikibase Cloud account] |
| Image / PDF / sidecar storage | `archive.hunterhousefoundation.com` (Cloudflare R2 bucket `hunter-house-archive`) | [TO COMPLETE — Cloudflare account] |
| Domain | `hunterhousefoundation.com` | [TO COMPLETE — registrar account] |
| Bot identity | `MyBot@my-bot` on Wikibase | tied to the Wikibase Cloud account above |

Operational glue: a `.env` file on Brandon's laptop holds the bot password + R2 API keys. Nothing in `.env` is itself unique data — every credential it carries can be regenerated from the respective vendor account. See §4.

---

## 3. Vendor accounts + access

### 3.1 GitHub
- **Username:** `bturep`
- **Primary email on account:** [TO COMPLETE]
- **2FA method + backup codes location:** [TO COMPLETE]
- **Repositories owned:**
  - `bturep/HunterHouse` (this one)
  - [TO COMPLETE — any others worth knowing]
- **GitHub Pages settings:** Settings → Pages, source = `main` branch / root. Custom domain: none (served at `bturep.github.io/HunterHouse/`).
- **Other admins / collaborators:** [TO COMPLETE — none currently?]
- **SSH key in use:** `~/.ssh/id_ed25519_github` on Brandon's machine. Rotation: generate a new key, add the public half at GitHub → Settings → SSH and GPG keys, remove the old one.

### 3.2 Cloudflare (R2 + DNS)
- **Login email:** [TO COMPLETE]
- **2FA method + backup codes:** [TO COMPLETE]
- **R2 bucket:** `hunter-house-archive`
  - **Public custom-domain endpoint:** `archive.hunterhousefoundation.com`
  - **CORS:** configured to allow `https://bturep.github.io`, `http://localhost`, `http://127.0.0.1` for GET/HEAD; exposes `Content-Length` / `Content-Type` / `Content-Disposition`; `max-age` 86400.
  - **Approximate size:** [TO COMPLETE — last measured]; growing as ingest proceeds.
- **DNS:** zone for `hunterhousefoundation.com` managed in this same Cloudflare account.
  - **Records of interest:**
    - `archive.hunterhousefoundation.com` → R2 bucket (Cloudflare-managed)
    - [TO COMPLETE — any root / apex / www records, MX, etc.]
- **API tokens currently in use:**
  - Object-scope token used by `rclone` for bucket reads/writes (lives in `.env`).
  - Admin-scope token used **only ad hoc** for bucket-config changes (CORS, lifecycle, etc.); not stored in `.env`.
- **Other admins:** [TO COMPLETE]

### 3.3 Wikibase Cloud
- **Instance URL:** `https://hunterhouse.wikibase.cloud`
- **Owner Wikibase Cloud login:** [TO COMPLETE]
- **2FA method:** [TO COMPLETE]
- **Bot identity:** `MyBot` user, app-password label `my-bot`. Full username in `.env` is `MyBot@my-bot`.
- **Support channel:** Wikibase Cloud support has the power to do instance reset, restore from backup, transfer ownership. Contact via the Wikibase Cloud help portal. [TO COMPLETE — direct support email if known]
- **Other admins / editors:** [TO COMPLETE]

### 3.4 Domain registrar
- **Domain:** `hunterhousefoundation.com`
- **Registrar:** [TO COMPLETE — e.g. Cloudflare Registrar, Namecheap, etc.]
- **Login:** [TO COMPLETE]
- **2FA:** [TO COMPLETE]
- **Renewal date:** [TO COMPLETE — set a calendar reminder a month before]
- **DNS hosted at:** Cloudflare (see §3.2).

### 3.5 The foundation itself
- **Legal entity:** [TO COMPLETE — registered name, jurisdiction, status]
- **Board / directors:** [TO COMPLETE]
- **Who can authorise a transfer of these accounts:** [TO COMPLETE]
- **Lawyer / accountant on file:** [TO COMPLETE]

### 3.6 Local development machine
- **Hostname:** Brandon's MacBook (specifics in his head).
- **Required tooling:** `python3` ≥ 3.9, `rclone`, `git`, `node` ≥ 20, `gh` CLI, `pip3 install requests` (for the Wikibase scripts).
- **Optional:** `playwright` + `pytest-playwright` for the smoke tests (`pip3 install pytest-playwright && playwright install chromium`).

---

## 4. Credentials

### 4.1 Where they live

`~/Documents/hh-wikibase-migration/.env` on Brandon's machine. **NOT** in the repo, **NOT** in git history (verified clean — see `ARCHITECTURE.md` §10).

Expected contents (verify against the live file):

```
WIKIBASE_BOT_USER=MyBot@my-bot
WIKIBASE_BOT_PASSWORD=…
R2_ACCESS_KEY_ID=…
R2_SECRET_ACCESS_KEY=…
R2_PUBLIC_BASE=https://archive.hunterhousefoundation.com
EDIT_PROXY_SECRET=               # optional; empty/absent ⇒ per-startup token
```

A reference `.env.example` may live next to the real one. [TO COMPLETE — confirm whether `.env.example` exists; if not, copy the field names above into one.]

### 4.2 Rotation procedures

**Wikibase bot password** (when compromised or as routine hygiene):
1. Log into Wikibase Cloud admin as the owner account (§3.3).
2. `Special:BotPasswords` → revoke the existing `my-bot` entry.
3. Recreate `my-bot` with the same grants (`highvolume`, `editpage`, `createeditmovepage`, `editmycssjs`, `editmywatchlist` — verify against current grants before destroying the old one).
4. Copy the new password.
5. Update `WIKIBASE_BOT_PASSWORD` in `.env`.
6. Restart any running `edit_proxy.py` (Ctrl-C and re-launch).

**R2 API token:**
1. Cloudflare dashboard → R2 → Manage R2 API tokens.
2. Note the existing object-scope token's permissions.
3. Create a new token with the same scope (Object Read & Write on `hunter-house-archive`).
4. Update `R2_ACCESS_KEY_ID` + `R2_SECRET_ACCESS_KEY` in `.env`.
5. Verify with `rclone ls hh-r2:hunter-house-archive | head`.
6. Once verified working, revoke the old token.

**Edit-proxy startup token:** rotates automatically on every restart of `scripts/edit_proxy.py` via `secrets.token_urlsafe(24)`. No action required. The admin pastes the printed token into `next.html`'s bottom-left badge after each restart.

### 4.3 If the `.env` is lost

Inconvenient, not catastrophic. Nothing in `.env` is the only copy of anything.

- **Bot password:** regenerate per §4.2.
- **R2 token:** regenerate per §4.2.
- **R2 bucket contents:** preserved on R2 itself; recreating `.env` does not touch the bucket.
- **Wikibase items:** preserved on the Wikibase Cloud instance.
- **`R2_PUBLIC_BASE`:** literal, can be retyped from this document.

---

## 5. Operational procedures

### 5.1 Per-session

```bash
# Start the local edit proxy (admin inline editing requires this).
python3 scripts/edit_proxy.py
# → copy the random token from the stdout banner into next.html's
#   bottom-left badge once. The proxy dies on Mac sleep — re-launch
#   afterwards (new token each time).

# Before session-end, a cheap integrity check.
python3 scripts/verify_r2_links.py
```

### 5.2 Push workflow

1. Make changes on `main` (typo / one-liner) or a feature branch (anything structural).
2. Bump the `VERSION` constant in any HTML file you touched. The CI guard will fail the push otherwise.
3. `node .github/scripts/validate.mjs` locally to confirm clean before pushing.
4. Commit, `git push`. GitHub Pages deploys in ~30 s. CI emails on failure.

### 5.3 Promoting `next.html` → `browse.html`

Documented in `CLAUDE.md` under "Staging / test page → Promotion (staging → live)". Summary:

```bash
cp next.html browse.html
# In browse.html, set VERSION to the real vMAJOR.SESSION.PATCH (live pattern).
# (If light.css was forked for this cycle) cp assets/verso.next.css assets/light.css
git tag vMAJOR.SESSION.00 && git push --tags
# Re-sync next.html from the new browse.html for the next cycle:
# bump VERSION to vMAJOR.(SESSION+1)-test.01.
```

### 5.4 Ingesting a new item

- **Single image:** `python3 scripts/ingest_item.py` — edit the config block at the top, dry-run first, then `--execute`.
- **Multi-page publication:** `python3 scripts/ingest_publication.py` — same shape.
- **Workbook-driven collection batch:** copy `scripts/batch_ingest_egc.py` as a template; edit the workbook path + constants; dry-run; `--execute`.

Each ingest auto-writes the new item's preservation sidecar to R2 via `sync_one_metadata.py`. No separate backup step is required.

### 5.5 Periodic full backup

```bash
python3 scripts/backup_metadata.py           # writes local snapshot
python3 scripts/sync_metadata_to_r2.py --execute   # rclone-pushes to R2
```

Run on demand. Recommended cadence: before each session-end, and always before a risky migration. Snapshots land at `data/snapshots/wikibase_full_YYYYMMDD/` locally (gitignored) and at `_wikibase/items/` + `_wikibase/properties/` + the per-collection `metadata/` paths on R2.

### 5.6 Wikidata interop

Three items are drafted in `WIKIDATA_DRAFT.md`: Richard Hunter (person), Canadian Architectural Archives (institution), Richard Hunter fonds. Pending submission via QuickStatements; blocked on Brandon's Wikimedia account hitting the autoconfirmed threshold (4 days + 50 edits on Wikidata). Once submitted, the resulting Q-numbers should be added as `P139` (Wikidata QID) on the corresponding items in our Wikibase: `Q201` (Hunter), `Q116` (CAA), and a new fonds item.

---

## 6. Disaster recovery

### 6.1 "My laptop died"

- **Code:** `git clone git@github.com:bturep/HunterHouse.git`.
- **Credentials:** regenerate per §4.2 — everything in `.env` is regenerable. The `.env` itself never lived anywhere else.
- **Local masters of TIFs not yet ingested:** [TO COMPLETE — location of master scans on Brandon's drive, and any backup of them]

### 6.2 "Wikibase Cloud is down or the instance is lost"

Short-term: the site renders the most recent `localStorage`-cached catalogue (stale-cache fallback in `loadFromWikibase()`; see `ARCHITECTURE.md` §4.5). New visitors see an empty list briefly until the splash overlay covers it.

Permanent loss: the R2 metadata sidecars (`{collection-folder}/metadata/{ARCH_ID}.json` + `_wikibase/items/Qnnn.json` + `_wikibase/properties/Pnn.json` + `_wikibase/_manifest.json`) are sufficient to reconstruct the entire archive via `wbeditentity`. This is the explicit purpose of the preservation pipeline (`ARCHITECTURE.md` §5.3).

Reconstruction sketch:
1. Stand up a new Wikibase instance (Wikibase Cloud or self-hosted).
2. Pull the R2 sidecars (`rclone copy hh-r2:hunter-house-archive/_wikibase/ ./recovery/`).
3. For each item JSON, post to the new instance via `wbeditentity new=item data=…`. Start with properties, then vocab items, then catalogue items (which reference the others).
4. Update the SPARQL endpoint URL in `browse.html` / `next.html`.

This procedure has not been rehearsed end-to-end. **[TO COMPLETE — schedule a dry-run rehearsal on a throwaway Wikibase instance to confirm the sidecars are sufficient.]**

### 6.3 "Cloudflare R2 is down or the bucket is lost"

Images + PDFs go dark on the site. Records still render (data is in Wikibase, separately).

Permanent loss: master TIFs live on Brandon's local machine at [TO COMPLETE — path]. Re-upload via `rclone copy` to a new R2 bucket, regenerate the 3 image tiers via `scripts/regen_previews.py`. The Wikibase items' `P95` / `P96` URLs would need updating if the bucket URL changes; mass-update via a one-off script modelled on `scripts/archived/fix_p95_legacy_urls_20260522.py`.

### 6.4 "Locked out of GitHub"

The site keeps serving the last-deployed `main` indefinitely (no push needed for continued reads). Push access recovery:
- If the bturep account is reachable via password reset → standard GitHub recovery.
- If the account is permanently lost → GitHub support, citing repo ownership documentation. Slow.
- **Mitigation:** add a second admin to `bturep/HunterHouse` who can keep pushing in the interim. [TO COMPLETE — decide whether to add a second admin and who.]

### 6.5 "Domain expired"

DNS resolves NXDOMAIN for `hunterhousefoundation.com` and `archive.hunterhousefoundation.com`. The site at `bturep.github.io/HunterHouse/` keeps serving its HTML, but every image URL breaks (they all resolve through the custom R2 domain).

Renew at the registrar (§3.4). Within 24 h of renewal the bucket endpoint is reachable again. **[TO COMPLETE — set a calendar reminder a month before each renewal date.]**

### 6.6 "Brandon is unreachable"

The system keeps running. The site is read-only for the public; nothing requires Brandon's intervention day-to-day. The following degrade if not addressed:
- Catalogue updates stop (no new ingests).
- Domain renewal lapses on the next cycle.
- R2 + Wikibase Cloud subscriptions continue auto-billing on whatever payment method is on file [TO COMPLETE — which].
- If billing fails → R2 bucket goes read-only or is reclaimed; Wikibase instance similarly.

A successor would proceed via §7.2.

---

## 7. Succession scenarios

### 7.1 Add a co-maintainer (Brandon stays involved)

1. **Repo:** add their GitHub account as a collaborator at `bturep/HunterHouse` → Settings → Collaborators. Push access is automatic.
2. **Cloudflare:** add to the Cloudflare account as a member with R2 read/write on `hunter-house-archive` (no need to give DNS or billing scope unless the role calls for it).
3. **Wikibase Cloud:** optionally add them as an editor on the instance via the wiki's user-rights page. They can write directly through the web UI; for bot-style writes, they'd run their own `edit_proxy.py` with their own `.env`.
4. **`.env`:** they generate their own on their own machine. Don't ship a shared one. Bot password can stay shared (per-process) or be rotated into per-maintainer bot accounts.

### 7.2 Transfer to a successor (Brandon stepping away)

1. **Repo:** transfer ownership at `github.com/bturep/HunterHouse` → Settings → "Transfer ownership" to the successor's GitHub account. Their GitHub Pages source stays `main`/root and the deployment continues at `successor.github.io/HunterHouse/`. If the URL needs to stay `bturep.github.io/HunterHouse/`, they'd need to keep posting under bturep — possible but unusual; cleaner to move.
2. **Cloudflare:** either (a) transfer the whole Cloudflare account ownership, or (b) move the R2 bucket + the `hunterhousefoundation.com` DNS zone into the successor's existing Cloudflare account. (b) requires recreating the R2 bucket on their side and `rclone copy`-ing the contents — slow but clean.
3. **Wikibase Cloud:** contact Wikibase Cloud support to transfer instance ownership.
4. **Domain:** transfer at the registrar (§3.4).
5. **`.env`:** regenerate on the successor's machine. Old `.env` should be destroyed.
6. **Update `ARCHITECTURE.md`, `README.md`, `HANDOFF.md`** to reflect the new owner identity and contact.

### 7.3 Mothball (read-only continuity)

1. Site stays live as-is on GitHub Pages. No push activity. No CI runs.
2. R2 + Wikibase Cloud subscriptions stay paid (auto-renew). Track the payment method.
3. No ingest happens. The R2 preservation sidecars are the long-term archival copy.
4. Annual lightweight check: verify domain renewal, verify Wikibase Cloud billing, run `scripts/verify_r2_links.py` to confirm nothing has drifted.

---

## 8. Deferred-by-design (don't undo without reading)

Decisions made deliberately, not by oversight. A successor seeing these might be tempted to "modernise" them — they're working as intended.

- **Single-file SPA** (no framework, no bundler, no build step). Easier to onboard + inspect than a modern stack; intentional. `ARCHITECTURE.md` §1, §4.1.
- **Inline scripts + styles** (with `'unsafe-inline'` in CSP). Cost of the single-file design; CSP still meaningfully restricts network exfiltration and remote script injection. `ARCHITECTURE.md` §10 Security.
- **Researcher notes are unencrypted `localStorage`.** Not a real ACL — a trusted-researcher honour-system arrangement. The UI labels don't imply encryption. `ARCHITECTURE.md` §10 Security.
- **Wikibase Cloud is public-read.** Anyone can SPARQL the archive; intentional for citability + Wikidata-ecosystem interop.
- **`RPINS` in cleartext HTML.** Gates UI affordances, not data. Writes require the local proxy + `.env`. Looks like a leak; isn't. `ARCHITECTURE.md` §10 Security.
- **Mobile is read-only.** No admin or researcher write UI at narrow widths. Deliberate constraint, not an oversight. `ARCHITECTURE.md` §10 Browser support.
- **`next.html` as a near-duplicate staging file.** Doubles the surface area during a development cycle, but avoids needing branch-preview infrastructure on plain GitHub Pages. `ARCHITECTURE.md` §10 Architecture.
- **PDF.js patched in-tree** (`assets/pdfjs/web/viewer.mjs`, `HOSTED_VIEWER_ORIGINS`). Patch must be re-applied on PDF.js upgrade. Intentional vs. running from a CDN.
- **No font / colour / contrast adjustments in the accessibility pass.** Functional a11y only (keyboard, ARIA, focus, motion preference). The visual design is treated as an architect-specified constraint. `ARCHITECTURE.md` §10 Accessibility.
- **No analytics.** No third-party JS of any kind. `ARCHITECTURE.md` §7.

---

## 9. State of play (snapshot — update periodically)

**As of 2026-05-24:**

- **Phase:** 3-month pilot, researchers only. The site is shared with a small group of trusted researchers, not the general public. Active work is on building out the archive and the curator-lens functionality. Feedback from pilot researchers informs subsequent iterations before a broader release.
- **Live:** `browse.html` `v1.06.38`. Stable; serves the catalogue at the v1.06 feature level (role system, admin inline editing, in-stage PDF reader, display rotation, splash overhaul).
- **Staging:** `next.html` `v1.07-test.81`. Substantially ahead of live; the next promotion lands compose mode, the researcher `?` help pane, marks-as-ordered-list with reorder UX + "marks first" sort, Markdown export/import with same-vs-other-researcher merge semantics, the admin "edit affordances off" toggle, the `Aa` text-size toggle, click-to-confirm in place of press-and-hold, a second researcher PIN (Olivia Jol), the full accessibility surface (focus rings, landmarks, ARIA labels, skip link, modal focus + trap, prefers-reduced-motion), and finished PROPERTIES interpolation in the catalogue SPARQL.
- **Catalogue size:** ~180 items across HHC + CAA + EGC. FRH + IVH not yet started.
- **Pending ingest:** EGC photographs (36, awaiting the Mary McNeill Knowles intake sheet).
- **Pending Wikidata:** three items drafted in `WIKIDATA_DRAFT.md`, awaiting autoconfirmed gating on Brandon's Wikimedia account (4 days + 50 edits — see CLAUDE.md).

**For current development state, always look at:**
- `CLAUDE.md` → the most recent session-log entry.
- `ARCHITECTURE.md` §4.7 → in-flight staging surface (updated periodically).

---

## 10. Who to call

- **Wikibase Cloud support:** [TO COMPLETE — direct contact channel if known; otherwise the Wikibase Cloud help portal]
- **Cloudflare support:** standard channel for the account's support tier — login required at [`dash.cloudflare.com/support`](https://dash.cloudflare.com/support)
- **GitHub support:** [`github.com/contact`](https://github.com/contact)
- **Registrar support:** [TO COMPLETE — depends on registrar identified in §3.4]
- **People in Brandon's network who know the project well enough to orient a successor:** [TO COMPLETE — possibly Olivia Jol as a researcher participant; possibly an academic advisor; possibly the foundation board]

---

## Maintenance

This document should be kept current whenever:
- A vendor account changes (new admin, rotated credential, transferred ownership).
- The domain or DNS arrangement changes.
- A new recovery path is verified (or fails).
- The deferred-by-design list grows (a new "we chose this; don't undo it" decision is made).

The architectural state — what's in flight, what's been promoted, what's pending — lives in `ARCHITECTURE.md` and `CLAUDE.md`. This document should not try to track that.
