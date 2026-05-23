#!/usr/bin/env python3
"""
R2 pipeline integrity check — addresses ARCHITECTURE.md §11.3 + §11.1 HIGH.

Two passes (both default-on; skip either with the flags below):
  1. Image / PDF URL claims (P95 master, P96 preview, P143 access copy).
     A silent ingest failure or a later R2 rename leaves a 404-pointing
     claim with no canary anywhere — this catches it.
  2. Metadata sidecar URLs (derived from archId + collection, written
     by scripts/sync_one_metadata.py at ingest time and refreshed in
     bulk by scripts/sync_metadata_to_r2.py). Confirms the §11.1 HIGH
     preservation pipeline is actually landing files on R2.

Read-only. No bot credentials needed (SPARQL + HEAD only). Sequential
HEADs are intentionally polite (50–150 ms per request × ~1000 URLs ≈
~2 min on this catalogue) — no concurrency complexity unless the
catalogue grows by an order of magnitude.

Usage:
    python3 scripts/verify_r2_links.py
    python3 scripts/verify_r2_links.py --pid P96       # one image-prop only
    python3 scripts/verify_r2_links.py --no-sidecars   # legacy: image/PDF only
    python3 scripts/verify_r2_links.py --sidecars-only # just preservation check
    python3 scripts/verify_r2_links.py --json out.json # machine-readable report

Exit codes:
    0  → every URL returned 2xx
    1  → at least one URL failed (4xx / 5xx / unreachable)

Suggested cadence: run before each session-end. If/when CI gains R2
access, this is the obvious next job to add to .github/workflows/.
"""

import argparse
import json
import sys
import time

try:
    import requests
except ImportError:
    sys.exit("Missing 'requests'.  pip3 install requests")


SPARQL = "https://hunterhouse.wikibase.cloud/query/sparql"
USER_AGENT = "HunterHouseVerify/1.0 (verify_r2_links; bturep)"

# URL-bearing properties we care about. Add to this dict if a new
# url-datatype property is minted later.
URL_PROPERTIES = {
    "P95":  "master image",
    "P96":  "preview image",
    "P143": "access copy (PDF)",
}

# Metadata sidecar URLs are *derived* from archId + collection (the
# ingest scripts write them via scripts/sync_one_metadata.py). We check
# them by computing the expected URL and HEAD-probing R2.
R2_CDN_BASE = "https://archive.hunterhousefoundation.com"
COLLECTION_FOLDER = {
    "HHC": "hunter-house-collection",
    "CAA": "canadian-architecture-archive",
    "EGC": "eric-gesinger-collection",
}


def sidecar_url_for(arch_id):
    """Derive the canonical R2 sidecar URL for one archId.

    Returns None if the archId's collection prefix isn't in our R2 map
    (e.g. legacy HH-A-* IDs, or a brand-new collection prefix not yet
    wired up). Callers should treat None as "no sidecar to check".
    """
    parts = arch_id.split("-")
    if len(parts) < 3:
        return None
    folder = COLLECTION_FOLDER.get(parts[1])
    if not folder:
        return None
    return f"{R2_CDN_BASE}/{folder}/metadata/{arch_id}.json"

# Per-request timeout (seconds). Most R2 HEADs respond in <200ms; 10s
# is generous enough to absorb a CDN cold-cache fetch without false-
# positives, and short enough that a true outage fails fast.
HTTP_TIMEOUT = 10


def sparql(query):
    r = requests.get(SPARQL, params={"query": query, "format": "json"},
                     headers={"Accept": "application/sparql-results+json",
                              "User-Agent": USER_AGENT},
                     timeout=30)
    r.raise_for_status()
    return r.json()["results"]["bindings"]


def fetch_urls(pids):
    """Return [{archId, qid, pid, url}, …] for every URL claim on a
    catalogue item under one of the given PIDs."""
    rows = []
    for pid in pids:
        q = f"""
PREFIX wdt: <https://hunterhouse.wikibase.cloud/prop/direct/>
SELECT ?item ?archId ?url WHERE {{
  ?item wdt:P2 ?archId .
  ?item wdt:P79 ?src .
  ?item wdt:{pid} ?url .
}}
ORDER BY ?archId
"""
        for row in sparql(q):
            rows.append({
                "qid":     row["item"]["value"].rsplit("/", 1)[-1],
                "archId":  row["archId"]["value"],
                "pid":     pid,
                "url":     row["url"]["value"],
            })
    return rows


