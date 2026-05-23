#!/usr/bin/env python3
"""
One-shot Wikibase metadata backup — local-only preservation.

Dumps every catalogue item (anything with a P2 archive ID + P79 source
collection) plus every vocab / person / institution item that those
catalogue items reference, one JSON sidecar per item, into a dated
snapshot directory.

This is the first half of ARCHITECTURE.md §11.1 HIGH (Wikibase has no
offsite metadata backup). The full remediation also writes JSON
sidecars to R2 alongside the image bytes and patches the three ingest
scripts to do the same on each ingest; that work is deferred. Running
this script gives you immediate offline preservation: the full
catalogue is recoverable from disk if the Wikibase Cloud instance
disappears tonight.

Read-only. Uses public API + SPARQL endpoints — no bot credentials,
no R2 keys, nothing to leak.

Usage:
    python3 scripts/backup_metadata.py
    python3 scripts/backup_metadata.py --out /tmp/manual_backup

Output layout (defaults to data/snapshots/wikibase_full_YYYYMMDD/):
    <out>/_manifest.json                     run metadata + per-collection counts
    <out>/<COLLECTION>/<HH-XXX-NNNN>.json    catalogue items, grouped by collection
    <out>/_referenced/<Qnnn>.json            vocab + people + institutions
    <out>/_properties/<Pnn>.json             property definitions

Each per-item JSON is the raw `wbgetentities` response for that QID —
sufficient to rebuild the item via `wbeditentity` if recovery is ever
needed.
"""

import argparse
import datetime as dt
import json
import os
import sys
import time

try:
    import requests
except ImportError:
    sys.exit("Missing 'requests'.  pip3 install requests")


WIKIBASE = "https://hunterhouse.wikibase.cloud"
SPARQL   = f"{WIKIBASE}/query/sparql"
API      = f"{WIKIBASE}/w/api.php"

USER_AGENT = "HunterHouseBackup/1.0 (backup_metadata; bturep)"

# Enumerate every item that carries both a P2 (archive ID) and a P79
# (source collection) — same gate the live browser uses, so the snapshot
# matches what the public site exposes. Vocab/people/institutions are
# excluded here on purpose; they're picked up via the one-hop walk below.
CATALOGUE_QUERY = """
PREFIX wdt: <https://hunterhouse.wikibase.cloud/prop/direct/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?item ?archId ?srcLabel WHERE {
  ?item wdt:P2 ?archId .
  ?item wdt:P79 ?src .
  OPTIONAL { ?src rdfs:label ?srcLabel . FILTER(LANG(?srcLabel)="en") }
}
ORDER BY ?archId
"""


# ─────────────────────────── transport ──────────────────────────────────────
def sparql(query):
    r = requests.get(SPARQL, params={"query": query, "format": "json"},
                     headers={"Accept": "application/sparql-results+json",
                              "User-Agent": USER_AGENT})
    r.raise_for_status()
    return r.json()["results"]["bindings"]


def wbgetentities(ids, *, kind="item", batch=50, pause=0.1):
    """Fetch entities in batches of up to 50. Returns {id: entity_json}."""
    out = {}
    ids = list(ids)
    for i in range(0, len(ids), batch):
        chunk = ids[i:i + batch]
        r = requests.get(API, params={
            "action": "wbgetentities",
            "ids": "|".join(chunk),
            "format": "json",
        }, headers={"User-Agent": USER_AGENT})
        r.raise_for_status()
        data = r.json()
        if "error" in data:
            raise RuntimeError(f"wbgetentities error: {data['error']}")
        out.update(data.get("entities", {}))
        # Be polite to a small public Wikibase instance.
        if i + batch < len(ids):
            time.sleep(pause)
    return out


# ─────────────────────────── walk + grouping ────────────────────────────────
def referenced_qids(entity):
    """Yield every QID referenced in an entity's wikibase-item claims."""
    out = set()
    for _pid, statements in (entity.get("claims") or {}).items():
        for st in statements:
            ms = st.get("mainsnak", {})
            if ms.get("datatype") != "wikibase-item":
                continue
            dv = ms.get("datavalue", {}).get("value", {})
            qid = dv.get("id")
            if qid:
                out.add(qid)
    return out


def referenced_pids(entity):
    """Yield every PID this entity uses in its claims."""
    return set((entity.get("claims") or {}).keys())


def collection_of(arch_id):
    """HH-HHC-0044 → HHC. Defensive against malformed IDs."""
    parts = arch_id.split("-")
    return parts[1] if len(parts) >= 3 else "UNKNOWN"


