#!/usr/bin/env python3
"""
Repair: the EGC renumber shifts (2026-06-30) had unchecked `rclone moveto` calls
that collided, overwriting 3 images (0041=0042, 0046=0047, 0056=0057 went
byte-identical). Re-establish the three AFFECTED subject groups from the original
Keep/ sources so every ID carries a distinct, correct image. R2 custom domain is
cf-cache-status:DYNAMIC (not cached), so overwriting in place serves fresh.

Overwrites master + 3 sRGB tiers (clamped, never upscales) at each ID's current
filename; re-sets P82 from the source EXIF. Run once. --execute to write.
"""
import os, sys, json, time, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _wikibase import WikibaseSession
from PIL import Image, ExifTags
_DTO = {v:k for k,v in ExifTags.TAGS.items()}["DateTimeOriginal"]

EXECUTE = "--execute" in sys.argv
KEEP = "/Users/brandonpoole/Downloads/high resolution finished/Keep"
R2   = "hh-r2:hunter-house-archive"; COLL="eric-gesinger-collection"
WORK = "/tmp/hh_egc_reupload"
CAL  = "http://www.wikidata.org/entity/Q1985727"
TIERS = {"_thumb.jpg":(600,75), "_prev.jpg":(2000,82), "_large.jpg":(3840,85)}

# ID → original Keep/ source (subject groups, in order). Each ID a distinct file.
MAP = {
    # Channel Chair 0040–0044
    "HH-EGC-0040":"32-GesingerInteriors_channel chair.jpg",
    "HH-EGC-0041":"34-GesingerInteriors_channel chair_ Living room.jpg",
    "HH-EGC-0042":"43-GesingerInteriors_channel chair.jpg",
    "HH-EGC-0043":"44-GesingerInteriors_channel chair.jpg",
    "HH-EGC-0044":"45-GesingerInteriors_channel chair.jpg",
    # Dining Room 0046–0055
    "HH-EGC-0046":"01-GesingerInteriors dinig room.jpg",
    "HH-EGC-0047":"04-GesingerInteriors_dinig room.jpg",
    "HH-EGC-0048":"07-GesingerInteriors_dinig room.jpg",
    "HH-EGC-0049":"13-GesingerInteriors_dinig room.jpg",
    "HH-EGC-0050":"17-GesingerInteriors_dinig room.jpg",
    "HH-EGC-0051":"20-GesingerInteriors_dinig room.jpg",
    "HH-EGC-0052":"21-GesingerInteriors_dinig room.jpg",
    "HH-EGC-0053":"25-GesingerInteriors_dinig room.jpg",
    "HH-EGC-0054":"26-GesingerInteriors_dinig room.jpg",
    "HH-EGC-0055":"29-GesingerInteriors_dining room.jpg",
    # Powder Room 0056–0057
    "HH-EGC-0056":"27-GesingerInteriors_bathroom.jpg",
    "HH-EGC-0057":"28-GesingerInteriors_bathroom.jpg",
}

def run(c): return subprocess.run(c, capture_output=True, text=True)
def sips(src,dst,px,q):
    try:
        w,h=Image.open(src).size; px=min(px,max(w,h))   # never upscale
    except Exception: pass
    subprocess.run(["sips","-Z",str(px),"-m","/System/Library/ColorSync/Profiles/sRGB Profile.icc",
        "-s","format","jpeg","-s","formatOptions",str(q),src,"--out",dst],check=True,capture_output=True)
def exif_day(p):
    try: v=(Image.open(p)._getexif() or {}).get(_DTO)
    except Exception: v=None
    return v[:10].replace(":","-") if v else None

def main():
    wb=WikibaseSession(user_agent="HunterHouseBot/1.0 (egc-reupload)")
    def post(a,**k):
        for i in range(5):
            r=wb.post(a,**k)
            if r.get("success"): return r
            time.sleep(1.3*(i+1))
        raise SystemExit(f"{a} FAILED: {r.get('error')}")
    # fetch qid, master filename, P82 claim id per ID
    ents=wb.get("wbgetentities", ids="|".join(f"Q{n}" for n in range(588,616)), props="claims")["entities"]
    byid={}
    for q,e in ents.items():
        p2=e["claims"].get("P2")
        if not p2: continue
        idv=p2[0]["mainsnak"]["datavalue"]["value"]
        if idv in MAP:
            byid[idv]=dict(qid=q, master=e["claims"]["P95"][0]["mainsnak"]["datavalue"]["value"].rsplit("/",1)[-1],
                           p82=(e["claims"].get("P82") or [{}])[0].get("id"))
    print(f"{'EXECUTE' if EXECUTE else 'DRY'} — re-upload {len(MAP)} images\n")
    for idv,src in MAP.items():
        p=os.path.join(KEEP,src); ok=os.path.isfile(p)
        m=byid.get(idv,{}); day=exif_day(p)
        print(f"  {idv} ← {src[:36]:36} {'OK' if ok else 'MISSING!'}  P82={day or '2023'}  → {m.get('master','?')}")
        if not ok: raise SystemExit("source missing")
    if not EXECUTE:
        print("\nDRY — re-run with --execute."); return
    os.makedirs(WORK,exist_ok=True)
    import shutil
    for idv,src in MAP.items():
        m=byid[idv]; base=m["master"][:-4]; sp=os.path.join(KEEP,src)
        run(["rclone","copyto",sp,f"{R2}/{COLL}/masters/{m['master']}"])
        for suf,(px,q) in TIERS.items():
            out=os.path.join(WORK,base+suf); sips(sp,out,px,q)
            folder={"_thumb.jpg":"thumbs","_prev.jpg":"previews","_large.jpg":"large"}[suf]
            run(["rclone","copyto",out,f"{R2}/{COLL}/{folder}/{base}{suf}"])
        day=exif_day(sp)
        if m["p82"]:
            val={"time":(f"+{day}T00:00:00Z" if day else "+2023-00-00T00:00:00Z"),"timezone":0,
                 "before":0,"after":0,"precision":(11 if day else 9),"calendarmodel":CAL}
            post("wbsetclaimvalue", claim=m["p82"], snaktype="value", value=json.dumps(val))
        print(f"  {idv} ✓")
    shutil.rmtree(WORK,ignore_errors=True)
    print("\nDONE — re-hash to verify, then regen gallery/pages/snapshot.")

if __name__=="__main__": main()
