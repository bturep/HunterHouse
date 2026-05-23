"""
Three smoke tests covering the highest-value paths in next.html:
  - catalogue loads from live Wikibase via SPARQL
  - search → select → record-pane renders
  - mobile shell renders at a phone viewport

Run:  pytest tests/                (headless, ~10–15 s)
      pytest tests/ --headed       (watch the browser)
"""

import re

import pytest
from playwright.sync_api import expect


# Generous timeout for SPARQL — Wikibase Cloud can take a couple seconds
# on a cold cache. Tests are smoke, not stress.
CATALOGUE_TIMEOUT_MS = 20_000


def _wait_for_catalogue(page):
    """Wait until the list pane has rendered at least one item row."""
    page.wait_for_selector(".row[data-id], .list .row", timeout=CATALOGUE_TIMEOUT_MS)


def test_loads_catalogue(server, page):
    """next.html boots, SPARQL returns, list pane renders the catalogue."""
    page.goto(server + "/next.html")
    _wait_for_catalogue(page)
    # We have ~180 items in the live catalogue; assert a generous floor so
    # a future schema tweak that drops a few items doesn't trip the test.
    rows = page.locator(".row[data-id]")
    count = rows.count()
    assert count >= 100, f"expected ≥100 list rows after catalogue load, got {count}"


def test_search_hunter(server, page):
    """`/` opens search → type → first result selects → record title shows."""
    page.goto(server + "/next.html")
    _wait_for_catalogue(page)
    # Dismiss the splash overlay (HHFA pane) so keyboard hits the page.
    # Try the desktop Continue button first; mobile flow has its own.
    continue_btn = page.locator("#about-pane-continue")
    if continue_btn.is_visible():
        continue_btn.click()
    page.wait_for_timeout(400)  # let the splash animation settle
    page.keyboard.press("/")
    page.locator("#search-input").fill("hunter")
    page.wait_for_timeout(400)  # debounce + filter
    visible_rows = page.locator(".row[data-id]:visible")
    assert visible_rows.count() > 0, "search filtered to zero rows"
    visible_rows.first.click()
    # Record pane title is the .meta-title element.
    expect(page.locator(".meta-title").first).to_be_visible(timeout=5_000)
    title_text = page.locator(".meta-title").first.inner_text().strip()
    assert title_text, "record-pane title is empty after selecting an item"


def test_mobile_shell(server, browser):
    """At a phone viewport the mobile tab bar is present and switchable."""
    context = browser.new_context(viewport={"width": 375, "height": 812},
                                  device_scale_factor=2,
                                  is_mobile=True, has_touch=True)
    page = context.new_page()
    try:
        page.goto(server + "/next.html")
        _wait_for_catalogue(page)
        # Mobile splash uses #mob-about — dismiss if visible so the
        # underlying tab bar is reachable.
        mob_continue = page.locator("#mob-about-continue")
        if mob_continue.is_visible():
            mob_continue.click()
            page.wait_for_timeout(300)
        # Mobile-only tab bar should be present.
        tabs = page.locator(".mob-tabs")
        expect(tabs).to_be_visible(timeout=5_000)
        # Tap the "Item" tab — should navigate without throwing.
        item_tab = page.locator(".mob-tabs [data-pane='item'], .mob-tabs button:has-text('Item')").first
        if item_tab.count():
            item_tab.click()
    finally:
        context.close()
