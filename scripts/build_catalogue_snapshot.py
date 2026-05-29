#!/usr/bin/env python3
"""
Build the public catalogue snapshot and push it to R2 — the resilience
fallback that keeps browse/next.html browsable when the Wikibase Cloud
SPARQL endpoint is unreachable.

Why this exists
---------------
The site reads its catalogue live from Wikibase SPARQL. That endpoint is
the one piece of the stack that is NOT static — if it is down, slow, or
mid-reindex, a *returning* visitor still sees their localStorage cache,
but a *first-time* visitor sees nothing. This script writes a snapshot of
the whole catalogue to R2 (Cloudflare — the same always-up CDN the images
live on). The browser falls back to it (see loadFromWikibase →
fetchSnapshot in next.html) so EVERYONE keeps seeing the archive during a
Wikibase outage.

Two artifacts, same data:
  • catalogue.json — raw SPARQL bindings, wrapped with a small header.
    This is what the browser consumes: it feeds the `bindings` array
    straight into processRows(), the exact same code path as a live
    SPARQL response, so the snapshot can never drift in *shape* from a
    live load. (It can drift in *freshness* — that's fine, it's a
    fallback — and in *fields* only if the query below diverges from
    next.html's CATALOGUE_QUERY; see the sync note on CATALOGUE_QUERY.)
  • catalogue.csv — one flat row per item, multi-value fields joined
    with "; ". Human-readable export (open in Excel / hand to an
    archivist). NOT consumed by the site.

⚠ SYNC NOTE — single most important maintenance fact:
  CATALOGUE_QUERY below must mirror next.html's CATALOGUE_QUERY (same
  name, ~line 5290). They are two copies of one contract. If you add a
  field to the SPARQL in next.html, add it here too, or the snapshot
  fallback will silently lack that field. Same discipline as the old
  index.html prefetch-sync rule. (A future validate.mjs check could
  diff the two; not wired yet.)

Read-only against Wikibase (public SPARQL, no bot credentials). The only
write is the rclone push to R2, which needs the `hh-r2` remote (already
configured) — no R2 keys in this file.

Usage:
    python3 scripts/build_catalogue_snapshot.py                 # dry-run: build locally, show what WOULD push
    python3 scripts/build_catalogue_snapshot.py --execute       # build + push to R2
    python3 scripts/build_catalogue_snapshot.py --no-csv        # JSON only
    python3 scripts/build_catalogue_snapshot.py --out /tmp/snap # local dir override

Exit codes:
    0 → snapshot built (and pushed, if --execute)
    1 → SPARQL fetch failed, or rclone push failed
"""

import argparse
import csv
import datetime as dt
import io
import json
import os
import subprocess
import sys

try:
    import requests
except ImportError:
    sys.exit("Missing 'requests'.  pip3 install requests")


SPARQL = "https://hunterhouse.wikibase.cloud/query/sparql"
USER_AGENT = "HunterHouseSnapshot/1.0 (build_catalogue_snapshot; bturep)"

# R2 destination. The browser fetches the JSON from the public CDN base;
# rclone pushes to the bucket-relative path under the same host.
R2_REMOTE = "hh-r2:hunter-house-archive"
R2_DIR = "catalogue"                       # → archive.hunterhousefoundation.com/catalogue/
R2_CDN_BASE = "https://archive.hunterhousefoundation.com"

DEFAULT_OUT = "data/snapshots/catalogue"

