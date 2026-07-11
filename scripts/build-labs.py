#!/usr/bin/env python3
"""
build-labs.py — generate the UI-lab variants (lab-a/b/c.html) from next.html.

2026-07-10 filter/browse study. REBASED same day after the first lab-a layer
(facet counts + zero-greys, applied-filter pills + real empty state, left-panel
search) was promoted into browse.html v1.08.05 and next.html v1.09-test.77.
The labs now carry only the still-open questions:

  lab-a.html  the TRAY: the filter dropdown becomes a max-height tray so the
              list stays visible and live-updates below while chips are
              toggled ("the horizontal split of the left pane" — undecided).
  lab-b.html  = a + the grouped list: opens grouped by ITEM TYPE (everyday
              bins, CCA functional-series style), contracted by default,
              sticky collapsible headers with counts; Phase grouping stays
              available via the Phase sort for the scholarly reading; an
              active search auto-expands all groups.
  lab-c.html  = a + an always-visible facet sidebar left of the item list
              (stakeholder proposal — REJECTED 2026-07-10 review, kept only
              for the F&O comparison; delete when the email is out).

Rules: labs are DISPOSABLE — fold the chosen direction into next.html and
delete the lab files. Regenerate after next.html changes with:
    py -3 scripts/build-labs.py
Exact-match patches; the script fails loudly if next.html drifts under an
anchor (count != 1), so a stale patch can never half-apply.
"""
import sys, io
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "next.html"
SRC_VERSION = "v1.09-test.77"

def patch(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"PATCH FAILED [{label}]: anchor found {n} times (want 1). next.html has drifted; update the patch.")
    return text.replace(old, new)

# ── the tray (all labs) ──────────────────────────────────────────────────
OLD_FILTER_PANEL_CSS = """\
  .filter-panel{
    position:absolute;top:41px;left:0;right:0;bottom:0;z-index:50;
    background:var(--bg);
    padding:16px 20px 14px;
    overflow-y:auto;
  }
"""
NEW_FILTER_PANEL_CSS = """\
  .filter-panel{
    position:absolute;top:41px;left:0;right:0;z-index:50;
    max-height:min(62%,520px);                     /* LAB: tray, not curtain — */
    background:var(--bg);                          /* the list stays visible + */
    padding:16px 20px 14px;                        /* live-updates below.      */
    overflow-y:auto;
    border-bottom:1px solid var(--rule);
    box-shadow:0 14px 24px -18px rgba(0,0,0,0.45);
  }
"""

# ── lab-b: grouped list ──────────────────────────────────────────────────
CSS_LAB_B = """\
  /* ══ LAB B: collapsible, sticky group headers (contracted by default) ══ */
  .ph-head{position:sticky;top:0;z-index:6;cursor:pointer}
  .ph-head:hover span:first-child{color:var(--ink)}
  .ph-chev{display:inline-block;width:14px;color:var(--muted)}
  .ph-head.closed{border-bottom-style:dashed}
"""

OLD_PHASE_DIVIDER = """\
    state.filtered.forEach((it, _idx) => {
      if (grouped && it.phase !== lastPhase) {
        lastPhase = it.phase;
        const count = state.filtered.filter(x => x.phase === lastPhase).length;
        const d = document.createElement("div");
        d.className = "phase-divider";
        d.innerHTML = `<span>${escapeHTML(lastPhase || "—")}</span><span class="r">${String(count).padStart(2,"0")} items</span>`;
        frag.appendChild(d);
      }
"""
NEW_PHASE_DIVIDER_B = """\
    // LAB B: groups follow the active sort column — Type (everyday, CCA-style
    // functional series) or Phase (the scholarly axis). Groups open CONTRACTED
    // (the CCA convention — counts do the orienting); a live search auto-
    // expands everything so results never hide behind a closed header.
    const gkeyOf = it => (state.sortCol === "type" ? (it.itemType || "—") : (it.phase || "—"));
    const searchOpen = !!state.search.trim();
    state.filtered.forEach((it, _idx) => {
      const gkey = gkeyOf(it);
      if (grouped && gkey !== lastPhase) {
        lastPhase = gkey;
        const count = state.filtered.filter(x => gkeyOf(x) === gkey).length;
        const d = document.createElement("div");
        const open = searchOpen || phaseExpanded.has(gkey);
        d.className = "phase-divider ph-head" + (open ? "" : " closed");
        d.dataset.phase = gkey;
        d.innerHTML = `<span><span class="ph-chev">${open ? "⌄" : "›"}</span>${escapeHTML(gkey)}</span><span class="r">${String(count).padStart(2,"0")} items</span>`;
        d.addEventListener("click", () => {
          if (phaseExpanded.has(gkey)) phaseExpanded.delete(gkey); else phaseExpanded.add(gkey);
          renderList();
        });
        frag.appendChild(d);
      }
      if (grouped && !searchOpen && !phaseExpanded.has(gkey)) return;   // LAB B: group is contracted
"""

