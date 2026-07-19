#!/usr/bin/env python3
"""
One-shot cleanup of the EGC photo batch (2026-06-30), same day as ingest:
  1. Rotate the Stool drawing HH-EGC-0031 (Q587) 90° CCW → P144 "270".
  2. Retire near-duplicate Stool photo HH-EGC-0041 (Q597) — clear item + R2 files.
  3. Renumber the remaining 27 photos into subject-contiguous IDs 0032–0058
     (Stool ×5, Dining Room Chair ×4, Channel Chair ×5, Ottoman ×1,
      Dining Room ×10, Powder Room ×2), renaming R2 files to match and
     updating P2 / P95 / P96 / description.

R2 rename is two-phase (via a _reorder/ staging subfolder per tier) because the
map is a permutation with collisions. Safe to re-run: identity moves are skipped
and rclone moveto is a no-op if the source is already gone.

Dry-run by default; --execute performs writes. Regenerate item pages + snapshot
AFTER (build_item_pages.py + build_catalogue_snapshot.py --execute).
"""
import json, os, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wikibase import WikibaseSession

EXECUTE = "--execute" in sys.argv
R2   = "hh-r2:hunter-house-archive"
COLL = "eric-gesinger-collection"
PUB  = "https://archive.hunterhousefoundation.com"

ROTATE = ("Q587", "270")          # HH-EGC-0031 stool drawing, 90° CCW
DELETE = ("HH-EGC-0041", "Q597")  # near-dup stool (keep 0049)

# old archId → new archId (27 kept photos), grouped by subject
OLD2NEW = {
    # Stool (studio) → 0032–0036
    "HH-EGC-0042":"HH-EGC-0032","HH-EGC-0045":"HH-EGC-0033","HH-EGC-0047":"HH-EGC-0034",
    "HH-EGC-0049":"HH-EGC-0035","HH-EGC-0057":"HH-EGC-0036",
    # Dining Room Chair (studio) → 0037–0040
    "HH-EGC-0037":"HH-EGC-0037","HH-EGC-0040":"HH-EGC-0038","HH-EGC-0058":"HH-EGC-0039",
    "HH-EGC-0059":"HH-EGC-0040",
    # Channel Chair (living room) → 0041–0045
    "HH-EGC-0051":"HH-EGC-0041","HH-EGC-0052":"HH-EGC-0042","HH-EGC-0054":"HH-EGC-0043",
    "HH-EGC-0055":"HH-EGC-0044","HH-EGC-0056":"HH-EGC-0045",
    # Channel Chair Ottoman → 0046
    "HH-EGC-0053":"HH-EGC-0046",
    # Dining Room (interior) → 0047–0056
    "HH-EGC-0032":"HH-EGC-0047","HH-EGC-0033":"HH-EGC-0048","HH-EGC-0034":"HH-EGC-0049",
    "HH-EGC-0035":"HH-EGC-0050","HH-EGC-0036":"HH-EGC-0051","HH-EGC-0038":"HH-EGC-0052",
    "HH-EGC-0039":"HH-EGC-0053","HH-EGC-0043":"HH-EGC-0054","HH-EGC-0044":"HH-EGC-0055",
    "HH-EGC-0050":"HH-EGC-0056",
    # Powder Room (interior) → 0057–0058
    "HH-EGC-0046":"HH-EGC-0057","HH-EGC-0048":"HH-EGC-0058",
}

def qid_of(archid):                       # 0032→Q588 … 0059→Q615
    return "Q" + str(588 + int(archid[-4:]) - 32)

def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)

# tier folder → (subdir, filename suffix)
TIERS = [("masters",".jpg"),("thumbs","_thumb.jpg"),("previews","_prev.jpg"),("large","_large.jpg")]

def base_from_master_url(url):            # …/masters/HH-EGC-0037_DiningRoomChair_2023.jpg
    fn = url.rsplit("/",1)[-1]
    return fn[:-4] if fn.lower().endswith(".jpg") else fn  # strip .jpg → {id}_{slug}