# ── CATALOGUE_QUERY ──────────────────────────────────────────────────────
# MUST mirror next.html's CATALOGUE_QUERY (see SYNC NOTE in the docstring).
# PIDs are spelled out here (next.html interpolates them from PROPERTIES);
# the resolved query is identical.
CATALOGUE_QUERY = """
PREFIX wdt: <https://hunterhouse.wikibase.cloud/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX bd: <http://www.bigdata.com/rdf#>
SELECT ?item ?archId ?label ?img ?master
       ?d1 ?d2 ?d3
       ?phase ?phaseLabel ?phase2 ?phase2Label
       ?drawType ?drawTypeLabel
       ?area ?areaLabel
       ?category ?categoryLabel
       ?itype ?itypeLabel
       ?src ?srcLabel
       ?creator ?creatorLabel
       ?builtBy ?builtByLabel
       ?designedBy ?designedByLabel
       ?use ?useLabel ?scale ?medium
       ?builtStatus ?builtStatusLabel
       ?setPos ?notes
       ?rights ?rightsLabel
       ?heldBy ?heldByLabel
       ?archiveLink ?location ?accessCopy ?rotation
WHERE {
  ?item wdt:P2 ?archId .
  OPTIONAL { ?item wdt:P96 ?img }
  ?item rdfs:label ?label . FILTER(LANG(?label)="en")
  OPTIONAL { ?item wdt:P95 ?master }
  OPTIONAL { ?item wdt:P82 ?d1 }
  OPTIONAL { ?item wdt:P64 ?d2 }
  OPTIONAL { ?item wdt:P118 ?d3 }
  OPTIONAL { ?item wdt:P62 ?phase . ?phase rdfs:label ?phaseLabel . FILTER(LANG(?phaseLabel)="en") }
  OPTIONAL { ?item wdt:P84 ?phase2 . ?phase2 rdfs:label ?phase2Label . FILTER(LANG(?phase2Label)="en") }
  OPTIONAL { ?item wdt:P88 ?drawType . ?drawType rdfs:label ?drawTypeLabel . FILTER(LANG(?drawTypeLabel)="en") }
  OPTIONAL { ?item wdt:P87 ?area . ?area rdfs:label ?areaLabel . FILTER(LANG(?areaLabel)="en") }
  OPTIONAL { ?item wdt:P145 ?category . ?category rdfs:label ?categoryLabel . FILTER(LANG(?categoryLabel)="en") }
  OPTIONAL { ?item wdt:P1 ?itype . ?itype rdfs:label ?itypeLabel . FILTER(LANG(?itypeLabel)="en") }
  ?item wdt:P79 ?src .
  OPTIONAL { ?src rdfs:label ?srcLabel . FILTER(LANG(?srcLabel)="en") }
  OPTIONAL { ?item wdt:P80 ?creator . ?creator rdfs:label ?creatorLabel . FILTER(LANG(?creatorLabel)="en") }
  OPTIONAL { ?item wdt:P140 ?builtBy . ?builtBy rdfs:label ?builtByLabel . FILTER(LANG(?builtByLabel)="en") }
  OPTIONAL { ?item wdt:P141 ?designedBy . ?designedBy rdfs:label ?designedByLabel . FILTER(LANG(?designedByLabel)="en") }
  OPTIONAL { ?item wdt:P89 ?use . ?use rdfs:label ?useLabel . FILTER(LANG(?useLabel)="en") }
  OPTIONAL { ?item wdt:P90 ?scale }
  OPTIONAL { ?item wdt:P91 ?medium }
  OPTIONAL { ?item wdt:P92 ?builtStatus . ?builtStatus rdfs:label ?builtStatusLabel . FILTER(LANG(?builtStatusLabel)="en") }
  OPTIONAL { ?item wdt:P86 ?setPos }
  OPTIONAL { ?item wdt:P100 ?notes }
  OPTIONAL { ?item wdt:P93 ?rights . ?rights rdfs:label ?rightsLabel . FILTER(LANG(?rightsLabel)="en") }
  OPTIONAL { ?item wdt:P94 ?heldBy . ?heldBy rdfs:label ?heldByLabel . FILTER(LANG(?heldByLabel)="en") }
  OPTIONAL { ?item wdt:P99 ?archiveLink }
  OPTIONAL { ?item wdt:P142 ?location }
  OPTIONAL { ?item wdt:P143 ?accessCopy }
  OPTIONAL { ?item wdt:P144 ?rotation }
}"""


def sparql(query):
    """Run the catalogue query against the public SPARQL endpoint.

    Returns the raw bindings list (results.bindings) — exactly the shape
    the browser's sparqlQuery() returns and processRows() consumes.
    """
    r = requests.get(
        SPARQL,
        params={"query": query, "format": "json"},
        headers={"Accept": "application/sparql-results+json", "User-Agent": USER_AGENT},
        timeout=120,
    )
    r.raise_for_status()
    return r.json()["results"]["bindings"]


def distinct_items(bindings):
    """Count distinct ?item QIDs in the bindings (one item spans several
    rows when it has multi-value areas / drawTypes / builtBy)."""
    return len({b["item"]["value"] for b in bindings if "item" in b})


# CSV is a flattened, human-facing view. Multi-value fields (area,
# drawType, builtBy, category) are collapsed per item with "; ".  The
# browser never reads this file — it exists for archivist export.
CSV_COLUMNS = [
    "archId", "qid", "label", "itemType", "sourceCollection", "heldBy",
    "phase", "date", "creator", "designedBy", "builtBy", "drawTypes",
    "areas", "categories", "use", "scale", "medium", "builtStatus",
    "setPosition", "rotation", "location", "rights", "notes",
    "image", "master", "accessCopy", "archiveLink",
]


