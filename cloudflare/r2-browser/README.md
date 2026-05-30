# hhf-r2-browser — read-only R2 listing Worker

Powers the researcher **bucket browser** in `next.html`. It exposes a single
read-only endpoint that lists one folder level of the `hunter-house-archive`
R2 bucket. Downloads are served by the existing public custom domain
(`https://archive.hunterhousefoundation.com/<key>`), **not** by this Worker.

It can only `list()` — there is no `put`/`delete`/`copy` in the code, so the
archive cannot be written to or rearranged through it.

## Endpoint

```
GET /list?prefix=<key-prefix>&cursor=<token>
→ { prefix, folders:[{type,key,name}], files:[{type,key,name,size,uploaded}],
    truncated, cursor }
```

- `prefix=""` → the top-level collection folders.
- `prefix="hunter-house-collection/masters/"` → that folder's contents.
- `cursor` → only needed for folders with >1000 direct entries (rare).

## Deploy (one-time, needs an interactive Cloudflare login)

From this directory:

```bash
cd cloudflare/r2-browser
npx wrangler login      # opens a browser to authorise the Cloudflare account
npx wrangler deploy     # builds + deploys; prints the Worker URL
```

`wrangler deploy` prints a URL like:

```
https://hhf-r2-browser.<your-account>.workers.dev
```

Copy that URL — it goes into `next.html` in two places (the client step):
1. `const R2_LIST_API = "<that URL>";`
2. the CSP `connect-src` allowlist (add the `*.workers.dev` host).

To watch logs while testing: `npx wrangler tail`.

## Notes

- CORS allowlist lives in `src/worker.js` (`ALLOW_ORIGINS`). It already permits
  `https://bturep.github.io` plus `localhost:8777` / `127.0.0.1:8777` for local
  dev. Add other origins there and re-`deploy` if needed.
- Later, the Worker can be mapped to a custom subdomain (e.g.
  `list.hunterhousefoundation.com`) via a route in `wrangler.toml` + a DNS
  record; the `workers.dev` URL is fine to start.
