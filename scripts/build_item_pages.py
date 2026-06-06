#!/usr/bin/env python3
"""
Generate per-item static permalink pages at  archive/<ARCH_ID>.html.

WHY: browse.html is a JavaScript single-page app — great as an interactive tool,
but its per-item views live behind ?id= query params that search engines index
poorly, and there was no stable, citable URL per archive item (the gap noted in
the discoverability backlog, and the natural target for the Wikidata P973
backlinks). These static pages are the crawlable, citable front door for each
item; each links into browse.html?id=… for the full interactive experience.

DATA: reuses build_catalogue_snapshot's helpers so the pages are built from the
exact same SPARQL the browser runs (no second query that could drift). One item
spans several SPARQL rows (multi-value areas / drawing-types / builders);
bindings_to_csv_rows() collapses them to one dict per item — the same shape used
for catalogue.csv.

STYLING: self-contained dark page in the browse.html palette + type tokens (the
same "browse.html dark palette" gallery.html/index.html use), so an item page
reads as a single browse.html record lifted out as a standalone page.

OUTPUT: writes archive/<ID>.html for every item, and regenerates sitemap.xml
(static pages + every item) so new items are discoverable. Idempotent — unchanged
items produce byte-identical files (no git churn); only changed/new pages diff.

USAGE:
  python3 scripts/build_item_pages.py                 # all items + sitemap
  python3 scripts/build_item_pages.py --one HH-CAA-0018   # just that page (+ sitemap)
  python3 scripts/build_item_pages.py --query-from next.html
Read-only on Wikibase; the only writes are local files in the repo.

INTAKE: each ingest script calls this best-effort at the end (see the call in
ingest_item.py / ingest_publication.py / batch_ingest_*). NOTE the Wikibase Query
Service (SPARQL) lags item creation by up to a minute, so a brand-new item may
not appear until the next run — re-run this (or the session-end full rebuild)
once WDQS catches up. Same lag applies to build_catalogue_snapshot.py.
"""

import os
import re
import sys
import json
import html as _html

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from build_catalogue_snapshot import load_catalogue_query, sparql, bindings_to_csv_rows  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(REPO, "archive")
SITE = "https://hunterhouse.org"
WIKIBASE = "https://hunterhouse.wikibase.cloud"
DEFAULT_QUERY_SOURCE = os.path.join(REPO, "browse.html")   # the live query
HUNTER_QID = "Q139959908"   # Richard Hunter on Wikidata (for schema sameAs)
HUNTER_NAMES = {"Richard Hunter", "Richard Morrow Hunter"}
FALLBACK_OG = ("https://archive.hunterhousefoundation.com/canadian-architecture-archive/"
               "previews/HH-CAA-0007_OG_Build_1970_Scheme_1_1of3_1970-08-25_prev.jpg")

# Static site URLs for the sitemap (kept here so the generator owns the whole
# sitemap; mirror of the hand-written set). (path, priority, changefreq)
STATIC_PAGES = [
    ("", "1.0", "monthly"),
    ("browse.html", "0.9", "weekly"),
    ("gallery.html", "0.7", "monthly"),
    ("richard-hunter.html", "0.8", "monthly"),
    ("the-house.html", "0.7", "monthly"),
    ("archive.html", "0.6", "monthly"),
    ("about.html", "0.6", "monthly"),
]

