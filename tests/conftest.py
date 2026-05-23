"""
Shared pytest fixtures for the HunterHouse smoke tests.

The `server` fixture spins up a one-off http.server on a random
loopback port, rooted at the repo root, for the duration of the test
session. That makes next.html / browse.html load over HTTP — necessary
for the relative `fetch()` calls (curations/, manifest.json, sw.js)
that don't work cleanly under file:// in Chromium.
"""

import http.server
import socketserver
import threading
from pathlib import Path

import pytest


@pytest.fixture(scope="session")
def server():
    repo_root = Path(__file__).parent.parent.resolve()

    class _Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(repo_root), **kwargs)

        # Quiet — pytest captures stdout and we don't need the per-request log.
        def log_message(self, *_a, **_kw):
            pass

    httpd = socketserver.TCPServer(("127.0.0.1", 0), _Handler)
    port = httpd.server_address[1]
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        httpd.shutdown()
        thread.join(timeout=2)
