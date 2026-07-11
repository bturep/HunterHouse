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
SRC_VERSION = "v1.09-test.78"

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
    // LAB B v05: the COLLECTIONS are the shape (Brandon, 2026-07-10 tuning) —
    // the fonds-level buckets: HHC 115 / EGC 57 / IHC 45 / CAA 36 / FRH 7.
    // ID sort already clusters by collection (HH-{COLL}-{NNNN}), so the
    // grouped view is simply the ID sort wearing collection headers; the
    // Phase sort keeps its headers as the scholarly reading. Groups open
    // CONTRACTED (counts + names do the orienting); a live search auto-
    // expands everything so results never hide behind a closed header.
    const gkeyOf = it => (state.sortCol === "id"
      ? (archiveAbbrev(collectionOf(it)) || "—")
      : (it.phase || "—"));
    const glabelOf = k => (state.sortCol === "id" && COLLECTION_INFO[k]?.title)
      ? `${k} — ${COLLECTION_INFO[k].title}` : k;
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
        d.innerHTML = `<span><span class="ph-chev">${open ? "⌄" : "›"}</span>${escapeHTML(glabelOf(gkey))}</span><span class="r">${String(count).padStart(2,"0")} items</span>`;
        d.addEventListener("click", () => {
          if (phaseExpanded.has(gkey)) phaseExpanded.delete(gkey); else phaseExpanded.add(gkey);
          renderList();
        });
        frag.appendChild(d);
      }
      if (grouped && !searchOpen && !phaseExpanded.has(gkey)) return;   // LAB B: group is contracted
