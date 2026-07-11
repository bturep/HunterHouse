#!/usr/bin/env python3
"""
build-labs.py — generate the UI-lab variants (lab-a/b/c.html) from next.html.

2026-07-10 filter/browse study. Three disposable test pages, each a full copy
of next.html with targeted patches, so options can be compared side-by-side at
real URLs (file-based staging, same model as next.html itself):

  lab-a.html  Layer 1 "feedback repairs": facet chips gain live result counts
              scoped to the current selection; zero-yield chips grey out
              (visible but unclickable); applied filters render as removable
              pills above the list, covering ALL six facet groups; a real
              empty state replaces the bare "No items match"; the filter
              dropdown becomes a tray (max-height) so the list stays visible
              and visibly reacts while chips are toggled.
  lab-b.html  = lab-a + the phase-grouped list: default sort is Phase, group
              headers become sticky, collapsible (chevron), with counts —
              the archival series view ("in the graph").
  lab-c.html  = lab-a + an always-visible facet sidebar left of the item list
              (the stakeholder proposal, built at full strength for a fair
              comparison). Desktop only; mobile keeps the dropdown.

Rules: labs are DISPOSABLE — when a direction is chosen, fold it into
next.html and delete the lab files. Regenerate after next.html changes with:
    py -3 scripts/build-labs.py
Every patch is an exact-match string replacement; the script fails loudly if
next.html has drifted under an anchor (count != 1), so a stale patch can never
half-apply.
"""
import sys, io
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC  = ROOT / "next.html"

def patch(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f"PATCH FAILED [{label}]: anchor found {n} times (want 1). next.html has drifted; update the patch.")
    return text.replace(old, new)

# ───────────────────────── shared patch material ─────────────────────────

CSS_COMMON = """\
  /* ══ LAB: facet counts + zero-greys ══ */
  .fp-chip .fp-ct{margin-left:6px;font-size:9px;opacity:0.6;letter-spacing:0.02em}
  .fp-chip.zero{opacity:0.32;cursor:default;pointer-events:none}
  .fp-chip.on .fp-ct{opacity:0.85}
  /* ══ LAB: applied-filter bar above the list ══ */
  .af-bar{display:flex;flex-wrap:wrap;gap:5px;align-items:center;
    padding:10px 20px;border-bottom:1px solid var(--rule);background:var(--soft)}
  .af-lbl{font-family:var(--mono);font-size:9px;color:var(--muted);
    letter-spacing:0.16em;text-transform:uppercase;margin-right:4px}
  .af-pill{font-family:var(--mono);font-size:10px;letter-spacing:0.03em;
    border:1px solid var(--rule);background:var(--bg);color:var(--ink);
    padding:2px 8px;border-radius:2px;cursor:pointer;line-height:1.5}
  .af-pill:hover{border-color:var(--ink)}
  .af-pill .x{margin-left:5px;color:var(--muted)}
  .af-pill:hover .x{color:var(--red-deep)}
  .af-clear{font-family:var(--mono);font-size:9px;color:var(--muted);
    letter-spacing:0.1em;text-transform:uppercase;cursor:pointer;
    background:none;border:0;padding:2px 4px;margin-left:auto}
  .af-clear:hover{color:var(--ink)}
  .empty-hint{padding:10px 20px 0;font-family:var(--mono);font-size:10px;color:var(--muted);line-height:1.7}
  /* ══ LAB: search lives with finding (left panel), not in the top-right
     settings cluster. Desktop hides the top-right search UI; the #search-input
     element stays in the DOM as the proxy target (same pattern mobile uses). ══ */
  .lp-search{display:flex;align-items:center;gap:8px;padding:8px 20px;border-bottom:1px solid var(--rule);flex-shrink:0}
  .lp-search .pfx{font-family:var(--mono);font-size:10px;color:var(--hint)}
  .lp-search input{flex:1;min-width:0;background:none;border:0;outline:none;font-family:var(--mono);font-size:11px;color:var(--ink);letter-spacing:0.03em}
  .lp-search input::placeholder{color:var(--hint);text-transform:lowercase;letter-spacing:0.06em}
  @media (min-width:768px){
    #search-toggle{display:none!important}
    #search-input.tr-search-input{display:none!important}
    .filter-panel{top:74px}   /* tray opens below the search row, not over it */
  }
  @media (max-width:767px){ .lp-search{display:none} }  /* mobile keeps its own fp-search-row */
"""

