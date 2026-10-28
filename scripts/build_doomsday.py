#!/usr/bin/env python3
"""
Build (or refresh) the Hunter House doomsday copy on an external drive.

A self-contained, offline, read-only copy of the whole archive: every master
and tier from R2, the catalogue, the site, the repo's full history, and the
Frances Hunter letters. Opens on any machine with Python 3 via START.bat
(Windows) or start.command (Mac). Spec: claude-system/audits/
2026-09-09_HH-doomsday-copy-spec.md.

Re-runnable: each step only fetches what changed, so a refresh after a site
push or an ingest is quick. Re-run it whenever a new browse.html version ships
or masters are ingested.

Steps (each can be skipped):
  mirror   rclone copy of the public bucket -> <target>/r2/ (byte-true), then
           rclone check (size + MD5) and a listing -> fixity/
  site     git archive of HEAD -> <target>/site/ (tracked files only)
  repo     git bundle --all -> <target>/repo/HunterHouse.bundle
  wikibase backup_metadata.py -> <target>/wikibase/wikibase_full_YYYYMMDD/
  gated    the letters, via the Worker's /gated/* (needs HH_GATED_TOKEN in the
           environment, the researcher token); skipped with a note if unset
  tools    serve.py + launchers + README-FIRST.txt -> <target>/
  index    CATALOGUE.html + LETTERS.html: plain pages, no Python or server needed
  fixity   SHA-256 of every file -> fixity/manifest-YYYYMMDD.sha256

--copy-to FOLDER then syncs the finished folder to a second copy (K:) and runs
that copy's own verify.py against the manifest it carries.

Usage (PC):
    py -3 scripts/build_doomsday.py J:\\HH-ARCHIVE-DOOMSDAY --copy-to K:\\BACKUPS\\HH-ARCHIVE-DOOMSDAY
    # after a website (UI) change:
    py -3 scripts/build_doomsday.py J:\\HH-ARCHIVE-DOOMSDAY --only site repo tools index fixity --copy-to K:\\BACKUPS\\HH-ARCHIVE-DOOMSDAY
Mac:
    python3 scripts/build_doomsday.py /Volumes/HH-DOOMSDAY/HH-ARCHIVE-DOOMSDAY

Needs: rclone with the `hh-r2` remote (mirror step), git, network.
"""

import argparse
import datetime as dt
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tarfile
import urllib.parse
import urllib.request

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(REPO, "scripts", "doomsday")
BUCKET = "hh-r2:hunter-house-archive"
WORKER = "https://hhf-r2-browser.brandon-628.workers.dev"
STEPS = ["mirror", "site", "repo", "wikibase", "gated", "tools", "index", "fixity"]
TODAY = dt.date.today().strftime("%Y%m%d")


def say(msg):
    print("[doomsday] " + msg, flush=True)


def run(cmd, **kw):
    say("$ " + " ".join(cmd))
    return subprocess.run(cmd, check=True, **kw)


# -- steps -----------------------------------------------------------------

def step_mirror(t, stage=None):
    r2 = os.path.join(t, "r2")
    os.makedirs(r2, exist_ok=True)
    stats = ["--stats", "1m", "--stats-one-line"]
    if stage:
        # USB flash sticks crawl under parallel writes (measured 2026-10-27: a
        # Kingston DT 3.0 does 8 MB/s alone, <1 MB/s with six writers). So
        # download in parallel to a fast local disk, then copy onto the drive
        # one file at a time. sync, not copy: r2/ stays an exact mirror.
        # sync deletes anything in the stage folder that is not in the bucket,
        # so only ever sync into a folder this script created (marker file).
        os.makedirs(stage, exist_ok=True)
        marker = os.path.join(stage, ".hh-doomsday-stage")
        if os.listdir(stage) and not os.path.exists(marker):
            raise SystemExit("--stage folder is not empty and not a doomsday stage: " + stage)
        open(marker, "a").close()
        run(["rclone", "sync", BUCKET, stage, "--transfers", "8", "--checkers", "16",
             "--exclude", "/.hh-doomsday-stage"] + stats)
        run(["rclone", "sync", stage, r2, "--transfers", "1", "--checkers", "4",
             "--exclude", "/.hh-doomsday-stage"] + stats)
    else:
        run(["rclone", "copy", BUCKET, r2, "--transfers", "2", "--checkers", "8"] + stats)
    fx = os.path.join(t, "fixity")
    os.makedirs(fx, exist_ok=True)
    # The bucket listing with sizes + MD5 at build time (the remote's own record).
    with open(os.path.join(fx, "r2-listing-%s.json" % TODAY), "wb") as f:
        run(["rclone", "lsjson", "-R", "--files-only", "--hash", BUCKET], stdout=f)
    # Compare drive vs bucket. Multipart uploads carry no MD5, so rclone
    # falls back to size for those; the SHA-256 manifest is the drive's own check.
    rep = os.path.join(fx, "r2-check-%s.txt" % TODAY)
    with open(rep, "w", encoding="utf-8") as f:
        res = subprocess.run(["rclone", "check", BUCKET, r2, "--one-way"],
                             stdout=f, stderr=subprocess.STDOUT)
    if res.returncode != 0:
        raise SystemExit("rclone check found differences -- see " + rep)
    say("mirror verified against the bucket (" + rep + ")")