def main():
    wb = WikibaseSession(user_agent="HunterHouseBot/1.0 (egc-renumber)")
    print(f"{'EXECUTE' if EXECUTE else 'DRY RUN'} — EGC photo renumber\n")

    # fetch claims for all kept + the delete target
    qids = [qid_of(o) for o in OLD2NEW] + [DELETE[1], ROTATE[0]]
    ents = wb.get("wbgetentities", ids="|".join(qids), props="claims")["entities"]

    def claim(ent, pid):
        cs = ent["claims"].get(pid, [])
        return cs[0] if cs else None

    # ── plan the per-item renames ───────────────────────────────────────────
    plan = []
    for old, new in sorted(OLD2NEW.items(), key=lambda kv: kv[1]):
        q = qid_of(old); e = ents[q]
        p95 = claim(e,"P95"); p96 = claim(e,"P96")
        oldbase = base_from_master_url(p95["mainsnak"]["datavalue"]["value"])
        slug = oldbase[len(old)+1:]                       # {id}_{slug} → slug
        newbase = f"{new}_{slug}"
        lbl = None
        plan.append(dict(old=old,new=new,qid=q,oldbase=oldbase,newbase=newbase,
                         p2=claim(e,"P2"),p95=p95,p96=p96,identity=(old==new)))
        print(f"  {old} → {new}  {q}  ({slug}){'  [identity]' if old==new else ''}")
    print(f"\n  rotate {ROTATE[0]} (HH-EGC-0031) → P144 {ROTATE[1]}")
    print(f"  retire {DELETE[0]} ({DELETE[1]}) + its 4 R2 files\n")

    if not EXECUTE:
        print("DRY RUN — re-run with --execute.")
        return

    # ── 1. rotate 0031 ──────────────────────────────────────────────────────
    e31 = ents[ROTATE[0]]
    if claim(e31,"P144"):
        wb.post("wbsetclaimvalue", claim=claim(e31,"P144")["id"], snaktype="value",
                value=json.dumps(ROTATE[1]))
    else:
        wb.post("wbcreateclaim", entity=ROTATE[0], property="P144", snaktype="value",
                value=json.dumps(ROTATE[1]))
    print(f"[1] rotated {ROTATE[0]} P144={ROTATE[1]}")

    # ── 2. retire 0041 ──────────────────────────────────────────────────────
    de = ents[DELETE[1]]
    delbase = base_from_master_url(claim(de,"P95")["mainsnak"]["datavalue"]["value"])
    for sub, suf in TIERS:
        run(["rclone","deletefile",f"{R2}/{COLL}/{sub}/{delbase}{suf}"])
    r = wb.post("delete", title=f"Item:{DELETE[1]}", reason="near-duplicate of HH-EGC-0049 (removed per Brandon)")
    if "error" in r:
        wb.post("wbeditentity", id=DELETE[1], clear=1,
                data=json.dumps({"descriptions":{"en":{"language":"en",
                "value":"retired — near-duplicate stool photo, superseded by HH-EGC-0035 (formerly 0049)"}}}))
        print(f"[2] {DELETE[1]} cleared (no delete right) + R2 files removed")
    else:
        print(f"[2] {DELETE[1]} deleted + R2 files removed")

    # ── 3a. R2 rename phase 1: old → _reorder/new ───────────────────────────
    movers = [p for p in plan if not p["identity"]]
    print(f"[3] R2 rename ({len(movers)} items, 2-phase)")
    for p in movers:
        for sub, suf in TIERS:
            run(["rclone","moveto",f"{R2}/{COLL}/{sub}/{p['oldbase']}{suf}",
                 f"{R2}/{COLL}/{sub}/_reorder/{p['newbase']}{suf}"])
    # ── 3b. phase 2: _reorder/new → new ─────────────────────────────────────
    for p in movers:
        for sub, suf in TIERS:
            run(["rclone","moveto",f"{R2}/{COLL}/{sub}/_reorder/{p['newbase']}{suf}",
                 f"{R2}/{COLL}/{sub}/{p['newbase']}{suf}"])
    print("    R2 files renamed")

    # ── 3c. Wikibase: P2 / P95 / P96 / description ──────────────────────────
    for p in movers:
        new = p["new"]
        newmaster = f"{PUB}/{COLL}/masters/{p['newbase']}.jpg"
        newprev   = f"{PUB}/{COLL}/previews/{p['newbase']}_prev.jpg"
        wb.post("wbsetclaimvalue", claim=p["p2"]["id"],  snaktype="value", value=json.dumps(new))
        wb.post("wbsetclaimvalue", claim=p["p95"]["id"], snaktype="value", value=json.dumps(newmaster))
        wb.post("wbsetclaimvalue", claim=p["p96"]["id"], snaktype="value", value=json.dumps(newprev))
        wb.post("wbsetdescription", id=p["qid"], language="en",
                value=f"photograph; EGC; {new}; 2023")
        print(f"    {p['old']} → {new}  {p['qid']} ✓")

    # ── 3d. sidecars for the renamed items (new id), drop stale old ones ─────
    here = os.path.dirname(__file__)
    for p in movers:
        subprocess.run(["python3", os.path.join(here,"sync_one_metadata.py"),
                        p["new"], "--execute","--quiet"], check=False)
        run(["rclone","deletefile",f"{R2}/{COLL}/metadata/{p['old']}.json"])
    run(["rclone","deletefile",f"{R2}/{COLL}/metadata/{DELETE[0]}.json"])
    print("\nDONE. Next: build_item_pages.py + build_catalogue_snapshot.py --execute")

if __name__ == "__main__":
    main()