def bindings_to_csv_rows(bindings):
    """Collapse the row-per-statement bindings into one dict per item."""
    def val(b, k):
        return b[k]["value"] if k in b else ""

    def date_of(b):
        for k in ("d1", "d2", "d3"):
            if k in b:
                return b[k]["value"].lstrip("+").split("T")[0]
        return ""

    by_qid = {}
    for b in bindings:
        qid = b["item"]["value"].rsplit("/", 1)[-1]
        row = by_qid.get(qid)
        if row is None:
            row = {
                "archId": val(b, "archId"),
                "qid": qid,
                "label": val(b, "label"),
                "itemType": val(b, "itypeLabel"),
                "sourceCollection": val(b, "srcLabel"),
                "heldBy": val(b, "heldByLabel"),
                "phase": val(b, "phaseLabel") or val(b, "phase2Label"),
                "date": date_of(b),
                "creator": val(b, "creatorLabel"),
                "designedBy": val(b, "designedByLabel"),
                "builtBy": set(),
                "drawTypes": set(),
                "areas": set(),
                "categories": set(),
                "use": val(b, "useLabel"),
                "scale": val(b, "scale"),
                "medium": val(b, "medium"),
                "builtStatus": val(b, "builtStatusLabel"),
                "setPosition": val(b, "setPos"),
                "rotation": val(b, "rotation"),
                "location": val(b, "location"),
                "rights": val(b, "rightsLabel"),
                "notes": val(b, "notes"),
                "image": val(b, "img"),
                "master": val(b, "master"),
                "accessCopy": val(b, "accessCopy"),
                "archiveLink": val(b, "archiveLink"),
            }
            by_qid[qid] = row
        # accumulate multi-value fields
        if "builtByLabel" in b:   row["builtBy"].add(b["builtByLabel"]["value"])
        if "drawTypeLabel" in b:  row["drawTypes"].add(b["drawTypeLabel"]["value"])
        if "areaLabel" in b:      row["areas"].add(b["areaLabel"]["value"])
        if "categoryLabel" in b:  row["categories"].add(b["categoryLabel"]["value"])

    out = []
    for row in sorted(by_qid.values(), key=lambda r: r["archId"]):
        for k in ("builtBy", "drawTypes", "areas", "categories"):
            row[k] = "; ".join(sorted(row[k]))
        out.append(row)
    return out


def write_csv(bindings, path):
    rows = bindings_to_csv_rows(bindings)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=CSV_COLUMNS, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(buf.getvalue())
    return len(rows)


def rclone_copy(local_path, dry_run):
    """Push one file to R2 via rclone copyto (so dest is the exact key)."""
    fname = os.path.basename(local_path)
    dest = f"{R2_REMOTE}/{R2_DIR}/{fname}"
    args = ["rclone", "copyto", local_path, dest, "--stats", "0", "--progress=false"]
    if dry_run:
        args.append("--dry-run")
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=120)
    except FileNotFoundError:
        return False, "  ✗ rclone not found on PATH"
    except subprocess.TimeoutExpired:
        return False, "  ✗ rclone timed out after 120s"
    out = (r.stdout + r.stderr).strip()
    public = f"{R2_CDN_BASE}/{R2_DIR}/{fname}"
    tag = "(dry-run) would push" if dry_run else "pushed"
    line = f"  {tag} → {public}" + (f"\n  {out}" if out else "")
    return r.returncode == 0, line


def main():
    ap = argparse.ArgumentParser(description="Build + push the public catalogue snapshot to R2.")
    ap.add_argument("--execute", action="store_true", help="actually push to R2 (default: dry-run)")
    ap.add_argument("--no-csv", action="store_true", help="skip the human-readable CSV export")
    ap.add_argument("--out", default=DEFAULT_OUT, help=f"local output dir (default: {DEFAULT_OUT})")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    print("Fetching catalogue from Wikibase SPARQL …")
    try:
        bindings = sparql(CATALOGUE_QUERY)
    except Exception as e:
        sys.exit(f"✗ SPARQL fetch failed: {e}")

    n_items = distinct_items(bindings)
    if n_items == 0:
        sys.exit("✗ SPARQL returned zero items — refusing to write an empty snapshot.")

    generated = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    snapshot = {
        "generated": generated,
        "source": SPARQL,
        "item_count": n_items,
        "binding_count": len(bindings),
        "note": "Fallback catalogue snapshot. Browser feeds `bindings` to processRows(). "
                "Mirror of next.html CATALOGUE_QUERY — see build_catalogue_snapshot.py SYNC NOTE.",
        "bindings": bindings,
    }

    json_path = os.path.join(args.out, "catalogue.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, separators=(",", ":"))
    size_kb = os.path.getsize(json_path) / 1024
    print(f"  wrote {json_path}  ({n_items} items, {len(bindings)} bindings, {size_kb:.0f} KB)")

    pushes = [json_path]
    if not args.no_csv:
        csv_path = os.path.join(args.out, "catalogue.csv")
        n_csv = write_csv(bindings, csv_path)
        print(f"  wrote {csv_path}  ({n_csv} item rows)")
        pushes.append(csv_path)

    mode = "EXECUTE" if args.execute else "DRY-RUN"
    print(f"\nR2 push ({mode}) → {R2_CDN_BASE}/{R2_DIR}/")
    all_ok = True
    for p in pushes:
        ok, line = rclone_copy(p, dry_run=not args.execute)
        all_ok = all_ok and ok
        print(line)

    if not all_ok:
        sys.exit(1)
    if not args.execute:
        print("\n(dry-run — re-run with --execute to push to R2)")


if __name__ == "__main__":
    main()