CSS_LAB_B = """\
  /* ══ LAB B: collapsible, sticky group headers (contracted by default) ══ */
  .ph-head{position:sticky;top:0;z-index:6;cursor:pointer}
  .ph-head:hover span:first-child{color:var(--ink)}
  .ph-chev{display:inline-block;width:14px;color:var(--muted)}
  .ph-head.closed{border-bottom-style:dashed}
"""

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

FACET_HELPER = """\
  // ── LAB: per-chip facet counts. For each facet group, the count base is
  // the item set passing every OTHER active filter (standard facet logic) —
  // a chip's number answers "what would I get if I added this?".
  function facetBase(exclude) {
    const q = state.search.trim().toLowerCase();
    return state.items.filter(it => {
      if (it.gated) return false;
      if (state.filterMarkedOnly && !marksHas(it.id)) return false;
      if (exclude !== "collection" && state.filterCollection.size && !state.filterCollection.has(archiveAbbrev(collectionOf(it)))) return false;
      if (exclude !== "area" && state.filterArea.size && !(it.areas||[]).some(a => state.filterArea.has(a))) return false;
      if (exclude !== "itype" && state.filterType.size && !state.filterType.has(it.itemType)) return false;
      if (exclude !== "drawtype" && state.filterDrawType.size && !(it.drawTypes||[]).some(dt => state.filterDrawType.has(dt))) return false;
      if (exclude !== "creator" && state.filterCreator.size) {
        const persons = [it.creator, it.designedBy, ...(it.builtBy || [])].filter(Boolean);
        if (!persons.some(c => state.filterCreator.has(c))) return false;
      }
      if (exclude !== "builtstatus" && state.filterBuiltStatus.size && !state.filterBuiltStatus.has(it.builtStatus)) return false;
      if (q) {
        const hay = [it.id, it.title, it.phase, it.itemType||"", (it.drawTypes||[]).join(" "), (it.areas||[]).join(" "), it.creator, it.designedBy||"", (it.builtBy||[]).join(" "), it.notes||"", it.location||""].join(" ").toLowerCase();
        if (!hay.includes(q)) return false;
      }
      return true;
    });
  }
  const FACET_MATCH = {
    collection:  (it, v) => archiveAbbrev(collectionOf(it)) === v,
    area:        (it, v) => (it.areas||[]).includes(v),
    itype:       (it, v) => it.itemType === v,
    drawtype:    (it, v) => (it.drawTypes||[]).includes(v),
    creator:     (it, v) => [it.creator, it.designedBy, ...(it.builtBy||[])].includes(v),
    builtstatus: (it, v) => it.builtStatus === v,
  };
"""

AF_BAR_BLOCK = """\
    // ── LAB: applied filters as removable pills above the list — always
    // visible whenever any facet is active, whether or not the dropdown is
    // open. Every group is represented (the old divider covered only 3 of 6).
    const AF_GROUPS = [
      ["collection",  state.filterCollection ],
      ["area",        state.filterArea       ],
      ["itype",       state.filterType       ],
      ["drawtype",    state.filterDrawType   ],
      ["creator",     state.filterCreator    ],
      ["builtstatus", state.filterBuiltStatus],
    ];
    const afActive = !state.curation && AF_GROUPS.some(([,s]) => s.size);
    const afBar = () => {
      const bar = document.createElement("div");
      bar.className = "af-bar";
      bar.innerHTML =
        `<span class="af-lbl">Filters</span>` +
        AF_GROUPS.flatMap(([g, s]) => [...s].map(v =>
          `<button class="af-pill" data-af-g="${g}" data-af-v="${escapeHTML(v)}">${escapeHTML(v)}<span class="x">×</span></button>`
        )).join("") +
        `<button class="af-clear" id="filter-clear-all">✕ clear all</button>`;
      bar.querySelectorAll(".af-pill").forEach(p => p.addEventListener("click", e => {
        e.stopPropagation();
        const set = new Map(AF_GROUPS).get(p.dataset.afG);
        if (set) set.delete(p.dataset.afV);
        applyFilters(); renderList(); updateFilterBadge(); renderFilterPanel();
      }));
      return bar;
    };

    if (state.filtered.length === 0) {
      if (afActive) container.appendChild(afBar());
      const d = document.createElement("div");
      d.className = "empty";
      d.textContent = "No items match this combination";
      container.appendChild(d);
      const hint = document.createElement("div");
      hint.className = "empty-hint";
      hint.textContent = afActive
        ? "Remove a filter above to widen the selection — an empty result means these facets don't overlap in the catalogue."
        : "Try a different search term.";
      container.appendChild(hint);
      const clearBtn0 = document.getElementById("filter-clear-all");
      if (clearBtn0) clearBtn0.addEventListener("click", e => {
        e.stopPropagation(); clearAllFilters();
        applyFilters(); renderList(); updateFilterBadge(); renderFilterPanel();
      });
      return;
    }

    const grouped = !state.curation && state.sortCol === "phase";
    const frag = document.createDocumentFragment();
    let lastPhase = null;
    const noted = rnNotedIds();   // items with a viewer-visible note
    const flags = canMark();      // the flag strip is a researcher workspace

    if (afActive) frag.appendChild(afBar());
"""