def git(*args):
    return subprocess.check_output(["git", "-C", REPO] + list(args)).decode().strip()


def step_site(t):
    site = os.path.join(t, "site")
    if os.path.isdir(site):
        shutil.rmtree(site)
    os.makedirs(site)
    tar = subprocess.check_output(["git", "-C", REPO, "archive", "--format=tar", "HEAD"])
    with tarfile.open(fileobj=io.BytesIO(tar)) as tf:
        tf.extractall(site, filter="data") if hasattr(tarfile, "data_filter") else tf.extractall(site)
    ver = re.search(r'const VERSION\s*=\s*"([^"]+)"',
                    open(os.path.join(site, "browse.html"), encoding="utf-8").read())
    info = {
        "built": dt.datetime.now().isoformat(timespec="seconds"),
        "commit": git("rev-parse", "HEAD"),
        "commit_date": git("log", "-1", "--format=%ci"),
        "branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "browse_version": ver.group(1) if ver else None,
    }
    with open(os.path.join(t, "BUILD-INFO.json"), "w", encoding="utf-8") as f:
        json.dump(info, f, indent=2)
    say("site exported at %s (browse %s)" % (info["commit"][:7], info["browse_version"]))


def step_repo(t):
    d = os.path.join(t, "repo")
    os.makedirs(d, exist_ok=True)
    out = os.path.join(d, "HunterHouse.bundle")
    tmp = out + ".tmp"
    run(["git", "-C", REPO, "bundle", "create", tmp, "--all"])
    os.replace(tmp, out)


