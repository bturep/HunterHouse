#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────
# Hunter House Foundation — read the usage analytics (Analytics Engine SQL API)
#
# The Worker writes one data point per /event + /dl hit to the
# "Hunter_House_Archive" dataset (column map in src/worker.js). This script runs
# the common reports against it. Read-only.
#
# Auth: by default it reuses the wrangler OAuth login (no extra token needed).
# If that ever stops working (token expired / lacks analytics scope), mint an
# API token with "Account Analytics: Read" and export it first:
#     export CF_API_TOKEN=xxxxxxxx
#
# Usage:
#   ./analytics.sh                 # dashboard: top items, searches, downloads…
#   ./analytics.sh items           # most-viewed items
#   ./analytics.sh searches        # top search terms
#   ./analytics.sh misses          # zero-result searches (catalogue gap-finder)
#   ./analytics.sh downloads        # downloads by collection
#   ./analytics.sh tools           # researcher-tool opens (timeline/files/curation)
#   ./analytics.sh countries        # traffic by country
#   ./analytics.sh raw "SQL…"      # run any SQL against Hunter_House_Archive
#
# Window defaults to the last 30 days; override with DAYS=7 ./analytics.sh …
# ─────────────────────────────────────────────────────────────────────────
set -euo pipefail

ACCT="628a738b1d9d965f53070f1729bcf596"
DATASET="Hunter_House_Archive"
DAYS="${DAYS:-30}"

# Token: explicit CF_API_TOKEN wins; else fall back to the wrangler OAuth token.
TOKEN="${CF_API_TOKEN:-}"
if [ -z "$TOKEN" ]; then
  TOKEN=$(python3 - <<'PY'
import glob, os, re
for f in glob.glob(os.path.expanduser("~/Library/Preferences/.wrangler/config/*.toml")) + \
         glob.glob(os.path.expanduser("~/.wrangler/config/*.toml")):
    try: s = open(f).read()
    except Exception: continue
    m = re.search(r'oauth_token\s*=\s*"([^"]+)"', s)
    if m: print(m.group(1)); break
PY
)
fi
if [ -z "$TOKEN" ]; then
  echo "No auth token. Run 'npx wrangler login', or export CF_API_TOKEN=…" >&2
  exit 1
fi

run() {
  curl -s "https://api.cloudflare.com/client/v4/accounts/$ACCT/analytics_engine/sql" \
    -H "Authorization: Bearer $TOKEN" --data "$1" \
  | python3 -c '
import sys, json
try: d = json.load(sys.stdin)
except Exception: print("  (no/invalid response)"); sys.exit()
if isinstance(d, dict) and d.get("errors"):
    print("  API error:", json.dumps(d["errors"])); sys.exit()
rows = d.get("data", [])
if not rows: print("  (no rows yet — Analytics Engine has a few-min lag)"); sys.exit()
cols = list(rows[0].keys())
w = {c: max(len(c), *(len(str(r[c])) for r in rows)) for c in cols}
print("  " + "  ".join(c.ljust(w[c]) for c in cols))
print("  " + "  ".join("-"*w[c] for c in cols))
for r in rows: print("  " + "  ".join(str(r[c]).ljust(w[c]) for c in cols))
'
}

WIN="timestamp > NOW() - INTERVAL '${DAYS}' DAY"

case "${1:-dashboard}" in
  items)
    run "SELECT blob2 AS item, count() AS views FROM $DATASET
         WHERE blob1='view' AND $WIN GROUP BY item ORDER BY views DESC LIMIT 25" ;;
  searches)
    run "SELECT blob4 AS query, count() AS times FROM $DATASET
         WHERE blob1='search' AND $WIN GROUP BY query ORDER BY times DESC LIMIT 25" ;;
  misses)
    run "SELECT blob4 AS zero_result_query, count() AS times FROM $DATASET
         WHERE blob1='search0' AND $WIN GROUP BY zero_result_query ORDER BY times DESC LIMIT 25" ;;
  downloads)
    run "SELECT blob3 AS collection, blob4 AS tier, count() AS downloads FROM $DATASET
         WHERE blob1='download' AND $WIN GROUP BY collection, tier ORDER BY downloads DESC LIMIT 25" ;;
  tools)
    run "SELECT blob1 AS tool, count() AS opens FROM $DATASET
         WHERE blob1 IN ('timeline','files','curation','deeplink') AND $WIN
         GROUP BY tool ORDER BY opens DESC" ;;
  countries)
    run "SELECT blob5 AS country, count() AS hits FROM $DATASET
         WHERE $WIN GROUP BY country ORDER BY hits DESC LIMIT 25" ;;
  raw)
    run "${2:?usage: ./analytics.sh raw \"SELECT … FROM $DATASET …\"}" ;;
  dashboard|*)
    echo "── Events by type (last ${DAYS}d) ──────────────────────────────"
    run "SELECT blob1 AS event, count() AS n FROM $DATASET WHERE $WIN GROUP BY event ORDER BY n DESC"
    echo; echo "── Top viewed items ────────────────────────────────────────"
    run "SELECT blob2 AS item, count() AS views FROM $DATASET WHERE blob1='view' AND $WIN GROUP BY item ORDER BY views DESC LIMIT 10"
    echo; echo "── Top searches ────────────────────────────────────────────"
    run "SELECT blob4 AS query, count() AS times FROM $DATASET WHERE blob1='search' AND $WIN GROUP BY query ORDER BY times DESC LIMIT 10"
    echo; echo "── Zero-result searches (catalogue gaps) ───────────────────"
    run "SELECT blob4 AS query, count() AS times FROM $DATASET WHERE blob1='search0' AND $WIN GROUP BY query ORDER BY times DESC LIMIT 10"
    echo; echo "── Downloads by collection ─────────────────────────────────"
    run "SELECT blob3 AS collection, count() AS downloads FROM $DATASET WHERE blob1='download' AND $WIN GROUP BY collection ORDER BY downloads DESC LIMIT 10"
    ;;
esac
