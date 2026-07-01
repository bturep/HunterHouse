import os, sys, json, time, subprocess, hashlib, requests, shutil
sys.path.insert(0,"scripts"); from _wikibase import WikibaseSession
from PIL import Image, ExifTags
_DTO={v:k for k,v in ExifTags.TAGS.items()}["DateTimeOriginal"]
KEEP="/Users/brandonpoole/Downloads/high resolution finished/Keep"
R2="hh-r2:hunter-house-archive"; COLL="eric-gesinger-collection"
PUB="https://archive.hunterhousefoundation.com/"+COLL; WORK="/tmp/hh_cb"; CAL="http://www.wikidata.org/entity/Q1985727"
TIERS={"_thumb.jpg":(600,75),"_prev.jpg":(2000,82),"_large.jpg":(3840,85)}
MAP={"HH-EGC-0040":"32-GesingerInteriors_channel chair.jpg","HH-EGC-0041":"34-GesingerInteriors_channel chair_ Living room.jpg",
"HH-EGC-0042":"43-GesingerInteriors_channel chair.jpg","HH-EGC-0043":"44-GesingerInteriors_channel chair.jpg","HH-EGC-0044":"45-GesingerInteriors_channel chair.jpg",
"HH-EGC-0046":"01-GesingerInteriors dinig room.jpg","HH-EGC-0047":"04-GesingerInteriors_dinig room.jpg","HH-EGC-0048":"07-GesingerInteriors_dinig room.jpg",
"HH-EGC-0049":"13-GesingerInteriors_dinig room.jpg","HH-EGC-0050":"17-GesingerInteriors_dinig room.jpg","HH-EGC-0051":"20-GesingerInteriors_dinig room.jpg",
"HH-EGC-0052":"21-GesingerInteriors_dinig room.jpg","HH-EGC-0053":"25-GesingerInteriors_dinig room.jpg","HH-EGC-0054":"26-GesingerInteriors_dinig room.jpg",
"HH-EGC-0055":"29-GesingerInteriors_dining room.jpg","HH-EGC-0056":"27-GesingerInteriors_bathroom.jpg","HH-EGC-0057":"28-GesingerInteriors_bathroom.jpg"}
def run(c): return subprocess.run(c,capture_output=True,text=True)
def sips(s,d,px,q):
    try: w,h=Image.open(s).size; px=min(px,max(w,h))
    except: pass
    subprocess.run(["sips","-Z",str(px),"-m","/System/Library/ColorSync/Profiles/sRGB Profile.icc","-s","format","jpeg","-s","formatOptions",str(q),s,"--out",d],check=True,capture_output=True)
def day(p):
    try: v=(Image.open(p)._getexif() or {}).get(_DTO)
    except: v=None
    return v[:10].replace(":","-") if v else None
wb=WikibaseSession(user_agent="HunterHouseBot/1.0 (egc-cachebust)")
def post(a,**k):
    for i in range(5):
        r=wb.post(a,**k)
        if r.get("success"): return r
        time.sleep(1.3*(i+1))
    raise SystemExit(f"{a} FAIL {r.get('error')}")
ents=wb.get("wbgetentities",ids="|".join(f"Q{n}" for n in range(588,616)),props="claims")["entities"]
byid={}
for q,e in ents.items():
    p2=e["claims"].get("P2")
    if not p2: continue
    idv=p2[0]["mainsnak"]["datavalue"]["value"]
    if idv in MAP:
        byid[idv]=dict(qid=q,masterfn=e["claims"]["P95"][0]["mainsnak"]["datavalue"]["value"].rsplit("/",1)[-1],
                       p95=e["claims"]["P95"][0]["id"],p96=e["claims"]["P96"][0]["id"],p82=(e["claims"].get("P82") or [{}])[0].get("id"))
os.makedirs(WORK,exist_ok=True)
for idv,src in MAP.items():
    m=byid[idv]; old=m["masterfn"][:-4]; new=old+"r"; sp=os.path.join(KEEP,src)  # cache-bust suffix
    run(["rclone","copyto",sp,f"{R2}/{COLL}/masters/{new}.jpg"])
    for suf,(px,q) in TIERS.items():
        o=os.path.join(WORK,new+suf); sips(sp,o,px,q)
        fol={"_thumb.jpg":"thumbs","_prev.jpg":"previews","_large.jpg":"large"}[suf]
        run(["rclone","copyto",o,f"{R2}/{COLL}/{fol}/{new}{suf}"])
    post("wbsetclaimvalue",claim=m["p95"],snaktype="value",value=json.dumps(f"{PUB}/masters/{new}.jpg"))
    post("wbsetclaimvalue",claim=m["p96"],snaktype="value",value=json.dumps(f"{PUB}/previews/{new}_prev.jpg"))
    d=day(sp)
    if m["p82"]:
        post("wbsetclaimvalue",claim=m["p82"],snaktype="value",value=json.dumps({"time":(f"+{d}T00:00:00Z" if d else "+2023-00-00T00:00:00Z"),"timezone":0,"before":0,"after":0,"precision":(11 if d else 9),"calendarmodel":CAL}))
    for fol,suf in [("masters",".jpg"),("thumbs","_thumb.jpg"),("previews","_prev.jpg"),("large","_large.jpg")]:
        run(["rclone","deletefile",f"{R2}/{COLL}/{fol}/{old}{suf}"])
    print(f"  {idv}: {old} → {new}")
shutil.rmtree(WORK,ignore_errors=True)
print("done — verifying PLAIN urls (browser-equivalent)…")
time.sleep(3)
import collections
h=collections.defaultdict(list)
for idv in MAP:
    m=byid[idv]; new=m["masterfn"][:-4]+"r"
    d=requests.get(f"{PUB}/previews/{new}_prev.jpg",timeout=30).content
    h[hashlib.md5(d).hexdigest()[:10]].append(idv)
dups=[v for v in h.values() if len(v)>1]
print("PLAIN-URL dup check:", "⚠ "+str(dups) if dups else "✓ all 17 distinct on plain URLs")