# ── browse.html dark palette + type (self-contained; no light.css dependency) ─
CSS = """
  :root{
    --bg:#1a1816; --bg2:#201e1a; --fg:#f0ede6;
    --muted:rgba(240,237,230,0.55); --hint:rgba(240,237,230,0.34);
    --line:rgba(240,237,230,0.13); --accent:#c4826e;
    --sans:"Inter Tight",-apple-system,Helvetica,Arial,sans-serif;
    --mono:"JetBrains Mono","SF Mono",Menlo,monospace;
  }
  *{box-sizing:border-box;margin:0;padding:0;-webkit-tap-highlight-color:transparent}
  html,body{background:var(--bg)}
  body{font-family:var(--sans);color:var(--fg);line-height:1.55;
    -webkit-font-smoothing:antialiased;font-weight:300}
  a{color:inherit}
  .wrap{max-width:880px;margin:0 auto;padding:0 28px}

  header.top{display:flex;align-items:center;justify-content:space-between;
    padding:18px 28px;border-bottom:1px solid var(--line);max-width:980px;margin:0 auto}
  header.top .mark{font-size:14px;letter-spacing:0.02em;text-decoration:none}
  header.top .mark .dim{color:var(--muted)}
  header.top nav a{font-family:var(--mono);font-size:10.5px;letter-spacing:0.1em;
    text-transform:uppercase;color:var(--muted);text-decoration:none;margin-left:18px}
  header.top nav a:hover,header.top nav a.on{color:var(--fg)}

  main{padding:48px 0 0}
  .eyebrow{font-family:var(--mono);font-size:11px;letter-spacing:0.2em;
    text-transform:uppercase;color:var(--accent);margin-bottom:14px}
  h1{font-weight:300;font-size:30px;letter-spacing:0.004em;line-height:1.18;margin-bottom:12px}
  .deck{font-family:var(--mono);font-size:11.5px;letter-spacing:0.06em;
    text-transform:uppercase;color:var(--muted);margin-bottom:36px}

  figure.plate{margin:0 0 14px;background:var(--bg2);border:1px solid var(--line);
    border-radius:2px;padding:26px;text-align:center}
  figure.plate img{max-width:100%;max-height:70vh;height:auto;display:inline-block}
  .pcap{display:flex;gap:14px;flex-wrap:wrap;margin-top:18px;font-family:var(--mono);
    font-size:10px;letter-spacing:0.06em;color:var(--hint);text-transform:uppercase}
  .pcap .id{color:var(--accent)}

  .lead{font-size:15.5px;color:var(--muted);max-width:62ch;margin:30px 0 8px}

  .sec-label{font-family:var(--mono);font-size:10px;letter-spacing:0.18em;
    text-transform:uppercase;color:var(--hint);margin:44px 0 16px;
    padding-bottom:9px;border-bottom:1px solid var(--line)}
  dl.rec{display:grid;grid-template-columns:170px 1fr;gap:2px 22px;font-size:14.5px}
  dl.rec dt{font-family:var(--mono);font-size:10px;letter-spacing:0.1em;
    text-transform:uppercase;color:var(--hint);padding:9px 0;align-self:start}
  dl.rec dd{color:var(--fg);padding:9px 0;border-bottom:1px solid var(--line)}
  dl.rec dt{border-bottom:1px solid var(--line)}

  .cta{display:inline-block;font-family:var(--mono);font-size:12px;letter-spacing:0.06em;
    text-transform:uppercase;color:var(--accent);text-decoration:none;margin:8px 0}
  .cta:hover{color:var(--fg)}
  .data{font-family:var(--mono);font-size:10.5px;letter-spacing:0.06em;
    text-transform:uppercase;color:var(--muted);margin-top:14px}
  .data a{color:var(--muted);text-decoration:none;border-bottom:1px solid var(--line)}
  .data a:hover{color:var(--fg)}
  .data .sep{color:var(--hint);margin:0 8px}

  footer{margin-top:64px;border-top:1px solid var(--line);padding:40px 28px 64px;text-align:center}
  footer .mark-link{display:inline-block;width:108px;height:108px;
    background:var(--fg);opacity:0.74;
    -webkit-mask:url(../assets/hunter-mark.png) center/contain no-repeat;
            mask:url(../assets/hunter-mark.png) center/contain no-repeat}
  footer .foot-meta{font-family:var(--mono);font-size:10px;letter-spacing:0.14em;
    text-transform:uppercase;color:var(--hint);margin-top:18px;line-height:1.7}
  @media(max-width:600px){
    h1{font-size:24px}
    dl.rec{grid-template-columns:1fr;gap:0}
    dl.rec dt{border-bottom:none;padding-bottom:0}
    dl.rec dd{padding-top:2px;margin-bottom:8px}
    header.top nav a{margin-left:12px}
  }
"""


