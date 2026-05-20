#!/usr/bin/env python3
"""
Local edit proxy for next.html admin editing (Slice 2).

Runs ONLY on your Mac. Holds the Wikibase bot credential server-side so it
never touches the public page. next.html (admin, unlocked) POSTs an edit here;
this relays it to the Wikibase API authenticated as the bot.

Run:   python3 scripts/edit_proxy.py
Stop:  Ctrl-C
Listens on http://127.0.0.1:8731  (localhost only — not exposed to the network)

Auth: every request must carry the admin secret (the admin pin, or
EDIT_PROXY_SECRET in .env). Action is restricted to a safe Wikibase allowlist.
"""

import json, os, sys
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

try:
    import requests
except ImportError:
    sys.exit("Missing 'requests'.  pip3 install requests")

ENV   = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")
PORT  = 8731
# Only these Wikibase write actions may be relayed — no arbitrary admin calls.
ALLOWED_ACTIONS = {
    "wbsetlabel", "wbsetdescription", "wbsetaliases",
    "wbcreateclaim", "wbsetclaim", "wbremoveclaims",
    "wbeditentity",   # admins can mint new vocab/person items via the picker (mint-new affordance)
}
# Origins allowed to call this proxy from the browser.
ALLOWED_ORIGINS = ("https://bturep.github.io", "http://localhost", "http://127.0.0.1")

cred = {}
for line in open(ENV):
    line = line.strip()
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        cred[k.strip()] = v.strip()

API    = cred.get("WIKIBASE_API") or cred["WIKIBASE_URL"].rstrip("/") + "/w/api.php"
USER   = cred["WIKIBASE_BOT_USER"]
PASS   = cred["WIKIBASE_BOT_PASSWORD"]
SECRET = cred.get("EDIT_PROXY_SECRET") or "203BTP"   # admin pin by default

session = requests.Session()
session.headers.update({"User-Agent": "HH-edit-proxy/1.0 (local; bturep)"})


def login():
    """MediaWiki login → returns a fresh CSRF token. Same flow as the scripts/."""
    lt = session.get(API, params={"action": "query", "meta": "tokens",
                                   "type": "login", "format": "json"}
                      ).json()["query"]["tokens"]["logintoken"]
    r = session.post(API, data={"action": "login", "lgname": USER,
                                "lgpassword": PASS, "lgtoken": lt,
                                "format": "json"}).json()
    if r.get("login", {}).get("result") != "Success":
        raise RuntimeError(f"Wikibase login failed: {r}")
    return session.get(API, params={"action": "query", "meta": "tokens",
                                    "format": "json"}
                       ).json()["query"]["tokens"]["csrftoken"]


csrf = login()
print(f"✓ logged in as {USER}", flush=True)


def do_edit(params):
    """Relay one allowlisted write, re-logging in once on a stale token."""
    global csrf
    if params.get("action") not in ALLOWED_ACTIONS:
        return {"error": f"action '{params.get('action')}' not allowed"}
    body = {**params, "token": csrf, "bot": 1, "format": "json"}
    out = session.post(API, data=body).json()
    if out.get("error", {}).get("code") in ("badtoken", "assertuserfailed", "notoken"):
        csrf = login()
        body["token"] = csrf
        out = session.post(API, data=body).json()
    return out


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        origin = self.headers.get("Origin", "")
        ok = next((o for o in ALLOWED_ORIGINS if origin.startswith(o)), None)
        self.send_header("Access-Control-Allow-Origin", ok or "null")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code, obj):
        payload = json.dumps(obj).encode()
        self.send_response(code)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_GET(self):
        if self.path == "/ping":
            return self._json(200, {"ok": True, "user": USER})
        self._json(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/edit":
            return self._json(404, {"error": "not found"})
        try:
            n = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(n) or b"{}")
        except Exception:
            return self._json(400, {"error": "bad JSON"})
        if data.get("secret") != SECRET:
            return self._json(403, {"error": "bad secret"})
        params = data.get("params") or {}
        try:
            return self._json(200, do_edit(params))
        except Exception as e:
            return self._json(502, {"error": str(e)})

    def log_message(self, fmt, *args):   # quieter console
        sys.stderr.write("  " + (fmt % args) + "\n")


if __name__ == "__main__":
    print(f"  listening on http://127.0.0.1:{PORT}   (Ctrl-C to stop)", flush=True)
    try:
        ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
    except KeyboardInterrupt:
        print("\n  stopped")