"""

# ── lab-d: record pops up, never pulls out ───────────────────────────────
CSS_LAB_D = """\
  /* ══ LAB D v02: record pops up, never pulls out (Brandon: "it's either
     available or isn't"). Public sessions have NO right pane — the image
     takes its width; a one-line caption under the image carries the identity
     line and opens the full record as a reading CARD over a dimmed image
     (Esc / scrim / × dismiss). Researcher & admin sessions keep the
     workbench pane exactly as today. Mobile untouched (Record tab stays). ══ */
  @media (min-width:768px){
    body:not(.is-researcher):not(.is-admin) .panel-right{display:none}
    body:not(.is-researcher):not(.is-admin) .rec-caption.has-item{display:flex}
  }
  .rec-caption{display:none;align-items:baseline;gap:14px;padding:9px 18px;border-top:1px solid var(--rule);background:var(--bg)}
  .rc-title{font-family:var(--mono);font-size:11px;color:var(--ink);font-weight:500;letter-spacing:0.02em;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
  .rc-meta{font-family:var(--mono);font-size:10px;color:var(--muted);letter-spacing:0.04em;white-space:nowrap;flex-shrink:0}
  .rc-open{margin-left:auto;flex-shrink:0;font-family:var(--mono);font-size:9px;letter-spacing:0.1em;text-transform:uppercase;background:none;border:1px solid var(--rule);border-radius:2px;color:var(--muted);padding:3px 9px;cursor:pointer}
  .rc-open:hover{color:var(--ink);border-color:var(--ink)}
  #rec-card{position:absolute;inset:0;z-index:60;display:flex;align-items:center;justify-content:center}
  #rec-card[hidden]{display:none}
  .rcc-scrim{position:absolute;inset:0;background:rgba(20,17,14,0.32)}
  .rcc-card{position:relative;width:min(440px,86%);max-height:82%;overflow-y:auto;
    background:var(--bg);border:1px solid var(--rule);padding:22px 24px 18px;
    box-shadow:0 18px 48px -20px rgba(0,0,0,0.5)}
  .rcc-x{position:absolute;top:10px;right:12px;background:none;border:0;font-size:16px;color:var(--muted);cursor:pointer;line-height:1}
  .rcc-x:hover{color:var(--ink)}
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

    # LAB B — + grouped list, v05: COLLECTION bins (the fonds level — Brandon:
    # "the collections themselves are good buckets… they show the shape").
    # Default ID sort = collection-grouped headers; Phase sort keeps phase
    # headers; Year sort stays flat. All groups contracted by default.
    build("b", CSS_LAB_B, [
        ("  function renderList() {",
         "  const phaseExpanded = new Set();   // LAB B: opened groups (contracted by default, session-scope)\n"
         "  function renderList() {",
         "expand-state"),
        ('    const grouped = !state.curation && state.sortCol === "phase";',
         '    const grouped = !state.curation && (state.sortCol === "phase" || state.sortCol === "id");   // LAB B v05',
         "grouped-trigger"),
        (OLD_PHASE_DIVIDER, NEW_PHASE_DIVIDER_B, "collapsible-headers"),
    ], version="05")

    # LAB D v02 — record pops up, never pulls out: public gets NO right pane;
    # caption under the image opens the full record as a card overlay.
    # Researchers/admins keep the workbench pane untouched.
    build("d", CSS_LAB_D, [
        ('      <span class="foot-dl"><a href="#" id="if-full" target="_blank" rel="noopener">↓ Original</a><a href="#" id="pdf-dl" rel="noopener" download hidden>↓ PDF</a></span>\n    </div>',
         '      <span class="foot-dl"><a href="#" id="if-full" target="_blank" rel="noopener">↓ Original</a><a href="#" id="pdf-dl" rel="noopener" download hidden>↓ PDF</a></span>\n'
         '    </div>\n'
         '    <div class="rec-caption" id="rec-caption">\n'
         '      <span class="rc-title" id="rc-title"></span>\n'
         '      <span class="rc-meta" id="rc-meta"></span>\n'
         '      <button class="rc-open" id="rc-open" type="button" title="Read the full record">Full record →</button>\n'
         '    </div>\n'
         '    <div id="rec-card" hidden>\n'
         '      <div class="rcc-scrim" id="rcc-scrim"></div>\n'
         '      <div class="rcc-card" role="dialog" aria-modal="true" aria-label="Item record">\n'
         '        <button class="rcc-x" id="rcc-x" aria-label="Close record">×</button>\n'
         '        <div class="rcc-body" id="rcc-body"></div>\n'
         '      </div>\n'
         '    </div>',
         "caption-card-markup"),
        ('      document.getElementById("right-handle").addEventListener("click", () => { if (document.body.classList.contains("lens-info")) { closeInfoPane(); return; } togglePanel("right"); syncFsBtn(); });',
         '      document.getElementById("right-handle").addEventListener("click", () => { if (document.body.classList.contains("lens-info")) { closeInfoPane(); return; } togglePanel("right"); syncFsBtn(); });\n'
         '\n'
         '      // LAB D v02: the public record CARD — populated from the (hidden)\n'
         '      // record pane\'s own rendered HTML, so one renderer serves both.\n'
         '      {\n'
         '        const card = document.getElementById("rec-card");\n'
         '        const openCard = () => {\n'
         '          const src = document.getElementById("meta-body");\n'
         '          if (!src) return;\n'
         '          document.getElementById("rcc-body").innerHTML = src.innerHTML;\n'
         '          card.hidden = false;\n'
         '        };\n'
         '        const closeCard = () => { card.hidden = true; };\n'
         '        const rcBtn = document.getElementById("rc-open");\n'
         '        if (rcBtn) rcBtn.addEventListener("click", openCard);\n'
         '        document.getElementById("rcc-x").addEventListener("click", closeCard);\n'
         '        document.getElementById("rcc-scrim").addEventListener("click", closeCard);\n'
         '        document.addEventListener("keydown", e => {\n'
         '          if (e.key === "Escape" && !card.hidden) { closeCard(); e.stopPropagation(); e.preventDefault(); }\n'
         '        }, true);\n'
         '      }',
         "card-wiring"),
        ('  function renderMeta(item) {\n    const body = $("#meta-body");',
         '  function renderMeta(item) {\n'
         '    // LAB D: mirror the record\'s identity line into the under-image caption;\n'
         '    // close any open record card (its contents belong to the previous item).\n'
         '    {\n'
         '      const rt = document.getElementById("rc-title"), rm = document.getElementById("rc-meta"), rc = document.getElementById("rec-caption");\n'
         '      if (rt && rm && rc) {\n'
         '        rt.textContent = item.title || "";\n'
         '        rm.textContent = [displayId(item.id), item.phase || "", yearOf(item.date)].filter(Boolean).join(" · ");\n'
         '        rc.classList.add("has-item");\n'
         '      }\n'
         '      const oc = document.getElementById("rec-card");\n'
         '      if (oc) oc.hidden = true;\n'
         '    }\n'
         '    const body = $("#meta-body");',
         "caption-populate"),
    ], version="02")

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