def esc(s):
    return _html.escape(str(s or ""), quote=True)


def title_case_type(t):
    return (t or "").strip().capitalize()


def derive_large(prev_url):
    if not prev_url:
        return ""
    if "/previews/" in prev_url and prev_url.endswith("_prev.jpg"):
        return prev_url.replace("/previews/", "/large/").replace("_prev.jpg", "_large.jpg")
    return prev_url


def schema_type(itype):
    t = (itype or "").lower()
    if "photograph" in t:
        return "Photograph"
    if "drawing" in t:
        return "VisualArtwork"
    if "publication" in t or "book" in t:
        return "Book"
    if "survey" in t or "map" in t or "plan" in t:
        return "Map"
    return "CreativeWork"


def date_clause(row):
    return f", {row['date']}" if row.get("date") else ""


def deck(row):
    parts = [p for p in (title_case_type(row.get("itemType")),
                         row.get("date"), row.get("sourceCollection")) if p]
    return " · ".join(parts)


def lead(row):
    coll = row.get("sourceCollection") or "the Hunter House archive"
    itl = (row.get("itemType") or "item").lower()
    return (f"This {itl} is held in {coll}{date_clause(row)}. It forms part of the "
            f"architectural archive of Richard Hunter (1930–2023), documenting his "
            f"residence at 203 Goward Road, Saanich, British Columbia.")


def description(row):
    itl = (row.get("itemType") or "item").lower()
    coll = row.get("sourceCollection") or "Hunter House archive"
    d = f"{row['label']} — {itl}, {coll}{date_clause(row)}. Hunter House Foundation archive ({row['archId']})."
    return d[:158]


def jsonld(row, page_url, img):
    obj = {
        "@context": "https://schema.org",
        "@type": schema_type(row.get("itemType")),
        "name": row["label"],
        "identifier": row["archId"],
        "url": page_url,
        "isPartOf": {"@type": "Collection",
                     "name": row.get("sourceCollection") or "Richard Hunter fonds"},
        "contentLocation": {"@type": "Place",
                            "name": "203 Goward Road, Saanich, British Columbia"},
        "isAccessibleForFree": True,
    }
    if row.get("date"):
        obj["dateCreated"] = row["date"]
    if img:
        obj["image"] = img
    if row.get("medium"):
        obj["artMedium"] = row["medium"]
    if row.get("rights"):
        obj["copyrightNotice"] = row["rights"]
    creator = row.get("creator")
    if creator:
        person = {"@type": "Person", "name": creator}
        if creator in HUNTER_NAMES:
            person["sameAs"] = f"https://www.wikidata.org/wiki/{HUNTER_QID}"
        obj["creator"] = person
    return json.dumps(obj, ensure_ascii=False, indent=2)


# Fields shown in the catalogue-record grid, in order. (label, row-key)
REC_FIELDS = [
    ("Date", "date"),
    ("Collection", "sourceCollection"),
    ("Held by", "heldBy"),
    ("Phase", "phase"),
    ("Type", "itemType"),
    ("Drawing type", "drawTypes"),
    ("Category", "categories"),
    ("Areas", "areas"),
    ("Creator", "creator"),
    ("Designed by", "designedBy"),
    ("Built by", "builtBy"),
    ("Built status", "builtStatus"),
    ("Use", "use"),
    ("Medium", "medium"),
    ("Scale", "scale"),
    ("Location", "location"),
    ("Rights", "rights"),
]