OLD_EMPTY_AND_DIVIDER = """\
    if (state.filtered.length === 0) {
      container.innerHTML = `<div class="empty">No items match</div>`;
      return;
    }

    const grouped = !state.curation && state.sortCol === "phase";
    const frag = document.createDocumentFragment();
    let lastPhase = null;
    const noted = rnNotedIds();   // items with a viewer-visible note
    const flags = canMark();      // the flag strip is a researcher workspace

    const anyFilter = state.filterArea.size || state.filterType.size || state.filterDrawType.size;
    if (anyFilter) {
      const d = document.createElement("div");
      d.className = "phase-divider";
      const n = String(state.filtered.length).padStart(2,"0");
      d.innerHTML = `<span>Filtered <span style="color:var(--muted);font-weight:400">${n} items</span></span><span class="r" style="cursor:pointer" id="filter-clear-all">✕ clear all</span>`;
      frag.appendChild(d);
    }
"""

OLD_GROUP_FN = """\
    const group = (label, vals, activeSet, cls, attr, color) => {
      if (!vals.length) return "";
      const pc = color ? ` ${pillCls(color)}` : "";
      const chips = vals.map(v => {
        const chip = `<button class="fp-chip${activeSet.has(v) ? " on" : ""}${pc}" data-${attr}="${escapeHTML(v)}">${escapeHTML(v)}</button>`;
"""

NEW_GROUP_FN = """\
    const group = (label, vals, activeSet, cls, attr, color) => {
      if (!vals.length) return "";
      const pc = color ? ` ${pillCls(color)}` : "";
      const base = facetBase(attr);          // LAB: count base for this group
      const match = FACET_MATCH[attr];
      const chips = vals.map(v => {
        const n = match ? base.filter(it => match(it, v)).length : 0;   // LAB
        const zero = n === 0 && !activeSet.has(v);   // active chips stay clickable (to deselect)
        const chip = `<button class="fp-chip${activeSet.has(v) ? " on" : ""}${zero ? " zero" : ""}${pc}" data-${attr}="${escapeHTML(v)}">${escapeHTML(v)}<span class="fp-ct">${n}</span></button>`;
"""

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

# ───────────────────────── per-lab build ─────────────────────────