def fetch_sidecar_urls():
    """Return [{archId, qid, pid, url}, …] for every catalogue item's
    derived sidecar URL. Uses pid='SIDECAR' (synthetic) so the rest of
    the verifier loop can treat them uniformly."""
    q = """
PREFIX wdt: <https://hunterhouse.wikibase.cloud/prop/direct/>
SELECT ?item ?archId WHERE {
  ?item wdt:P2 ?archId .
  ?item wdt:P79 ?src .
}
ORDER BY ?archId
"""
    rows = []
    for row in sparql(q):
        arch_id = row["archId"]["value"]
        url = sidecar_url_for(arch_id)
        if not url:
            continue   # archId we don't have an R2 folder mapping for
        rows.append({
            "qid":     row["item"]["value"].rsplit("/", 1)[-1],
            "archId":  arch_id,
            "pid":     "SIDECAR",
            "url":     url,
        })
    return rows


def head(url):
    """HEAD with a redirect-allowed retry. Returns (ok, status, note)."""
    try:
        r = requests.head(url, allow_redirects=True, timeout=HTTP_TIMEOUT,
                          headers={"User-Agent": USER_AGENT})
        return (r.status_code < 400, r.status_code, "")
    except requests.exceptions.Timeout:
        return (False, None, "timeout")
    except requests.exceptions.RequestException as e:
        return (False, None, type(e).__name__)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pid", choices=sorted(URL_PROPERTIES.keys()), action="append",
                    help="restrict image/PDF check to one or more PIDs (default: all)")
    ap.add_argument("--no-sidecars", action="store_true",
                    help="skip the derived sidecar URL check (§11.1 HIGH part 2)")
    ap.add_argument("--sidecars-only", action="store_true",
                    help="ONLY check sidecar URLs (skip image/PDF claims)")
    ap.add_argument("--json", metavar="PATH",
                    help="also write a machine-readable report to PATH")
    args = ap.parse_args()

    pids = args.pid or sorted(URL_PROPERTIES.keys())
    urls = []
    if not args.sidecars_only:
        print(f"→ SPARQL: enumerating URLs for {', '.join(pids)} …")
        urls.extend(fetch_urls(pids))
        print(f"  found {len(urls)} URL claims across {len(set(r['archId'] for r in urls))} items")
    if not args.no_sidecars:
        print(f"→ SPARQL: deriving sidecar URLs for every catalogue item …")
        sc = fetch_sidecar_urls()
        print(f"  derived {len(sc)} sidecar URLs (one per catalogue item)")
        urls.extend(sc)

    print(f"→ HEAD-checking each (timeout {HTTP_TIMEOUT}s, sequential) …")
    started = time.time()
    failures = []
    by_status = {}
    for i, row in enumerate(urls, 1):
        ok, status, note = head(row["url"])
        key = note or str(status)
        by_status[key] = by_status.get(key, 0) + 1
        if not ok:
            failures.append({**row, "status": status, "note": note})
            print(f"  ✗ [{i:3d}/{len(urls)}] {row['archId']} {row['pid']} "
                  f"→ {status or note}  {row['url']}")
        elif i % 50 == 0 or i == len(urls):
            elapsed = time.time() - started
            print(f"  · [{i:3d}/{len(urls)}] {elapsed:0.1f}s elapsed, "
                  f"{len(failures)} failures so far")

    elapsed = time.time() - started
    print()
    print(f"summary ({elapsed:0.1f}s):")
    for key, count in sorted(by_status.items()):
        marker = "✓" if key == "200" else "✗"
        print(f"  {marker} {key:8} × {count}")

    if args.json:
        with open(args.json, "w") as f:
            json.dump({
                "checked":  len(urls),
                "elapsed":  elapsed,
                "by_status": by_status,
                "failures": failures,
            }, f, indent=2, sort_keys=True)
        print(f"  json report → {args.json}")

    if failures:
        print(f"\n{len(failures)} URL(s) failed — see above")
        sys.exit(1)
    print(f"\n✓ all {len(urls)} URLs return 2xx")


if __name__ == "__main__":
    main()