def render_page(row):
    aid = row["archId"]
    title = row["label"] or aid
    page_url = f"{SITE}/archive/{aid}.html"
    img = row.get("image") or ""
    full = row.get("master") or derive_large(img) or img
    og_img = img or FALLBACK_OG
    desc = description(row)
    alt = f"{title} ({aid}) — {(row.get('itemType') or 'item').lower()}, {row.get('sourceCollection') or 'Hunter House archive'}"

    # Catalogue grid (present fields only; Held-by suppressed when == collection).
    rows_html = []
    for label, key in REC_FIELDS:
        v = row.get(key)
        if not v:
            continue
        if key == "heldBy" and v == row.get("sourceCollection"):
            continue
        disp = title_case_type(v) if key == "itemType" else v
        rows_html.append(f"      <dt>{esc(label)}</dt><dd>{esc(disp)}</dd>")
    grid = "\n".join(rows_html)

    # Image block (omitted for stub items with no preview).
    if img:
        fig = (
            '    <figure class="plate">\n'
            f'      <a href="{esc(full)}" target="_blank" rel="noopener">'
            f'<img src="{esc(img)}" alt="{esc(alt)}" loading="lazy"></a>\n'
            '      <figcaption class="pcap">'
            f'<span class="id">{esc(aid)}</span>'
            f'<span>{esc(title)}</span>'
            + (f'<span>{esc(row["date"])}</span>' if row.get("date") else '')
            + '</figcaption>\n'
            '    </figure>\n'
        )
    else:
        fig = ""

    # Data-layer links.
    qid = row.get("qid")
    data_bits = []
    if qid:
        data_bits.append(f'<a href="{WIKIBASE}/wiki/Item:{qid}">Wikibase item</a>')
        data_bits.append(f'<a href="{WIKIBASE}/wiki/Special:EntityData/{qid}.json">JSON</a>')
    if row.get("archiveLink"):
        data_bits.append(f'<a href="{esc(row["archiveLink"])}" target="_blank" rel="noopener">Finding aid →</a>')
    data_html = '<span class="sep">·</span>'.join(data_bits)

    parts = []
    parts.append("<!doctype html>")
    parts.append('<html lang="en">')
    parts.append("<head>")
    parts.append('<meta charset="utf-8">')
    parts.append(f"<title>{esc(title)} ({esc(aid)}) — Hunter House Foundation</title>")
    parts.append('<meta name="viewport" content="width=device-width,initial-scale=1">')
    parts.append(f'<meta name="description" content="{esc(desc)}">')
    parts.append(f'<link rel="canonical" href="{page_url}">')
    parts.append('<meta property="og:type" content="article">')
    parts.append('<meta property="og:site_name" content="Hunter House Foundation">')
    parts.append(f'<meta property="og:title" content="{esc(title)} ({esc(aid)})">')
    parts.append(f'<meta property="og:description" content="{esc(desc)}">')
    parts.append(f'<meta property="og:image" content="{esc(og_img)}">')
    parts.append(f'<meta property="og:url" content="{page_url}">')
    parts.append('<meta name="theme-color" content="#1a1816">')
    parts.append(f'<script type="application/ld+json">\n{jsonld(row, page_url, img)}\n</script>')
    parts.append('<link rel="manifest" href="../manifest.json">')
    parts.append('<link rel="apple-touch-icon" href="../assets/icon-180.png">')
    parts.append('<link rel="icon" type="image/png" href="../assets/icon-192.png">')
    parts.append('<link rel="preconnect" href="https://fonts.googleapis.com">')
    parts.append('<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>')
    parts.append('<link href="https://fonts.googleapis.com/css2?family=Inter+Tight:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">')
    parts.append(f"<style>{CSS}</style>")
    parts.append("</head>")
    parts.append("<body>")
    parts.append('<header class="top">')
    parts.append('  <a class="mark" href="../index.html">Hunter House <span class="dim">Foundation</span></a>')
    parts.append('  <nav><a href="../richard-hunter.html">Hunter</a><a href="../the-house.html">House</a>'
                 '<a href="../archive.html" class="on">Archive</a><a href="../browse.html">Browse</a></nav>')
    parts.append("</header>")
    parts.append('<main class="wrap">')
    parts.append(f'  <p class="eyebrow">{esc(aid)}</p>')
    parts.append(f"  <h1>{esc(title)}</h1>")
    parts.append(f'  <p class="deck">{esc(deck(row))}</p>')
    if fig:
        parts.append(fig.rstrip("\n"))
    parts.append(f'  <p class="lead">{esc(lead(row))}</p>')
    parts.append('  <div class="sec-label">Catalogue record</div>')
    parts.append('  <dl class="rec">')
    parts.append(grid)
    parts.append("  </dl>")
    parts.append('  <div class="sec-label">In the archive</div>')
    parts.append(f'  <p><a class="cta" href="../browse.html?id={esc(aid)}">View in the interactive archive →</a></p>')
    if data_html:
        parts.append(f'  <p class="data">{data_html}</p>')
    parts.append("</main>")
    parts.append("<footer>")
    parts.append('  <a class="mark-link" href="../browse.html" aria-label="Browse the full archive"></a>')
    parts.append('  <p class="foot-meta">Hunter House Foundation<br>203 Goward Road · Saanich · British Columbia</p>')
    parts.append("</footer>")
    parts.append("<script>if('serviceWorker' in navigator)navigator.serviceWorker.register('../sw.js');</script>")
    parts.append("</body>")
    parts.append("</html>")
    return "\n".join(parts) + "\n"