# ── lab-c: permanent facet sidebar ───────────────────────────────────────
CSS_LAB_C = """\
  /* ══ LAB C: always-visible facet sidebar (stakeholder proposal) ══ */
  .panel-left{width:44%}
  #facet-side{width:210px;flex-shrink:0;overflow-y:auto;
    border-right:1px solid var(--rule);padding:14px 14px 20px}
  #facet-side .fp-group{margin-bottom:16px}
  @media (max-width:1100px){ .panel-left{width:52%} }
  @media (min-width:768px){ .filter-chevron{display:none} #filter-panel{display:none!important} }
  @media (max-width:767px){ #facet-side{display:none} }
"""

# ── per-lab build ────────────────────────────────────────────────────────

def build(lab, css_extra, extra_patches, version):
    text = SRC.read_text(encoding="utf-8")
    L = lab.upper()

    text = patch(text, "<title>Hunter House Archive — NEXT</title>",
                       f"<title>Hunter House Archive — LAB {L}</title>", "title")
    text = patch(text, f'  const VERSION      = "{SRC_VERSION}";',
                       f'  const VERSION      = "{SRC_VERSION}-lab{lab}.{version}";', "version")
    text = patch(text, '<span class="mk-page" id="mk-page">Archive</span>',
                       f'<span class="mk-page" id="mk-page">Archive · Lab {L}</span>', "mk-page")
    text = patch(text, "cur==='map'?'Site Plan':(cur==='tl'?'Timeline':'Archive')",
                       f"cur==='map'?'Site Plan':(cur==='tl'?'Timeline':'Archive · Lab {L}')", "mk-page-js")
    text = patch(text, OLD_FILTER_PANEL_CSS, NEW_FILTER_PANEL_CSS, "tray-css")
    if css_extra:
        row_anchor = "  .row{\n    display:grid;grid-template-columns:104px 1fr 50px;gap:12px;"
        text = patch(text, row_anchor, css_extra + row_anchor, "lab-css")

    for old, new, label in extra_patches:
        text = patch(text, old, new, label)

    out = ROOT / f"lab-{lab}.html"
    out.write_text(text, encoding="utf-8", newline="\n")
    print(f"built {out.name}  ({len(text):,} chars)")

def main():
    # LAB A — the tray only (everything else promoted 2026-07-10)
    build("a", "", [], version="03")

    # LAB B — + grouped list (type bins, contracted). v04 candidate: authored
    # series map (House drawings 116 / House photographs 71 / Furniture &
    # objects 45 / Engineering & surveys 21 / Papers & ephemera 7) — pending
    # Brandon's blessing of the labels.
    build("b", CSS_LAB_B, [
        ('    sortCol: "id",',
         '    sortCol: "type",   // LAB B: open grouped by item type — everyday bins (CCA-style series)',
         "default-sort"),
        ('          <button class="sort-hd" data-sort-col="id">ID<span class="sort-arrow" id="sa-id"></span></button>',
         '          <button class="sort-hd" data-sort-col="id">ID<span class="sort-arrow" id="sa-id"></span></button>\n'
         '          <button class="sort-hd" data-sort-col="type">Type<span class="sort-arrow" id="sa-type"></span></button>',
         "type-sort-button"),
        ('    ["id", "phase", "year"].forEach(col => {',
         '    ["id", "type", "phase", "year"].forEach(col => {',
         "type-sort-head"),
        ('      "phase": tailLast((a, b) => dir * (a.phase||"").localeCompare(b.phase||"") || (a.id||"").localeCompare(b.id||"")),',
         '      "type":  tailLast((a, b) => dir * (a.itemType||"").localeCompare(b.itemType||"") || (a.id||"").localeCompare(b.id||"")),   // LAB B\n'
         '      "phase": tailLast((a, b) => dir * (a.phase||"").localeCompare(b.phase||"") || (a.id||"").localeCompare(b.id||"")),',
         "type-comparator"),
        ("  function renderList() {",
         "  const phaseExpanded = new Set();   // LAB B: opened groups (contracted by default, session-scope)\n"
         "  function renderList() {",
         "expand-state"),
        ('    const grouped = !state.curation && state.sortCol === "phase";',
         '    const grouped = !state.curation && (state.sortCol === "phase" || state.sortCol === "type");   // LAB B',
         "grouped-trigger"),
        (OLD_PHASE_DIVIDER, NEW_PHASE_DIVIDER_B, "collapsible-headers"),
    ], version="04")

    # LAB C — + always-on facet sidebar (rejected; kept for the F&O comparison)
    build("c", CSS_LAB_C, [
        ('    <button class="cur-leave" id="cur-leave" type="button" hidden title="Leave this selection">LEAVE SELECTION <span class="cl-x">×</span></button>\n    <div class="panel-content">',
         '    <button class="cur-leave" id="cur-leave" type="button" hidden title="Leave this selection">LEAVE SELECTION <span class="cl-x">×</span></button>\n'
         '    <div id="facet-side" aria-label="Filters"></div>\n    <div class="panel-content">',
         "sidebar-markup"),
        ('  function renderFilterPanel() {\n    const panel = $("#filter-panel");\n    if (!panel) return;',
         '  function renderFilterPanel() {\n'
         '    // LAB C: on desktop the facets render into the permanent sidebar;\n'
         '    // mobile keeps the dropdown.\n'
         '    const side = document.getElementById("facet-side");\n'
         '    const panel = (side && window.matchMedia("(min-width:768px)").matches) ? side : $("#filter-panel");\n'
         '    if (!panel) return;',
         "sidebar-target"),
    ], version="03")

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