# ─────────────────────────── main ───────────────────────────────────────────
def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=None,
                    help="output dir (default: data/snapshots/wikibase_full_YYYYMMDD/)")
    ap.add_argument("--no-properties", action="store_true",
                    help="skip the P-entity dump (catalogue + vocab only)")
    args = ap.parse_args()

    today = dt.date.today().strftime("%Y%m%d")
    out_dir = os.path.abspath(args.out or f"data/snapshots/wikibase_full_{today}")
    os.makedirs(out_dir, exist_ok=True)
    print(f"→ output → {out_dir}/")

    # 1. enumerate catalogue items
    print(f"→ SPARQL: enumerating catalogue items …")
    rows = sparql(CATALOGUE_QUERY)
    items = []  # [(qid, archId, collection), ...]
    for row in rows:
        qid = row["item"]["value"].rsplit("/", 1)[-1]
        arch_id = row["archId"]["value"]
        items.append((qid, arch_id, collection_of(arch_id)))
    print(f"  found {len(items)} catalogue items")
    cat_qids = [q for q, _, _ in items]

    # 2. fetch the catalogue entities
    print(f"→ wbgetentities: catalogue items …")
    entities = wbgetentities(cat_qids)
    print(f"  retrieved {len(entities)} entities")
    if len(entities) != len(cat_qids):
        missing = set(cat_qids) - set(entities)
        print(f"  ⚠ {len(missing)} entities missing from response: {sorted(missing)[:5]}…")

    # 3. one-hop walk: every QID referenced in those items
    referenced = set()
    used_pids  = set()
    for ent in entities.values():
        referenced.update(referenced_qids(ent))
        used_pids.update(referenced_pids(ent))
    referenced -= set(cat_qids)
    print(f"→ walked references: {len(referenced)} vocab/person/institution items, "
          f"{len(used_pids)} properties in use")

    # 4. fetch the referenced entities (vocab, people, institutions)
    if referenced:
        print(f"→ wbgetentities: referenced items …")
        ref_entities = wbgetentities(sorted(referenced))
        entities.update(ref_entities)
        print(f"  retrieved {len(ref_entities)} referenced entities")

    # 5. fetch property definitions
    properties = {}
    if used_pids and not args.no_properties:
        print(f"→ wbgetentities: properties …")
        properties = wbgetentities(sorted(used_pids))
        print(f"  retrieved {len(properties)} properties")

    # 6. write sidecars
    print(f"→ writing per-item JSON sidecars …")
    per_collection = {}
    for qid, arch_id, coll in items:
        ent = entities.get(qid)
        if not ent:
            continue
        coll_dir = os.path.join(out_dir, coll)
        os.makedirs(coll_dir, exist_ok=True)
        with open(os.path.join(coll_dir, f"{arch_id}.json"), "w") as f:
            json.dump(ent, f, indent=2, ensure_ascii=False, sort_keys=True)
        per_collection[coll] = per_collection.get(coll, 0) + 1

    ref_dir = os.path.join(out_dir, "_referenced")
    os.makedirs(ref_dir, exist_ok=True)
    ref_written = 0
    for qid in sorted(referenced):
        ent = entities.get(qid)
        if not ent:
            continue
        with open(os.path.join(ref_dir, f"{qid}.json"), "w") as f:
            json.dump(ent, f, indent=2, ensure_ascii=False, sort_keys=True)
        ref_written += 1

    prop_written = 0
    if properties:
        prop_dir = os.path.join(out_dir, "_properties")
        os.makedirs(prop_dir, exist_ok=True)
        for pid, ent in properties.items():
            with open(os.path.join(prop_dir, f"{pid}.json"), "w") as f:
                json.dump(ent, f, indent=2, ensure_ascii=False, sort_keys=True)
            prop_written += 1

    # 7. manifest
    manifest = {
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "wikibase": WIKIBASE,
        "script": "scripts/backup_metadata.py",
        "totals": {
            "catalogue_items": sum(per_collection.values()),
            "referenced_items": ref_written,
            "properties": prop_written,
            "grand_total": sum(per_collection.values()) + ref_written + prop_written,
        },
        "per_collection": dict(sorted(per_collection.items())),
        "note": (
            "Local-only metadata backup — first half of ARCHITECTURE.md "
            "§11.1 HIGH. Each per-item JSON is the raw wbgetentities "
            "response for that QID, sufficient to rebuild the item via "
            "wbeditentity if the Wikibase Cloud instance is lost. R2 "
            "sidecar mirror + per-ingest sidecar writes still pending."
        ),
    }
    with open(os.path.join(out_dir, "_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False, sort_keys=True)

    # 8. summary
    print()
    print(f"✓ done")
    print(f"  {sum(per_collection.values())} catalogue items "
          f"(by collection: {dict(sorted(per_collection.items()))})")
    print(f"  {ref_written} referenced items (vocab / people / institutions)")
    print(f"  {prop_written} properties")
    print(f"  → {out_dir}/")
    print(f"  manifest: {out_dir}/_manifest.json")


if __name__ == "__main__":
    main()