def step_wikibase(t):
    out = os.path.join(t, "wikibase", "wikibase_full_" + TODAY)
    # UTF-8 stdout: the dump prints arrows, which a Windows cp1252 console can't encode.
    run([sys.executable, os.path.join(REPO, "scripts", "backup_metadata.py"), "--out", out],
        env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    # The consolidated snapshot, alongside, for anyone without the site.
    cat = os.path.join(t, "r2", "catalogue")
    if os.path.isdir(cat):
        for n in os.listdir(cat):
            shutil.copy2(os.path.join(cat, n), os.path.join(t, "wikibase", n))


def fetch(url, token):
    req = urllib.request.Request(url, headers={"X-Researcher-Token": token,
                                               "User-Agent": "hh-doomsday/1"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read()


def step_gated(t):
    g = os.path.join(t, "gated")
    os.makedirs(g, exist_ok=True)
    token = os.environ.get("HH_GATED_TOKEN", "").strip()
    if not token:
        with open(os.path.join(g, "NOT-YET.txt"), "w", encoding="utf-8") as f:
            f.write("The Frances Hunter letters are not on this drive yet.\n\n"
                    "Re-run the build with the researcher token set:\n"
                    "  PC:  $env:HH_GATED_TOKEN='<token>'; py -3 scripts/build_doomsday.py <target> --only gated tools fixity\n"
                    "  Mac: HH_GATED_TOKEN='<token>' python3 scripts/build_doomsday.py <target> --only gated tools fixity\n")
        say("gated: HH_GATED_TOKEN not set -- letters skipped (note left in gated/)")
        return
    data = fetch(WORKER + "/gated/letters", token)
    ds = json.loads(data)
    keys = set()
    for r in ds.get("records", []):
        pre = r.get("img_prefix")
        n = (r["pages"] if isinstance(r.get("pages"), int)
             else len(r.get("source_scans") or [])) or (1 if pre else 0)
        if pre:
            for k in range(n):
                keys.add("%s%02d_prev.jpg" % (pre, k + 1))
        for s in r.get("source_scans") or []:
            if isinstance(s, str) and s.startswith("gated/"):
                keys.add(s)
    got = miss = 0
    for key in sorted(keys):
        dest = os.path.join(g, "bucket", *key.split("/"))
        if os.path.isfile(dest) and os.path.getsize(dest) > 0:
            got += 1
            continue
        try:
            body = fetch(WORKER + "/gated/img?key=" + urllib.parse.quote(key, safe=""), token)
        except urllib.error.HTTPError as e:
            say("gated: %s -> HTTP %s" % (key, e.code))
            miss += 1
            continue
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as f:
            f.write(body)
        got += 1
    with open(os.path.join(g, "letters-dataset.json"), "wb") as f:
        f.write(data)
    note = os.path.join(g, "NOT-YET.txt")
    if os.path.exists(note):
        os.remove(note)
    say("gated: %d records, %d page images on drive, %d missing"
        % (len(ds.get("records", [])), got, miss))


def step_tools(t):
    for n in os.listdir(TOOLS):
        src = os.path.join(TOOLS, n)
        if os.path.isfile(src) and not n.startswith("."):
            shutil.copy2(src, os.path.join(t, n))
    say("server + launchers copied to drive root")


# -- index: plain HTML pages that open by double-click, no Python, no server --

R2_ORIGIN = "https://archive.hunterhousefoundation.com/"
COLL_ORDER = ["CAA", "HHC", "IHC", "EGC", "FRH"]

PAGE_CSS = """
:root{--paper:#faf8f4;--ink:#222;--soft:#6b665e;--rule:#ddd6cb;--link:#8a4b2a}
@media (prefers-color-scheme:dark){:root{--paper:#1c1b1a;--ink:#e8e4dc;--soft:#9a948a;--rule:#3a3734;--link:#d99a6c}}
body{background:var(--paper);color:var(--ink);font:15px/1.5 Georgia,serif;margin:0 auto;max-width:980px;padding:24px 16px 80px}
h1,h2,h3,.mono{font-family:Menlo,Consolas,"Courier New",monospace;letter-spacing:.04em}
h1{font-size:18px;text-transform:uppercase}h2{font-size:15px;text-transform:uppercase;border-bottom:1px solid var(--rule);padding-bottom:6px;margin-top:48px}
h3{font-size:14px;margin:0 0 4px}a{color:var(--link)}p.lede,.soft{color:var(--soft)}
.item{display:flex;gap:16px;padding:14px 0;border-bottom:1px solid var(--rule)}
.item img{width:140px;height:auto;flex:none;background:var(--rule)}
dl{display:grid;grid-template-columns:max-content 1fr;gap:2px 12px;margin:6px 0;font-size:13px}
dt{color:var(--soft)}dd{margin:0}.links{font-size:13px}
pre{white-space:pre-wrap;font:13px/1.5 Menlo,Consolas,monospace;background:rgba(127,127,127,.08);padding:12px}
.pages img{width:120px;margin:0 6px 6px 0}
@media (max-width:600px){.item{flex-direction:column}.item img{width:100%}}
"""


def _esc(s):
    import html
    return html.escape(str(s or ""), quote=True)


def _href(rel):
    return urllib.parse.quote(rel)


def _page(title, body):
    return ("<!doctype html>\n<html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
            "<title>%s</title><style>%s</style></head><body>%s</body></html>\n"
            % (_esc(title), PAGE_CSS, body))


def _dl(pairs):
    rows = "".join("<dt>%s</dt><dd>%s</dd>" % (_esc(k), _esc(v)) for k, v in pairs if v)
    return "<dl>%s</dl>" % rows if rows else ""


def step_index(t):
    import csv
    from collections import Counter, OrderedDict
    built = dt.date.today().isoformat()

    def local(url):
        if not url or not url.startswith(R2_ORIGIN):
            return None
        rel = "r2/" + urllib.parse.unquote(url[len(R2_ORIGIN):])
        return rel if os.path.isfile(os.path.join(t, *rel.split("/"))) else None

    def size(rel):
        b = os.path.getsize(os.path.join(t, *rel.split("/")))
        return "%.1f MB" % (b / 1e6) if b >= 1e6 else "%d KB" % (b // 1000)

    csv_path = os.path.join(t, "r2", "catalogue", "catalogue.csv")
    rows = list(csv.DictReader(open(csv_path, encoding="utf-8")))
    groups = OrderedDict((c, []) for c in COLL_ORDER)
    for r in sorted(rows, key=lambda r: r["archId"]):
        groups.setdefault(r["archId"].split("-")[1], []).append(r)
    toc, body = [], []
    for code, items in groups.items():
        if not items:
            continue
        name = Counter(r["sourceCollection"] for r in items).most_common(1)[0][0]
        toc.append('<li><a href="#%s">%s -- %s</a> <span class="soft">(%d)</span></li>'
                   % (code, code, _esc(name), len(items)))
        body.append('<h2 id="%s">%s -- %s</h2>' % (code, code, _esc(name)))
        for r in items:
            prev = local(r["image"])
            thumb = None
            if prev:
                tr = prev.replace("/previews/", "/thumbs/").replace("_prev.jpg", "_thumb.jpg")
                thumb = tr if os.path.isfile(os.path.join(t, *tr.split("/"))) else prev
            links = []
            if prev:
                links.append('<a href="%s">view image</a>' % _href(prev))
            m = local(r["master"])
            if m:
                links.append('<a href="%s">master (%s)</a>' % (_href(m), size(m)))
            ac = local(r["accessCopy"])
            if ac:
                links.append('<a href="%s">access copy (%s)</a>' % (_href(ac), size(ac)))
            if r["archiveLink"]:
                links.append('<a href="%s">holding archive (online)</a>' % _esc(r["archiveLink"]))
            body.append(
                '<div class="item" id="%s">%s<div><h3>%s &middot; %s</h3>%s<div class="links">%s</div></div></div>'
                % (_esc(r["archId"]),
                   '<a href="%s"><img loading="lazy" src="%s" alt=""></a>' % (_href(prev), _href(thumb)) if prev else "",
                   _esc(r["archId"]), _esc(r["label"]),
                   _dl([("date", r["date"]), ("type", r["itemType"]), ("drawing", r["drawTypes"]),
                        ("by", r["creator"]), ("designed by", r["designedBy"]), ("built by", r["builtBy"]),
                        ("medium", r["medium"]), ("phase", r["phase"]), ("areas", r["areas"]),
                        ("sheet", r["setPosition"]), ("held by", r["heldBy"]), ("location", r["location"]),
                        ("rights", r["rights"] or r["rightsUri"]), ("notes", r["notes"])]),
                   " &middot; ".join(links)))
    has_letters = os.path.isfile(os.path.join(t, "gated", "letters-dataset.json"))
    head = ('<h1>Hunter House Archive -- catalogue</h1>'
            '<p class="lede">Every object in the archive, %d in all, with links to the files on this drive. '
            'This page needs no program and no internet: it is plain HTML and works in any browser, on any machine. '
            'The full website (START.bat / start.command) is richer; this page is the fallback that should outlast it. '
            'Built %s from r2/catalogue/catalogue.csv.</p>' % (len(rows), built)
            + ('<p><a href="LETTERS.html">The Frances Hunter correspondence (confidential) &rarr;</a></p>' if has_letters else "")
            + "<ul>%s</ul>" % "".join(toc))
    with open(os.path.join(t, "CATALOGUE.html"), "w", encoding="utf-8") as f:
        f.write(_page("Hunter House Archive catalogue", head + "".join(body)))
    n_letters = 0
    if has_letters:
        ds = json.load(open(os.path.join(t, "gated", "letters-dataset.json"), encoding="utf-8"))
        recs = ds.get("records", [])
        n_letters = len(recs)
        out = []
        for r in recs:
            pre = r.get("img_prefix")
            n = r["pages"] if isinstance(r.get("pages"), int) else len(r.get("source_scans") or [])
            pages = []
            for k in range(n or 0):
                rel = "gated/bucket/%s%02d_prev.jpg" % (pre, k + 1) if pre else None
                if rel and os.path.isfile(os.path.join(t, *rel.split("/"))):
                    pages.append('<a href="%s"><img loading="lazy" src="%s" alt="page %d"></a>'
                                 % (_href(rel), _href(rel), k + 1))
            to = r.get("to")
            to = ", ".join(to) if isinstance(to, list) else to
            date = r.get("date") or ""
            if r.get("as_written"):
                date += ' (as written "%s")' % r["as_written"]
            out.append(
                '<div id="%s" style="padding:18px 0;border-bottom:1px solid var(--rule)"><h3>%s &middot; %s &rarr; %s</h3>%s%s%s%s</div>'
                % (_esc(r.get("id")), _esc(r.get("id")), _esc(r.get("from")), _esc(to),
                   _dl([("date", date), ("place", r.get("place_written")), ("form", r.get("doc_form")),
                        ("medium", r.get("medium")), ("leaves", r.get("leaves")),
                        ("subjects", "; ".join(r.get("subjects") or [])),
                        ("uncertain", "; ".join(
                            u if isinstance(u, str) else "%s (%s)" % (u.get("reading", ""), u.get("note", ""))
                            for u in r.get("uncertain") or []))]),
                   "<p>%s</p>" % _esc(r["summary"]) if r.get("summary") else "",
                   '<div class="pages">%s</div>' % "".join(pages) if pages else "",
                   "<pre>%s</pre>" % _esc(r["transcript"]) if r.get("transcript") else ""))
        lhead = ('<h1>Frances Hunter correspondence</h1>'
                 '<p class="lede">CONFIDENTIAL. %d letters with transcriptions and page images, from '
                 'gated/letters-dataset.json. Not public on the website. Built %s. '
                 '<a href="CATALOGUE.html">&larr; catalogue</a></p>' % (n_letters, built))
        with open(os.path.join(t, "LETTERS.html"), "w", encoding="utf-8") as f:
            f.write(_page("Frances Hunter correspondence", lhead + "".join(out)))
    say("index: CATALOGUE.html (%d objects)%s" % (len(rows), ", LETTERS.html (%d)" % n_letters if has_letters else ""))


# -- copy-to: a second, verified copy of the finished drive folder --------------

def step_copy(t, dest):
    dest = os.path.abspath(dest)
    if os.path.normcase(dest) == os.path.normcase(t):
        raise SystemExit("--copy-to is the same folder as the target")
    os.makedirs(dest, exist_ok=True)
    # sync deletes extras in dest: only into an empty folder or an earlier copy.
    if os.listdir(dest) and not os.path.isfile(os.path.join(dest, "BUILD-INFO.json")):
        raise SystemExit("--copy-to folder is not empty and not a doomsday copy: " + dest)
    run(["rclone", "sync", t, dest, "--transfers", "4", "--checkers", "8",
         "--stats", "1m", "--stats-one-line"])
    # The copy checks itself against the manifest it carries.
    res = subprocess.run([sys.executable, os.path.join(dest, "verify.py"), "--no-pause"])
    if res.returncode != 0:
        raise SystemExit("copy at %s failed verification" % dest)
    say("copy at %s verified" % dest)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def step_fixity(t):
    fx = os.path.join(t, "fixity")
    os.makedirs(fx, exist_ok=True)
    lines, n = [], 0
    for dp, dns, fns in os.walk(t):
        dns[:] = sorted(d for d in dns if os.path.join(dp, d) != fx)
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            rel = os.path.relpath(p, t).replace(os.sep, "/")
            lines.append("%s  %s" % (sha256(p), rel))
            n += 1
            if n % 250 == 0:
                say("fixity: %d files hashed" % n)
    body = "\n".join(lines) + "\n"
    for name in ("manifest-%s.sha256" % TODAY, "manifest-latest.sha256"):
        with open(os.path.join(fx, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(body)
    say("fixity: %d files -> fixity/manifest-%s.sha256" % (n, TODAY))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("target", help="folder on the drive, e.g. J:\\HH-ARCHIVE-DOOMSDAY")
    ap.add_argument("--only", nargs="+", choices=STEPS, help="run just these steps")
    ap.add_argument("--skip", nargs="+", choices=STEPS, default=[], help="skip these steps")
    ap.add_argument("--stage", help="fast local folder to download into first (for slow USB sticks)")
    ap.add_argument("--copy-to", nargs="+", default=[], metavar="FOLDER",
                    help="after building, sync the finished folder here too and verify it "
                         "(e.g. K:\\BACKUPS\\HH-ARCHIVE-DOOMSDAY)")
    a = ap.parse_args()
    t = os.path.abspath(a.target)
    os.makedirs(t, exist_ok=True)
    steps = [s for s in (a.only or STEPS) if s not in a.skip]
    for s in STEPS:
        if s in steps:
            say("== %s ==" % s)
            if s == "mirror":
                step_mirror(t, a.stage)
            else:
                globals()["step_" + s](t)
    for dest in a.copy_to:
        say("== copy-to %s ==" % dest)
        step_copy(t, dest)
    say("done: " + ", ".join(steps + ["copy-to"] * bool(a.copy_to)))


if __name__ == "__main__":
    main()
