# tests/ — Playwright smoke tests

Dev-only smoke tests. Not run in CI; not deployed. They exist as a guard
against silent regressions in the things that are hardest to catch by
inspection: the SPARQL→list pipeline, the desktop→record flow, and the
mobile shell at a phone viewport.

The audit (§11.3) recommends keeping smoke tests around for exactly the
moment a refactor breaks something subtle that the validate workflow
(JS syntax + VERSION regex + manifest parse) can't see.

## One-time setup

```bash
pip3 install pytest-playwright   # ~10 MB
playwright install chromium      # ~150 MB (browser binary)
```

That's it. Both touch only your local Python environment / Playwright's
own cache; nothing inside this repo changes.

## Run

```bash
# From the repo root:
pytest tests/

# A single test, with browser UI visible:
pytest tests/test_smoke.py::test_search_hunter --headed --slowmo 200
```

The `conftest.py` spins up a one-off `http.server` on `127.0.0.1:<random
port>` rooted at the repo, so the tests load `next.html` (and `browse.html`)
exactly as a real browser would, including the relative-path fetches for
`curations/*.json` and `assets/*.css`.

Catalogue data is fetched from the real `hunterhouse.wikibase.cloud`
SPARQL endpoint — these are smoke tests, not unit tests. Each run takes
~10–15 seconds; failures usually point at:
1. A JS exception during init (run with `--headed` to see DevTools).
2. SPARQL or R2 down (rare; check `verify_r2_links.py`).
3. A genuine regression in the path under test.

## What's covered

- **`test_loads_catalogue`** — `next.html` loads, SPARQL returns, list
  renders ≥ 100 rows. Catches a syntax error in the main script block
  (CI catches some of these too; this catches the runtime-only ones).
- **`test_search_hunter`** — type `/` to open search, type "hunter",
  pick the first result, confirm the record-pane title renders.
  Catches a regression in filtering / selection / `renderMeta`.
- **`test_mobile_shell`** — load at 375×812, confirm the mobile tab
  bar is visible. Catches a regression in the desktop/mobile
  breakpoint or in `switchMobileTab`.

Three tests covers the "would I notice if X stopped working in 90
seconds" surface. Add more when a real regression escapes; until
then this is the right size.
