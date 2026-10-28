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
  fixity   SHA-256 of every file -> fixity/manifest-YYYYMMDD.sha256

Usage (PC):
    py -3 scripts/build_doomsday.py J:\\HH-ARCHIVE-DOOMSDAY
    py -3 scripts/build_doomsday.py J:\\HH-ARCHIVE-DOOMSDAY --only site tools fixity
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
STEPS = ["mirror", "site", "repo", "wikibase", "gated", "tools", "fixity"]
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
    say("done: " + ", ".join(steps))


if __name__ == "__main__":
    main()
