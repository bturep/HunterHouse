#!/usr/bin/env python3
"""Tiny static server that sends no-cache headers — use while iterating on the
mocks so the browser never serves a stale explore-3d.js / mock file.

Run from the project root:  py -3 scripts/serve-nocache.py   (then open :8000)
"""
import http.server, socketserver, os

PORT = 8000
os.chdir(os.path.join(os.path.dirname(__file__), ".."))  # serve the repo root

class NoCache(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

with socketserver.TCPServer(("", PORT), NoCache) as httpd:
    print(f"no-cache server on http://localhost:{PORT}  (Ctrl+C to stop)")
    httpd.serve_forever()
