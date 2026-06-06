# hhf-r2-browser — read-only R2 listing Worker

Powers the (planned) researcher **bucket browser** in `next.html`. Exposes one
read-only endpoint that lists a single folder level of the `hunter-house-archive`
R2 bucket. Downloads are served by the existing public custom domain
(`https://archive.hunterhousefoundation.com/<key>`), **not** by this Worker.

List-only: the code calls the R2 **S3 API** `ListObjectsV2` and nothing else —
no Put/Delete/Copy — so the archive cannot be written to or rearranged.

## Why the S3 API (not a native R2 binding)

The bucket lives in the **Foundation** Cloudflare account
(`3f5df2ae…`, [redacted-email]), where Brandon has **R2 Admin** but
**not Workers**. Native R2 bindings are same-account only, so instead the Worker
is deployed in **Brandon's own account** (`628a…`, full Workers rights) and
reaches the bucket cross-account over the signed S3 endpoint with a **read-only
R2 token**.

## Endpoints

```
GET  /list?prefix=<key-prefix>&cursor=<continuation-token>
→ { prefix, folders:[{type,key,name}], files:[{type,key,name,size,uploaded}],
    truncated, cursor }

GET  /dl?key=<bucket-key>      → 302 to https://archive.hunterhousefoundation.com/<key>
                                 (logs a download first; behaviour unchanged for
                                 the visitor — same file, we just count it)

POST /event   {t,id,q,n,p}     → 204  (cookieless usage beacon from the SPA:
                                 item views, searches, deep-links, tool opens)
```

### Cookieless usage analytics (added 2026-06-06)

`/dl` and `/event` let the Foundation see how the archive is used **without a
third-party tracker and without needing dashboard access in Floyd's account** —
everything stays in Brandon's own account, like the listing does. No cookies, no
identifiers, no stored IPs; only coarse country (added at the edge). The SPA
honours Do-Not-Track / Global-Privacy-Control. Each hit:

- `console.log`s a structured line → **Workers Logs** (dashboard → this Worker →
  Logs) and `wrangler tail`. Works on any plan.
- best-effort writes one point to **Workers Analytics Engine** (dataset
  `Hunter_House_Archive`; column map in `src/worker.js`).

**Analytics Engine — enabled 2026-06-06.** AE is on for the account and the
dataset `Hunter_House_Archive` exists (created in the dashboard); the
`[[analytics_engine_datasets]]` binding in `wrangler.toml` is live (`binding =
"AE"`, the name the Worker reads via `env.AE`). Query via the Analytics Engine
SQL API. The `console.log` → Workers Logs path runs regardless, so usage is
visible there too. If the binding is ever removed the endpoints still function —
they just stop writing data points.

## STATUS (2026-05-30): uploaded but NOT yet live — two setup steps remain

The Worker script uploads, but publishing + listing need these one-time steps:

### 1. Register a `workers.dev` subdomain on account `628a…` (one-time)

wrangler can't publish until the account has a subdomain. Visit:

```
https://dash.cloudflare.com/628a738b1d9d965f53070f1729bcf596/workers/onboarding
```

pick any subdomain, then re-run `npx wrangler deploy` from this directory. It
will print the live URL (`https://hhf-r2-browser.<subdomain>.workers.dev`).

### 2. Set the read-only R2 credentials as secrets

In the **Foundation** account (Cloudflare dashboard → R2 → *Manage R2 API
Tokens* → **Create API token** → permission **Object Read only** → optionally
scope to `hunter-house-archive`). It shows an **Access Key ID** + **Secret
Access Key**. Then, from this directory (run plainly, no leading `!`):

```bash
npx wrangler secret put R2_ACCESS_KEY_ID       # paste the Access Key ID
npx wrangler secret put R2_SECRET_ACCESS_KEY   # paste the Secret Access Key
```

Until both are set, `/list` returns `{"error":"not configured"}`.

### Verify

```bash
curl -s "https://hhf-r2-browser.<subdomain>.workers.dev/list?prefix=" \
  -H "Origin: https://bturep.github.io"
# → JSON with the 7 top-level collection folders
```

## Hidden folders (researcher-facing filtering)

The browser is researcher-facing, so website assets and internal
preservation/plumbing folders are filtered out **server-side** (see
`isHiddenKey` in `src/worker.js`). Hidden folders are dropped from every
listing AND can't be reached by hitting `/list?prefix=…` directly — the guard
returns an empty result for any hidden prefix. The rules:

- `HIDDEN_PREFIXES` — whole subtrees hidden from the bucket root:
  `web/` (now deleted), `_wikibase/`, `catalogue/`.
- `HIDDEN_SEGMENTS` — folder names hidden at any depth: `metadata`, `intake`.
- Any path segment starting with `_` is treated as internal — covers
  `_wikibase` and the `_pre-deskew_…` master-backup folders, plus any future
  underscore-prefixed working folder, automatically.

Researchers therefore see only the four archive collections and their image
tiers (`masters`, `large`, `previews`, `thumbs`, `pdf`). To hide/reveal
something, edit those two lists and `wrangler deploy`.

## Config

- `wrangler.toml` `[vars]`: `R2_ACCOUNT_ID` (Foundation acct that owns the
  bucket) + `R2_BUCKET`. `account_id` pins the deploy to Brandon's account.
- Secrets: `R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY` (set via `wrangler secret put`).
- CORS allowlist: `ALLOW_ORIGINS` in `src/worker.js` (bturep.github.io + loopback).
- Logs while testing: `npx wrangler tail`.