def write_sitemap(rows):
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             "<!-- Auto-generated by scripts/build_item_pages.py — static pages + every",
             "     per-item permalink. Re-run that script after catalogue changes. -->",
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for path, prio, freq in STATIC_PAGES:
        lines += ["  <url>",
                  f"    <loc>{SITE}/{path}</loc>",
                  f"    <changefreq>{freq}</changefreq>",
                  f"    <priority>{prio}</priority>",
                  "  </url>"]
    for row in sorted(rows, key=lambda r: r["archId"]):
        lines += ["  <url>",
                  f"    <loc>{SITE}/archive/{row['archId']}.html</loc>",
                  "    <changefreq>monthly</changefreq>",
                  "    <priority>0.6</priority>",
                  "  </url>"]
    lines.append("</urlset>")
    with open(os.path.join(REPO, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def main(argv):
    only = None
    if "--one" in argv:
        i = argv.index("--one")
        only = argv[i + 1] if i + 1 < len(argv) else None
        if not only:
            sys.exit("--one needs an ARCH_ID, e.g. --one HH-CAA-0018")
    query_src = DEFAULT_QUERY_SOURCE
    if "--query-from" in argv:
        query_src = argv[argv.index("--query-from") + 1]

    query = load_catalogue_query(query_src)
    bindings = sparql(query)
    rows = bindings_to_csv_rows(bindings)
    if not rows:
        sys.exit("✗ no items returned from SPARQL — aborting (won't wipe pages).")

    os.makedirs(OUT_DIR, exist_ok=True)

    targets = rows
    if only:
        targets = [r for r in rows if r["archId"] == only]
        if not targets:
            sys.exit(f"✗ {only} not found in the catalogue (WDQS lag? try again shortly).")

    written = 0
    for row in targets:
        path = os.path.join(OUT_DIR, f"{row['archId']}.html")
        html_str = render_page(row)
        # Skip the write if unchanged (keeps git diffs clean on full rebuilds).
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                if f.read() == html_str:
                    continue
        with open(path, "w", encoding="utf-8") as f:
            f.write(html_str)
        written += 1

    # Sitemap always reflects the full catalogue.
    write_sitemap(rows)

    scope = f"--one {only}" if only else f"all {len(rows)} items"
    print(f"✓ item pages ({scope}): {written} file(s) written/updated in archive/, "
          f"{len(rows)} URLs in sitemap.xml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
