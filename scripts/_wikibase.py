#!/usr/bin/env python3
"""
Shared Wikibase helper module for HunterHouse scripts.

Why this exists:
  Before this module, every script that wrote to Wikibase re-implemented
  the same four pieces: .env loading, MediaWiki login, CSRF token fetch,
  and "POST with token + retry once on stale-token". The code was correct
  but copy-pasted across 11 files. A bug fix or rate-limit tweak would
  have meant editing all of them. ARCHITECTURE.md §11.2 LOW flagged the
  duplication; this module is the resolution.

What it provides:
  load_env(path)            -> dict of KEY=VALUE pairs from a dotenv file
  WikibaseSession(...)      -> a logged-in requests.Session wrapper with:
      .login()              -> obtain a fresh CSRF token (rare; auto on init)
      .post(action, **kw)   -> POST to /w/api.php with the CSRF token and
                               bot=1; one automatic re-login + retry on
                               badtoken / assertuserfailed / notoken.
      .get(action, **kw)    -> GET (no token needed) for read endpoints.

What it deliberately does NOT do:
  - Wrap every wbX action with a typed helper. Scripts that already build
    `data` dicts by hand keep doing so; this module just centralises the
    transport layer + auth, not the claim-builder surface. Tighter
    wrappers can be added in a follow-up when a clear pattern emerges
    across migrated callers.

Usage:
    from _wikibase import WikibaseSession
    wb = WikibaseSession(user_agent="HunterHouseBot/1.0 (patch_dates)")
    res = wb.post("wbsetlabel", id="Q123", language="en", value="New label")

Read-only callers (SPARQL, wbgetentities) don't need a session and can
just `requests.get(...)` directly — see scripts/backup_metadata.py for
the pattern.
"""

import os
import sys

try:
    import requests
except ImportError:
    sys.exit("Missing 'requests'. Install with:  pip3 install requests")


DEFAULT_ENV  = os.path.expanduser("~/Documents/hh-wikibase-migration/.env")
DEFAULT_API  = "https://hunterhouse.wikibase.cloud/w/api.php"


def load_env(path=DEFAULT_ENV):
    """Read a dotenv-style file → {key: value}. Strips blanks and # comments.

    Tolerant: silently skips malformed lines (no = sign). Returns {} if the
    file is missing (caller decides whether that's fatal).
    """
    env = {}
    try:
        with open(path) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, _, v = line.partition("=")
                env[k.strip()] = v.strip()
    except FileNotFoundError:
        pass
    return env


class WikibaseLoginError(RuntimeError):
    """Raised when MediaWiki login fails (bad creds, locked account, etc.)."""


class WikibaseSession:
    """A logged-in requests.Session against the MediaWiki action API.

    Holds the CSRF token internally and refreshes it once if a write
    returns badtoken / assertuserfailed / notoken (typically a session
    timeout during a long batch run).
    """

    def __init__(self, user_agent, api=DEFAULT_API, env_path=DEFAULT_ENV,
                 env=None, login_now=True):
        self.api = api
        self.env = env if env is not None else load_env(env_path)
        try:
            self.user = self.env["WIKIBASE_BOT_USER"]
            self.password = self.env["WIKIBASE_BOT_PASSWORD"]
        except KeyError as e:
            raise WikibaseLoginError(
                f"Missing credential in .env: {e.args[0]}"
            ) from None
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})
        self.csrf = None
        if login_now:
            self.login()

    # ── auth ────────────────────────────────────────────────────────────
    def login(self):
        """Perform a fresh login → returns the CSRF token (also stored on self)."""
        # MediaWiki two-step login: get a logintoken first, then submit creds.
        r = self.session.get(self.api, params={
            "action": "query", "meta": "tokens", "type": "login",
            "format": "json",
        }).json()
        lt = r["query"]["tokens"]["logintoken"]
        r = self.session.post(self.api, data={
            "action": "login", "lgname": self.user, "lgpassword": self.password,
            "lgtoken": lt, "format": "json",
        }).json()
        if r.get("login", {}).get("result") != "Success":
            raise WikibaseLoginError(f"Wikibase login failed: {r}")
        # CSRF token is separate from the login token — fetch after login.
        r = self.session.get(self.api, params={
            "action": "query", "meta": "tokens", "format": "json",
        }).json()
        self.csrf = r["query"]["tokens"]["csrftoken"]
        return self.csrf

    # ── transport ───────────────────────────────────────────────────────
    _STALE = {"badtoken", "assertuserfailed", "notoken"}

    def post(self, action, **params):
        """POST an action API call with CSRF + bot=1. Retries once on stale token."""
        body = {**params, "action": action, "token": self.csrf,
                "bot": 1, "format": "json"}
        out = self.session.post(self.api, data=body).json()
        if out.get("error", {}).get("code") in self._STALE:
            self.login()
            body["token"] = self.csrf
            out = self.session.post(self.api, data=body).json()
        return out

    def get(self, action, **params):
        """GET an action API call (read-only; no token required)."""
        return self.session.get(self.api, params={
            **params, "action": action, "format": "json",
        }).json()
