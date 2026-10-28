#!/usr/bin/env python3
"""
Hunter House archive -- offline server for the doomsday copy.

Runs the archive from this drive with no internet. Standard library only, so
any machine with Python 3 can start it (START.bat / start.command / start.sh
call this file).

The site in site/ is an unmodified copy of the public repo. Instead of
rebuilding it for offline use, this server stands in for the three online
services the site expects, and rewrites their addresses as pages are served:

  archive.hunterhousefoundation.com  -> /r2/           (the mirrored bucket, r2/)
  hhf-r2-browser...workers.dev       -> this server   (/list /dl /gated/* /event)
  hunterhouse.wikibase.cloud SPARQL  -> /offline/sparql (always 503, so the site
                                        falls back to the catalogue snapshot)
  hunterhouse.org                    -> this server

Files on disk are never changed; rewriting happens only in what is sent to
the browser. The copy is read-only by design: nothing here writes anywhere.

The Frances Hunter letters (gated/) open WITHOUT a password on this drive
(Brandon, 2026-10-27): any researcher token is accepted, and browse.html is
served with researcher mode switched on.

Usage:  python3 serve.py [--port 8787] [--no-browser]
"""

import argparse
import datetime as dt
import json
import mimetypes
import os
import posixpath
import socket
import sys
import threading
import urllib.parse
import webbrowser
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.join(ROOT, "site")
R2 = os.path.join(ROOT, "r2")
GATED = os.path.join(ROOT, "gated")

# Text responses get these string swaps. {o} is this server's own origin
# (http://127.0.0.1:<port>), so rewritten URLs stay absolute: the site parses
# some of them with new URL(), which rejects bare paths. Only the SPARQL
# endpoint is diverted; other Wikibase links stay as ordinary outbound links.
REWRITES = [
    ("https://archive.hunterhousefoundation.com", "{o}/r2"),
    ("https://hhf-r2-browser.brandon-628.workers.dev", "{o}"),
    ("https://hunterhouse.wikibase.cloud/query/sparql", "{o}/offline/sparql"),
    ("https://hunterhouse.org/", "{o}/"),
    ("https://www.hunterhousefoundation.com/", "{o}/"),
]
TEXT_EXT = {".html", ".htm", ".js", ".mjs", ".json", ".css", ".xml", ".webmanifest"}

# browse.html only: switch researcher mode on so the letters load with no token.
BROWSE_PATCH = (
    'var _rt = new URLSearchParams(location.search).get("researcher");',
    'var _rt = new URLSearchParams(location.search).get("researcher") || "offline-copy";',
)

for ext, ct in ((".mjs", "text/javascript"), (".json", "application/json"),
                (".webmanifest", "application/manifest+json"), (".jsonl", "application/json")):
    mimetypes.add_type(ct, ext)


def safe_join(base, rel):
    """Join a URL path onto a folder, refusing anything that escapes it."""
    rel = posixpath.normpath("/" + urllib.parse.unquote(rel)).lstrip("/")
    full = os.path.normpath(os.path.join(base, *rel.split("/"))) if rel else base
    if full != base and not full.startswith(base + os.sep):
        return None
    return full


def list_r2(prefix):
    """Emulate the Worker's /list: one folder level of the mirrored bucket."""
    folder = safe_join(R2, prefix)
    out = {"prefix": prefix, "folders": [], "files": [], "truncated": False, "cursor": None}
    if not folder or not os.path.isdir(folder):
        return out
    for name in sorted(os.listdir(folder)):
        p = os.path.join(folder, name)
        key = prefix + name
        if os.path.isdir(p):
            out["folders"].append({"type": "folder", "key": key + "/", "name": name})
        else:
            st = os.stat(p)
            out["files"].append({"type": "file", "key": key, "name": name, "size": st.st_size,
                                 "uploaded": dt.datetime.fromtimestamp(st.st_mtime, dt.timezone.utc)
                                 .strftime("%Y-%m-%dT%H:%M:%S.000Z")})
    return out


