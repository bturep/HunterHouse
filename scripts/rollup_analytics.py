#!/usr/bin/env python3
"""
Monthly analytics rollup — preserve usage history past Analytics Engine's ~90-day
retention by snapshotting each month's aggregates to a permanent file in the repo.

WHY: Cloudflare Analytics Engine keeps raw data points for only ~90 days (rolling).
This script queries the live dataset, aggregates one calendar month, and writes
data/analytics/<YYYY-MM>.json — a permanent, version-controlled record. It also
regenerates data/analytics/monthly-summary.csv (one row per month) from all the
JSON files, so the long-term trend survives even though the raw points expire.

Runs monthly via .github/workflows/rollup-analytics.yml (or manually). Read-only:
the only thing it touches is the repo files it writes.

AUTH (Cloudflare Analytics Engine SQL API):
  - CI: env CF_ANALYTICS_TOKEN  (GitHub secret; a token scoped Account Analytics:Read)
  - Local: falls back to the wrangler OAuth login if that env var is absent.
  CF_ACCOUNT_ID defaults to the account that owns the dataset (not secret).

USAGE:
  python3 scripts/rollup_analytics.py                 # prior calendar month
  python3 scripts/rollup_analytics.py --month 2026-06 # a specific month
  python3 scripts/rollup_analytics.py --summary-only   # just rebuild the CSV
"""

import os
import re
import sys
import json
import glob
from datetime import date

try:
    import requests
except ImportError:
    sys.exit("Missing 'requests'. Install with:  pip3 install requests")

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "data", "analytics")
ACCOUNT_ID = os.environ.get("CF_ACCOUNT_ID", "628a738b1d9d965f53070f1729bcf596")
DATASET = "Hunter_House_Archive"
SQL_API = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/analytics_engine/sql"
TOP_N = 50   # cap per ranked list


def resolve_token():
    tok = os.environ.get("CF_ANALYTICS_TOKEN")
    if tok:
        return tok
    # Local fallback: the wrangler OAuth token (works for the AE SQL API).
    for f in (glob.glob(os.path.expanduser("~/Library/Preferences/.wrangler/config/*.toml"))
              + glob.glob(os.path.expanduser("~/.wrangler/config/*.toml"))):
        try:
            m = re.search(r'oauth_token\s*=\s*"([^"]+)"', open(f).read())
            if m:
                return m.group(1)
        except OSError:
            pass
    sys.exit("No analytics token. Set CF_ANALYTICS_TOKEN, or run `npx wrangler login` locally.")


def q(token, sql):
    r = requests.post(SQL_API, headers={"Authorization": f"Bearer {token}"}, data=sql, timeout=60)
    try:
        j = r.json()
    except ValueError:
        sys.exit(f"AE SQL API returned non-JSON (HTTP {r.status_code}): {r.text[:200]}")
    if isinstance(j, dict) and j.get("errors"):
        sys.exit(f"AE SQL API error: {json.dumps(j['errors'])}")
    return j.get("data", [])


def month_bounds(ym):
    y, m = map(int, ym.split("-"))
    start = date(y, m, 1)
    end = date(y + 1, 1, 1) if m == 12 else date(y, m + 1, 1)
    return f"{start} 00:00:00", f"{end} 00:00:00"


def prior_month():
    t = date.today()
    p = date(t.year - 1, 12, 1) if t.month == 1 else date(t.year, t.month - 1, 1)
    return f"{p.year}-{p.month:02d}"


def rollup_month(token, ym):
    start, end = month_bounds(ym)
    win = f"timestamp >= toDateTime('{start}') AND timestamp < toDateTime('{end}')"

    def rows(select, extra=""):
        return q(token, f"SELECT {select} FROM {DATASET} WHERE {win} {extra}")

    def ranked(select, extra):
        return [{k: (int(v) if str(v).isdigit() else v) for k, v in r.items()}
                for r in rows(select, extra)]

    by_type = {r["event"]: int(r["n"]) for r in rows("blob1 AS event, count() AS n", "GROUP BY event")}
    out = {
        "period": ym,
        "dataset": DATASET,
        "totals": {
            "events": sum(by_type.values()),
            "views": by_type.get("view", 0),
            "searches": by_type.get("search", 0),
            "zero_result_searches": by_type.get("search0", 0),
            "downloads": by_type.get("download", 0),
        },
        "events_by_type": by_type,
        "top_items": ranked("blob2 AS id, count() AS views",
                            f"AND blob1='view' AND blob2!='' GROUP BY id ORDER BY views DESC LIMIT {TOP_N}"),
        "top_searches": ranked("blob4 AS q, count() AS n",
                               f"AND blob1='search' AND blob4!='' GROUP BY q ORDER BY n DESC LIMIT {TOP_N}"),
        "zero_result_searches": ranked("blob4 AS q, count() AS n",
                                       f"AND blob1='search0' AND blob4!='' GROUP BY q ORDER BY n DESC LIMIT {TOP_N}"),
        "downloads_by_collection": ranked("blob3 AS collection, count() AS n",
                                          f"AND blob1='download' GROUP BY collection ORDER BY n DESC LIMIT {TOP_N}"),
        "by_country": ranked("blob5 AS country, count() AS n",
                             f"AND blob5!='' GROUP BY country ORDER BY n DESC LIMIT {TOP_N}"),
    }
    return out


def write_month(out):
    os.makedirs(OUT_DIR, exist_ok=True)
    path = os.path.join(OUT_DIR, f"{out['period']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return path


def rebuild_summary():
    """One CSV row per month, rebuilt from every <YYYY-MM>.json — self-healing."""
    files = sorted(glob.glob(os.path.join(OUT_DIR, "20*-*.json")))
    lines = ["month,events,views,searches,zero_result_searches,downloads,top_item,top_search"]
    for fp in files:
        d = json.load(open(fp, encoding="utf-8"))
        t = d.get("totals", {})
        ti = (d.get("top_items") or [{}])[0].get("id", "")
        ts = (d.get("top_searches") or [{}])[0].get("q", "")
        ts = '"' + ts.replace('"', '""') + '"' if ts else ""
        lines.append(",".join(str(x) for x in [
            d.get("period", ""), t.get("events", 0), t.get("views", 0),
            t.get("searches", 0), t.get("zero_result_searches", 0),
            t.get("downloads", 0), ti, ts]))
    path = os.path.join(OUT_DIR, "monthly-summary.csv")
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    return path, len(files)


def main(argv):
    if "--summary-only" in argv:
        path, n = rebuild_summary()
        print(f"✓ rebuilt {path} from {n} monthly file(s)")
        return 0
    ym = prior_month()
    if "--month" in argv:
        ym = argv[argv.index("--month") + 1]
    if not re.fullmatch(r"\d{4}-\d{2}", ym):
        sys.exit(f"bad --month '{ym}' (expected YYYY-MM)")

    token = resolve_token()
    out = rollup_month(token, ym)
    path = write_month(out)
    spath, n = rebuild_summary()
    t = out["totals"]
    print(f"✓ {path}")
    print(f"  {ym}: {t['events']} events — {t['views']} views, {t['searches']} searches "
          f"({t['zero_result_searches']} zero-result), {t['downloads']} downloads")
    print(f"✓ {spath} ({n} month(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
