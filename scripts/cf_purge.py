#!/usr/bin/env python3
"""
cf_purge.py — Cloudflare edge-cache purge for the archive zone.

Retires the long-standing "no CF purge token" blocker: once an R2 object is
overwritten or deleted, the custom-domain edge cache can keep serving stale
bytes (cf-cache-status often misreports DYNAMIC). This forces an eviction so
the fix is visible immediately instead of waiting out an unreadable TTL.

Credentials load from ~/Documents/hh-wikibase-migration/.env (never embedded):
    CF_CACHE_PURGE_TOKEN   scoped token, Zone.Cache Purge only
    CF_ZONE_ID             zone id for hunterhousefoundation.com

Usage:
    python3 scripts/cf_purge.py <url> [<url> ...]     # purge specific URLs (up to 30/call)
    python3 scripts/cf_purge.py --file urls.txt       # one URL per line
    python3 scripts/cf_purge.py --everything          # purge whole zone (cold-caches all)

Read-only against R2/Wikibase; the only effect is cache eviction.
"""
import json
import os
import sys
import urllib.request

ENV_PATH = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")
API = "https://api.cloudflare.com/client/v4/zones/{zid}/purge_cache"


def load_env():
    creds = {}
    with open(ENV_PATH) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            creds[k.strip()] = v.strip()
    tok = creds.get("CF_CACHE_PURGE_TOKEN")
    zid = creds.get("CF_ZONE_ID")
    if not tok or not zid:
        sys.exit("Missing CF_CACHE_PURGE_TOKEN / CF_ZONE_ID in .env")
    return tok, zid


def purge(tok, zid, payload):
    req = urllib.request.Request(
        API.format(zid=zid),
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req) as resp:
            body = json.load(resp)
    except urllib.error.HTTPError as e:
        body = json.load(e)
    return body


def main():
    args = sys.argv[1:]
    if not args:
        sys.exit(__doc__)
    tok, zid = load_env()

    if args[0] == "--everything":
        payload = {"purge_everything": True}
    elif args[0] == "--file":
        if len(args) < 2:
            sys.exit("--file needs a path")
        with open(args[1]) as fh:
            urls = [ln.strip() for ln in fh if ln.strip()]
        payload = {"files": urls}
    else:
        payload = {"files": args}

    if "files" in payload and len(payload["files"]) > 30:
        sys.exit(f"{len(payload['files'])} URLs — Cloudflare caps purge-by-URL at 30/call. Batch it.")

    body = purge(tok, zid, payload)
    if body.get("success"):
        n = "everything" if "purge_everything" in payload else f"{len(payload['files'])} URL(s)"
        print(f"✓ purged {n}")
    else:
        print("✗ purge failed:", json.dumps(body.get("errors"), indent=2))
        sys.exit(1)


if __name__ == "__main__":
    main()