def build(lab, css_extra, extra_patches, version="01"):
    text = SRC.read_text(encoding="utf-8")
    L = lab.upper()

    text = patch(text, "<title>Hunter House Archive — NEXT</title>",
                       f"<title>Hunter House Archive — LAB {L}</title>", "title")
    text = patch(text, '  const VERSION      = "v1.09-test.76";',
                       f'  const VERSION      = "v1.09-test.76-lab{lab}.{version}";', "version")
    text = patch(text, '<span class="mk-page" id="mk-page">Archive</span>',
                       f'<span class="mk-page" id="mk-page">Archive · Lab {L}</span>', "mk-page")
    text = patch(text, "cur==='map'?'Site Plan':(cur==='tl'?'Timeline':'Archive')",
                       f"cur==='map'?'Site Plan':(cur==='tl'?'Timeline':'Archive · Lab {L}')", "mk-page-js")
    text = patch(text, OLD_FILTER_PANEL_CSS, NEW_FILTER_PANEL_CSS, "tray-css")
    # inject lab CSS just before the .row rule
    row_anchor = "  .row{\n    display:grid;grid-template-columns:104px 1fr 50px;gap:12px;"
    text = patch(text, row_anchor, CSS_COMMON + css_extra + row_anchor, "lab-css")
    # facet helper before renderFilterPanel
    rfp_anchor = "  function renderFilterPanel() {"
    text = patch(text, rfp_anchor, FACET_HELPER + rfp_anchor, "facet-helper")
    text = patch(text, OLD_GROUP_FN, NEW_GROUP_FN, "chip-counts")
    text = patch(text, OLD_EMPTY_AND_DIVIDER, AF_BAR_BLOCK, "af-bar")

    # Left-panel search row (markup + proxy wiring + "/" shortcut retarget)
    text = patch(text,
        '      <div class="filter-panel" id="filter-panel" hidden></div>',
        '      <div class="lp-search" id="lp-search">\n'
        '        <span class="pfx">/</span>\n'
        '        <input id="lp-search-input" type="text" placeholder="search archive" autocomplete="off" autocorrect="off" spellcheck="false" aria-label="Search the archive">\n'
        '      </div>\n'
        '      <div class="filter-panel" id="filter-panel" hidden></div>',
        "lp-search-markup")
    text = patch(text,
        '    $("#filter-panel").addEventListener("click", e => e.stopPropagation());',
        '    $("#filter-panel").addEventListener("click", e => e.stopPropagation());\n'
        '\n'
        '    // LAB: left-panel search — proxies into #search-input exactly like the\n'
        '    // mobile filter-panel search does. Two-way sync, Escape clears.\n'
        '    {\n'
        '      const lp = document.getElementById("lp-search-input");\n'
        '      const se = document.getElementById("search-input");\n'
        '      if (lp && se) {\n'
        '        lp.addEventListener("input", () => {\n'
        '          se.value = lp.value;\n'
        '          se.dispatchEvent(new Event("input", { bubbles: true }));\n'
        '        });\n'
        '        se.addEventListener("input", () => {\n'
        '          if (document.activeElement !== lp && lp.value !== se.value) lp.value = se.value;\n'
        '        });\n'
        '        lp.addEventListener("keydown", e => {\n'
        '          if (e.key === "Escape") {\n'
        '            lp.value = ""; se.value = "";\n'
        '            se.dispatchEvent(new Event("input", { bubbles: true }));\n'
        '            lp.blur(); e.preventDefault();\n'
        '          }\n'
        '        });\n'
        '      }\n'
        '    }',
        "lp-search-wiring")
    text = patch(text,
        '    function openSearch() { if (!searchInput) return; searchInput.classList.add("open"); searchInput.focus(); }',
        '    function openSearch() {\n'
        '      const lp = document.getElementById("lp-search-input");          // LAB: "/" focuses the\n'
        '      if (lp && lp.offsetParent) { lp.focus(); return; }              // left-panel search\n'
        '      if (!searchInput) return; searchInput.classList.add("open"); searchInput.focus();\n'
        '    }',
        "slash-retarget")

    for old, new, label in extra_patches:
        text = patch(text, old, new, label)

    out = ROOT / f"lab-{lab}.html"
    out.write_text(text, encoding="utf-8", newline="\n")
    print(f"built {out.name}  ({len(text):,} chars)")

def main():
    # LAB A — feedback repairs only
    build("a", "", [], version="02")

    # LAB B — + grouped list. v.02 after Brandon's 2026-07-10 review: groups by
    # ITEM TYPE by default (everyday bins, CCA functional-series style — phases
    # assume expert knowledge), contracted by default (the CCA convention),
    # Phase grouping still available via the Phase sort for the scholarly eye.
    build("b", CSS_LAB_B, [
        ('    sortCol: "id",',
         '    sortCol: "type",   // LAB B: open grouped by item type — everyday bins (CCA-style series)',
         "default-sort"),
        # Type joins the sort row (ID · Type · Phase · Year)
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
        # grouped-view trigger widens to the Type sort (AF_BAR_BLOCK plants this line)
        ('    const grouped = !state.curation && state.sortCol === "phase";',
         '    const grouped = !state.curation && (state.sortCol === "phase" || state.sortCol === "type");   // LAB B',
         "grouped-trigger"),
        (OLD_PHASE_DIVIDER, NEW_PHASE_DIVIDER_B, "collapsible-headers"),
    ], version="03")

    # LAB C — + always-visible facet sidebar (desktop)
    build("c", CSS_LAB_C, [
        ('    <button class="cur-leave" id="cur-leave" type="button" hidden title="Leave this selection">LEAVE SELECTION <span class="cl-x">×</span></button>\n    <div class="panel-content">',
         '    <button class="cur-leave" id="cur-leave" type="button" hidden title="Leave this selection">LEAVE SELECTION <span class="cl-x">×</span></button>\n'
         '    <div id="facet-side" aria-label="Filters"></div>\n    <div class="panel-content">',
         "sidebar-markup"),
        ('  function renderFilterPanel() {\n    const panel = $("#filter-panel");\n    if (!panel) return;',
         '  function renderFilterPanel() {\n'
         '    // LAB C: on desktop the facets render into the permanent sidebar;\n'
         '    // mobile keeps the dropdown tray.\n'
         '    const side = document.getElementById("facet-side");\n'
         '    const panel = (side && window.matchMedia("(min-width:768px)").matches) ? side : $("#filter-panel");\n'
         '    if (!panel) return;',
         "sidebar-target"),
    ], version="02")

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