class Handler(BaseHTTPRequestHandler):
    server_version = "HHOffline/1"

    def log_message(self, fmt, *args):
        if "--quiet" not in sys.argv:
            sys.stderr.write("  %s\n" % (fmt % args))

    # -- helpers -------------------------------------------------------------
    def send_json(self, obj, status=200):
        body = json.dumps(obj).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def send_plain(self, status, text=""):
        body = text.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        if self.command != "HEAD" and body:
            self.wfile.write(body)

    def redirect(self, location):
        self.send_response(HTTPStatus.FOUND)
        self.send_header("Location", location)
        self.send_header("Content-Length", "0")
        self.end_headers()

    def send_file(self, path, rewrite=False, patch=None):
        if not path or not os.path.isfile(path):
            return self.send_plain(404, "Not found on this drive.")
        ext = os.path.splitext(path)[1].lower()
        ctype = mimetypes.guess_type(path)[0] or "application/octet-stream"
        if rewrite and ext in TEXT_EXT:
            with open(path, "rb") as f:
                text = f.read().decode("utf-8", errors="surrogateescape")
            origin = "http://" + (self.headers.get("Host") or "127.0.0.1")
            for a, b in REWRITES:
                text = text.replace(a, b.replace("{o}", origin))
            if patch:
                text = text.replace(*patch)
            body = text.encode("utf-8", errors="surrogateescape")
            if ctype.startswith("text/") or ext in (".js", ".mjs", ".json"):
                ctype += "; charset=utf-8"
            self.send_response(200)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(body)
            return
        # Binary (masters, images, PDFs, video): stream, with Range support so
        # the PDF reader and video players can seek.
        size = os.path.getsize(path)
        start, end = 0, size - 1
        rng = self.headers.get("Range")
        status = 200
        if rng and rng.startswith("bytes="):
            try:
                a, b = rng[6:].split(",")[0].split("-")
                if a:
                    start, end = int(a), (int(b) if b else size - 1)
                else:
                    start, end = size - int(b), size - 1
                start, end = max(0, start), min(end, size - 1)
                status = 206 if start <= end else 416
            except ValueError:
                status = 200
        if status == 416:
            self.send_response(416)
            self.send_header("Content-Range", "bytes */%d" % size)
            self.end_headers()
            return
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        if status == 206:
            self.send_header("Content-Range", "bytes %d-%d/%d" % (start, end, size))
        self.end_headers()
        if self.command == "HEAD":
            return
        with open(path, "rb") as f:
            f.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = f.read(min(1 << 20, left))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                left -= len(chunk)

    # -- routing -------------------------------------------------------------
    def do_HEAD(self):
        self.do_GET()

    def do_POST(self):
        # /event beacons and /api/notes: accepted and dropped (read-only copy).
        self.send_response(204)
        self.end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        url = urllib.parse.urlsplit(self.path)
        path, q = url.path, urllib.parse.parse_qs(url.query)

        if path in ("/", ""):
            return self.redirect("/index.html")
        if path.startswith("/r2/"):
            return self.send_file(safe_join(R2, path[4:]), rewrite=path.endswith(".json"))
        if path == "/list":
            return self.send_json(list_r2(q.get("prefix", [""])[0]))
        if path == "/dl":
            key = q.get("key", [""])[0]
            return self.redirect("/r2/" + urllib.parse.quote(key))
        if path == "/gated/letters":
            p = os.path.join(GATED, "letters-dataset.json")
            if not os.path.isfile(p):
                return self.send_json({"error": "letters not on this drive yet", "records": []}, 404)
            return self.send_file(p)
        if path == "/gated/img":
            key = q.get("key", [""])[0]
            if not key.startswith("gated/"):
                return self.send_plain(400, "Bad key")
            return self.send_file(safe_join(os.path.join(GATED, "bucket"), key))
        if path.startswith("/offline/") or path in ("/event", "/api/notes"):
            return self.send_plain(503, "Not available in the offline copy.")
        if path == "/sw.js":
            # No service worker: the copy is local, caching would only hide drift.
            return self.send_plain(404)

        full = safe_join(SITE, path)
        if full and os.path.isdir(full):
            full = os.path.join(full, "index.html")
        patch = BROWSE_PATCH if path.rstrip("/").endswith("browse.html") else None
        return self.send_file(full, rewrite=True, patch=patch)


def main():
    ap = argparse.ArgumentParser(description="Serve the Hunter House archive from this drive.")
    ap.add_argument("--port", type=int, default=8787)
    ap.add_argument("--no-browser", action="store_true")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--open", default="/browse.html", help="page to open in the browser")
    args = ap.parse_args()

    if not os.path.isdir(SITE):
        sys.exit("site/ is missing next to serve.py -- is this the archive drive?")

    port = args.port
    for _ in range(20):
        try:
            httpd = ThreadingHTTPServer(("127.0.0.1", port), Handler)
            break
        except OSError:
            port += 1
    else:
        sys.exit("No free port found near %d." % args.port)

    url = "http://127.0.0.1:%d%s" % (port, args.open)
    print()
    print("  Hunter House archive -- offline copy")
    print("  Open:  %s" % url)
    print("  Letters view:  http://127.0.0.1:%d/browse.html?open=letters" % port)
    print("  Leave this window open while browsing. Close it (or Ctrl+C) to stop.")
    print()
    if not args.no_browser:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
