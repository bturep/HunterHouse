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
  lab-b.html  = a + the grouped list: opens grouped by COLLECTION (the
              fonds-level bins, authored order), contracted by default,
              sticky collapsible headers; v09 = headers ONLY (no item peek),
              each with an authored equal-word-count gloss ending in a
              contents list; Phase grouping stays available via the Phase
              sort; an active search auto-expands all groups.
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
SRC_VERSION = "v1.09-test.79"

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
  .ph-head{cursor:pointer}   /* v23: rails replace sticky headers */
  .ph-head:hover span:first-child{color:var(--ink)}
  .ph-chev{display:inline-block;width:14px;color:var(--muted)}
  .ph-head.closed{border-bottom-style:dashed}
  /* v09: header gloss only — authored, equal word count, no peek rows */
  .ph-gloss{display:block;font-family:var(--mono);font-size:9px;letter-spacing:0.05em;text-transform:none;color:var(--muted);margin:3px 0 0 0;white-space:normal;line-height:1.5}
  /* v21: THREE tonal tiers (Brandon) — with several collections open the
     header block read too much like the item block. Ladder: chrome
     (Catalogue / filter / search) = plain ground; collection headers =
     var(--soft), a clear step up, open or closed; rows + their sort strip
     = the faint ink tint between. Hover/selected sit on top (later in
     the cascade). */
  .phase-divider.ph-head{background:var(--soft)}
  .bin-sort,.row.in-bin{background:color-mix(in srgb, var(--bg) 96.5%, var(--ink))}
  /* v22: collection SPINE — a 2px left rule in the collection facet's
     sienna runs down every header and through each open block (header,
     sort strip, rows: one continuous line), so mid-scroll you are never
     in unmarked territory. Closed headers carry a short tick of the same
     line. 2px, not an indent — horizontal space stays whole. Composes
     with the v21 tiers; either dial can be turned off alone. */
  /* v24: the spine DESCRIBES something now — it marks the extent of an
     OPEN collection only (header, strip, rows, and its rail shadow).
     Closed bars carry a transparent stub so text never shifts. */
  .phase-divider.ph-head,.bin-sort,.row.in-bin{border-left:2px solid transparent}
  .ph-head:not(.closed),.bin-sort,.row.in-bin{border-left-color:#7a4020}
  html.dark .ph-head:not(.closed),html.dark .bin-sort,html.dark .row.in-bin{border-left-color:#b08468}
  /* v23: bin RAILS — collections scrolled past stack compact at the top of
     the rows viewport, upcoming ones at the bottom: every archive block is
     always on screen in abbreviated, non-description form (chevron, code,
     count). Click a rail row to jump to that collection. Empty rails have
     zero height, so they never block the list. */
  #bin-rail-top,#bin-rail-bot{position:absolute;left:0;right:0;z-index:8;overflow:hidden}
  #bin-rail-bot{bottom:0}
  .br-row{display:flex;justify-content:space-between;align-items:center;height:25px;box-sizing:border-box;
    padding:0 20px 0 12px;background:var(--soft);border-bottom:1px solid var(--rule);
    border-left:2px solid transparent;cursor:pointer;
    font-family:var(--mono);font-size:10px;font-weight:500;letter-spacing:0.18em;text-transform:uppercase;color:var(--copper-deep)}
  .br-row.open{border-left-color:#7a4020}
  html.dark .br-row.open{border-left-color:#b08468}
  #bin-rail-bot .br-row{border-bottom:0;border-top:1px solid var(--rule)}
  .br-row .r{color:var(--muted);letter-spacing:0.06em;font-size:9px}
  .br-row:hover{color:var(--ink)}
  .br-row .ph-chev{display:inline-block;width:14px;color:var(--muted)}
  /* v23: the pip rides ABOVE the tinted blocks (was sliding behind them)
     but below the rails and the filter overlay. */
  .scroll-pip{z-index:7}
  /* ══ v25: dark-mode DEPTH LADDER (Brandon) — light = instrument, dark =
     viewing depth. Darkest to lightest: image stage (artifact floats in
     the deepest room) < item rows < collection bars < UI chrome (the
     surface you grip). Light mode already follows this logic (paper
     chrome, soft stage) and is untouched. All four steps stay inside the
     warm near-black family, one perceptible step apart. `html.dark body`
     outranks the base html.dark overrides that lightened the stage. ══ */
  html.dark body .pane-image,html.dark body .image-stage{background:#151311}
  html.dark body .bin-sort,html.dark body .row.in-bin{background:#1e1b19}
  html.dark body .phase-divider.ph-head,html.dark body .br-row{background:#252220}
  html.dark body .site-top,html.dark body .list-head,html.dark body .lp-search,
  html.dark body .meta-head,html.dark body .image-foot,html.dark body .panel-handle{background:#2b2823}
  html.dark body .panel-handle::before{background:#8a847c}
  /* v17: hanging indent — a long collection name (CAA, FRH) wraps back to
     the panel edge under the chevron. Chevron gets its own column; the name
     wraps within its column; the gloss sits aligned beneath the name. */
  .ph-head > span:first-child{display:grid;grid-template-columns:14px 1fr;align-items:baseline}
  .ph-head .ph-gloss{grid-column:2}
  /* v10: panel handle = PULL TAB (Brandon 2026-07-11). The base handle is an
     innie straddling the panel edge, which merges visually with the list
     scroll bar. Here it sits fully OUTSIDE the edge on the image stage, panel-
     coloured with a rule border (none on the attached side, so it reads as one
     piece with the panel) and an always-visible grip line in place of the
     hover chevron. */
  .panel-handle{width:12px;height:44px;background:var(--bg);border:1px solid var(--rule)}
  .panel-left .panel-handle{right:-13px;border-left:0;border-radius:0 4px 4px 0}
  .panel-right .panel-handle{left:-13px;border-right:0;border-radius:4px 0 0 4px}
  .panel-handle::before{content:"";width:1px;height:14px;background:var(--muted);transition:background 0.15s}
  .panel-handle:hover{background:var(--bg)}
  .panel-handle:hover::before{background:var(--ink)}
  .panel-handle .handle-chevron{display:none}
  /* v18: the panels clip at their edge (overflow:hidden on .pane-list /
     .pane-meta), which swallowed the outie tab entirely — the panes lost
     their open/close affordance. Content containment lives one level down
     on .panel-content, so the panel frame itself can be visible. */
  .panel-left.pane-list,.panel-right.pane-meta{overflow:visible}
  /* v12: CATALOGUE alone on the header line; FILTER lives in the search
     row below, separated from the input by a rule. v13: the .l styles are
     scoped to .list-head, so out here the button needs the full flat
     treatment itself (native button chrome was showing as a box). */
  .lh-title{cursor:default}
  .lh-filter{
    font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:0.18em;
    text-transform:uppercase;color:var(--muted);cursor:pointer;
    display:flex;align-items:center;gap:6px;
    background:none;border:0;padding:0 12px 0 0;flex-shrink:0;
    border-right:1px solid var(--rule);border-radius:0;
  }
  .lh-filter .filter-chevron{font-size:13px;color:var(--muted);letter-spacing:0;font-weight:400;line-height:1}
  .lh-filter:hover,.lh-filter.fp-open{color:var(--ink)}
  .lh-filter:hover .filter-chevron,.lh-filter.fp-open .filter-chevron{color:var(--ink)}
  /* v24: tighten the seam under the filter/search row — its 8px bottom
     padding + rule read as a gap above the first collection bar. The
     bar's own soft edge is the separator now. Overlay top follows. */
  .lp-search{border-bottom:0;padding-bottom:4px}
  @media (min-width:768px){ .filter-panel{top:69px} }
  /* v14/v19: the sort keys are column headers on the row grid (104px /
     1fr / 50px); v19 renders one strip per OPEN bin, under its header,
     dashed like the rows it governs. */
  .pane-list .sort-mini{
    display:grid;grid-template-columns:104px 1fr 50px;gap:12px;
    padding:6px 20px;border-bottom:1px dashed var(--rule);flex-shrink:0;
  }
  .pane-list .sort-mini .sort-hd{justify-content:flex-start}
  /* v15: Phase sort retired for now — the phase labels aren't worked out
     yet and sort illogically (alphabetic). Hidden, not removed, so the
     wiring stays intact for reintegration later. */
  .pane-list .sort-mini .sort-hd[data-sort-col="phase"]{display:none}
  .pane-list .sort-mini .sort-hd[data-sort-col="year"]{width:auto;justify-content:flex-end;grid-column:3}
  /* mobile: the row survives for the FILTER control alone — the filter
     panel carries its own search field on mobile. */
  @media (max-width:767px){
    .lp-search{display:flex}
    .lp-search .pfx,.lp-search input{display:none}
    .lh-filter{border-right:0}
  }
  /* v11: applied-filter pills = the browse chips' bracket convention —
     no box, per-category colour (pc-*), the removal \u00d7 inside the brackets. */
  .af-pill{font-family:var(--mono);font-size:11px;font-weight:400;letter-spacing:0.02em;
    text-transform:capitalize;line-height:1.6;background:transparent;border:0;
    padding:0;border-radius:0;color:var(--pf,var(--ink))}
  .af-pill::before{content:"["}
  .af-pill::after{content:"]"}
  .af-pill:hover{opacity:0.75}
  .af-pill .x{margin-left:5px;color:var(--muted)}
  .af-pill:hover .x{color:var(--red-deep)}
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
    // LAB B: the COLLECTIONS are the shape (Brandon, 2026-07-10 tuning) — the
    // fonds-level buckets in authored order. v09 (Brandon, 2026-07-11):
    // headers ONLY — no item peek. Each header carries an authored gloss:
    // EXACTLY 12 words each (equal length is the design constraint; keep
    // parity when editing), a tight description ending in a semicolon list
    // of contents. Never derived, never truncated. A live search still
    // auto-expands everything.
    const GLOSS = {
      CAA: "Richard Hunter's career donations to the University of Calgary, 1955–2010. Drawings; photographs.",
      HHC: "The residence's own record, passed with the house in 2024. Drawings; documents.",
      IHC: "Ivan Hunter's first photographic survey of the residence, captured February 2024. Photographs.",
      EGC: "Furniture drawings gifted to cabinetmaker Eric Gesinger, photographed in situ. Drawings; photographs.",
      FRH: "Papers of Frances Hunter; correspondence gated to researchers. Photographs; invitations; flyers; programs.",
      FUL: "John Fulker's photographs, held at the West Vancouver Museum; catalogue pending. Photographs.",
    };
    const gkeyOf = it => (state.sortCol !== "phase"
      ? (archiveAbbrev(collectionOf(it)) || "—")
      : (it.phase || "—"));
    const glabelOf = k => (state.sortCol !== "phase" && COLLECTION_INFO[k]?.title)
      ? `${k} — ${COLLECTION_INFO[k].title}` : k;
    const glossOf = k => (state.sortCol !== "phase" && GLOSS[k]) || "";
    const searchOpen = !!state.search.trim();
    let groupOpen = true;
    state.filtered.forEach((it, _idx) => {
      const gkey = gkeyOf(it);
      if (grouped && gkey !== lastPhase) {
        lastPhase = gkey;
        const count = state.filtered.filter(x => gkeyOf(x) === gkey).length;
        const d = document.createElement("div");
        const open = searchOpen || phaseExpanded.has(gkey);
        d.className = "phase-divider ph-head" + (open ? "" : " closed");
        d.dataset.phase = gkey;
        d.dataset.count = String(count).padStart(2,"0");   // v23: the rails read this
        const gloss = glossOf(gkey);
        d.innerHTML = `<span><span class="ph-chev">${open ? "\\u2304" : "\\u203a"}</span>${escapeHTML(glabelOf(gkey))}${gloss ? `<span class="ph-gloss">${escapeHTML(gloss)}</span>` : ""}</span><span class="r">${String(count).padStart(2,"0")} items</span>`;
        d.addEventListener("click", () => {
          if (phaseExpanded.has(gkey)) phaseExpanded.delete(gkey); else phaseExpanded.add(gkey);
          renderList();
        });
        frag.appendChild(d);
        groupOpen = open;
        if (open) {   // v19: sort keys live INSIDE the open bin, under its header
          const ss = document.createElement("div");
          ss.className = "sort-mini bin-sort";
          [["id","ID"],["year","Year"]].forEach(([col, lbl]) => {
            const b = document.createElement("button");
            b.className = "sort-hd" + (state.sortCol === col ? " active" : "");
            b.dataset.sortCol = col;
            b.innerHTML = `${lbl}<span class="sort-arrow">${state.sortCol === col ? (state.sortDir === "asc" ? "\u2191" : "\u2193") : ""}</span>`;
            b.addEventListener("click", e => {
              e.stopPropagation();
              if (state.sortCol === col) state.sortDir = state.sortDir === "asc" ? "desc" : "asc";
              else { state.sortCol = col; state.sortDir = "asc"; }
              applyFilters(); renderList();
              const url = new URL(location.href);
              url.searchParams.set("sort", state.sortCol);
              url.searchParams.set("dir", state.sortDir);
              history.replaceState({}, "", url);
            });
            ss.appendChild(b);
          });
          frag.appendChild(ss);
        }
      }
      if (grouped && !groupOpen) return;   // v09: contracted = header only, no peek
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
  /* v03: the record covers the ENTIRE preview pane as a near-opaque veil —
     the image ghosts through behind the text; no floating card chrome. */
  #rec-card{position:absolute;inset:0;z-index:60}
  #rec-card[hidden]{display:none}
  .rcc-scrim{position:absolute;inset:0;background:color-mix(in srgb, var(--bg) 93%, transparent)}
  .rcc-card{position:relative;height:100%;width:100%;overflow-y:auto;
    background:transparent;border:0;box-shadow:none;padding:46px 58px 40px}
  .rcc-body{max-width:560px}
  .rcc-x{position:fixed;position:absolute;top:14px;right:20px;background:none;border:0;font-size:18px;color:var(--muted);cursor:pointer;line-height:1}
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

def build(lab, css_extra, extra_patches, version, tray=True):
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
    if tray:   # lab-b opted back to the full-height pane (Brandon 2026-07-11)
        text = patch(text, OLD_FILTER_PANEL_CSS, NEW_FILTER_PANEL_CSS, "tray-css")

    # Authored collection order (Brandon 2026-07-10): CAA, HHC, IHC, EGC, FRH —
    # replaces alphabetical-with-EGC-last. Unknown future collections fall to
    # the end alphabetically. All labs share the tray.
    text = patch(text,
        '    // Collections in the filter panel mirror the catalogue list\'s order:\n'
        '    // tail collections (EGC) sort to the bottom regardless of alphabet.\n'
        '    const uniqueCollections = [...new Set(\n'
        '      state.items.map(i => archiveAbbrev(collectionOf(i))).filter(Boolean)\n'
        '    )].sort((a, b) =>\n'
        '      (isTailCollection(a) ? 1 : 0) - (isTailCollection(b) ? 1 : 0)\n'
        '      || a.localeCompare(b)\n'
        '    );',
        '    // LAB: authored collection order (Brandon 2026-07-10).\n'
        '    const COLL_ORDER = ["CAA", "HHC", "IHC", "EGC", "FRH"];\n'
        '    const uniqueCollections = [...new Set(\n'
        '      state.items.map(i => archiveAbbrev(collectionOf(i))).filter(Boolean)\n'
        '    )].sort((a, b) => {\n'
        '      const ra = COLL_ORDER.indexOf(a), rb = COLL_ORDER.indexOf(b);\n'
        '      return (ra === -1 ? 99 : ra) - (rb === -1 ? 99 : rb) || a.localeCompare(b);\n'
        '    });',
        "collection-order")

    # Collection chips carry their full names ("HHC — Hunter House Collection")
    # — the bare abbreviations don't tell a visitor what a collection contains
    # (Brandon, 2026-07-10 review of lab-a). All labs share the tray.
    text = patch(text,
        '        const n = match ? base.filter(it => match(it, v)).length : 0;\n'
        '        const zero = n === 0 && !activeSet.has(v);   // active chips stay clickable (to deselect)\n'
        '        const chip = `<button class="fp-chip${activeSet.has(v) ? " on" : ""}${zero ? " zero" : ""}${pc}" data-${attr}="${escapeHTML(v)}">${escapeHTML(v)}<span class="fp-ct">${n}</span></button>`;',
        '        const n = match ? base.filter(it => match(it, v)).length : 0;\n'
        '        const zero = n === 0 && !activeSet.has(v);   // active chips stay clickable (to deselect)\n'
        '        const lbl = (attr === "collection" && COLLECTION_INFO[v]?.title) ? `${v} — ${COLLECTION_INFO[v].title}` : v;   // LAB: legible collections\n'
        '        const chip = `<button class="fp-chip${activeSet.has(v) ? " on" : ""}${zero ? " zero" : ""}${pc}" data-${attr}="${escapeHTML(v)}">${escapeHTML(lbl)}<span class="fp-ct">${n}</span></button>`;',
        "collection-names")
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
    build("a", "", [], version="08")

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
         '    const grouped = !state.curation;   // LAB B v16: the bins ARE the list — sorting reorders within them, never dissolves them',
         "grouped-trigger"),
        # ID sort orders groups by the authored collection order (CAA, HHC,
        # IHC, EGC, FRH), IDs ascending within each group. Replaces tailLast
        # for the id column — the authored order decides EGC's place now.
        ('      "id":    tailLast((a, b) => dir * (a.id || "").localeCompare(b.id || "")),',
         '      "id":    ((a, b) => {   // LAB B: authored collection order, then ID\n'
         '        const rank = x => { const i = ["CAA","HHC","IHC","EGC","FRH"].indexOf(archiveAbbrev(collectionOf(x))); return i === -1 ? 99 : i; };\n'
         '        return (rank(a) - rank(b)) || dir * (a.id || "").localeCompare(b.id || "");\n'
         '      }),',
         "id-collection-order"),
        # v16: Year must sort WITHIN the bins, not dissolve them into a flat
        # global list — collection rank leads, date decides inside each bin.
        ('      "year":  tailLast((a, b) => dir * dateKey(a).localeCompare(dateKey(b)) || (a.id||"").localeCompare(b.id||"")),',
         '      "year":  ((a, b) => {   // LAB B v16: collection bins first, date within\n'
         '        const rank = x => { const i = ["CAA","HHC","IHC","EGC","FRH"].indexOf(archiveAbbrev(collectionOf(x))); return i === -1 ? 99 : i; };\n'
         '        return (rank(a) - rank(b)) || dir * dateKey(a).localeCompare(dateKey(b)) || (a.id||"").localeCompare(b.id||"");\n'
         '      }),',
         "year-within-bins"),
        # v20: rows rendered under grouping are always in an OPEN bin (closed
        # bins return before row creation) — tag them so the block can tint.
        ('      row.className = "row" + (it.id === state.selectedId ? " sel" : "")',
         '      row.className = "row" + (grouped ? " in-bin" : "") + (it.id === state.selectedId ? " sel" : "")',
         "row-in-bin"),
        (OLD_PHASE_DIVIDER, NEW_PHASE_DIVIDER_B, "collapsible-headers"),
        # v10: curated row label (Brandon 2026-07-11).
        ('<div class="fp-lbl">Curators</div>',
         '<div class="fp-lbl">Curated selections by</div>',
         "curators-label"),
        # v11/v12: "Browse items" was doing double duty as the pane title AND
        # the filter toggle — vague. v12: CATALOGUE stands alone on the header
        # line (v11's inline pair read as one phrase); FILTER moves into the
        # search row below, so the two narrowing tools share a line. The
        # #filter-toggle id travels with the button so all wiring holds.
        ('        <button class="l" id="filter-toggle" title="Filter">Browse items<span class="filter-badge" id="filter-badge"></span><span class="filter-chevron">\u203a</span></button>',
         '        <span class="l lh-title">Catalogue</span>',
         "catalogue-title"),
        ('      <div class="lp-search" id="lp-search">\n        <span class="pfx">/</span>',
         '      <div class="lp-search" id="lp-search">\n'
         '        <button class="l lh-filter" id="filter-toggle" title="Filter">Filter<span class="filter-badge" id="filter-badge"></span><span class="filter-chevron">\u203a</span></button>\n'
         '        <span class="pfx">/</span>',
         "filter-into-search-row"),
        # v23: rail containers — siblings of #rows inside .panel-content.
        ('      <div class="rows" id="rows"></div>',
         '      <div class="rows" id="rows"></div>\n'
         '      <div id="bin-rail-top" aria-hidden="true"></div>\n'
         '      <div id="bin-rail-bot" aria-hidden="true"></div>',
         "bin-rail-markup"),
        # v23: rails logic rides on updatePip, which already fires on every
        # list render, scroll and resize; pip track top derives from the
        # scroller's real offset (was hardcoded 41px — in this lab the rows
        # start lower, so the pip bled into the filter/search row).
        ('  function updatePip(scrollId, pipId) {\n    const scrollEl = document.getElementById(scrollId);',
         '  const BR_H = 25;   // LAB B v23: rail row height\n'
         '  function updateBinRails() {\n'
         '    const rows = document.getElementById("rows");\n'
         '    const railT = document.getElementById("bin-rail-top");\n'
         '    const railB = document.getElementById("bin-rail-bot");\n'
         '    if (!rows || !railT || !railB) return;\n'
         '    const heads = [...rows.querySelectorAll(".ph-head")];\n'
         '    const rect  = rows.getBoundingClientRect();\n'
         '    railT.style.top = rows.offsetTop + "px";\n'
         '    const above = [];\n'
         '    for (const h of heads) {\n'
         '      if (h.getBoundingClientRect().top < rect.top + above.length * BR_H) above.push(h); else break;\n'
         '    }\n'
         '    const below = [];\n'
         '    for (let i = heads.length - 1; i >= 0; i--) {\n'
         '      const h = heads[i];\n'
         '      if (above.includes(h)) break;\n'
         '      if (h.getBoundingClientRect().bottom > rect.bottom - below.length * BR_H) below.unshift(h); else break;\n'
         '    }\n'
         '    const brRow = h => {\n'
         '      const el = document.createElement("div");\n'
         '      el.className = "br-row" + (h.classList.contains("closed") ? "" : " open");\n'
         '      el.innerHTML = `<span><span class="ph-chev">${h.classList.contains("closed") ? "\\u203a" : "\\u2304"}</span>${escapeHTML(h.dataset.phase || "")}</span><span class="r">${escapeHTML(h.dataset.count || "")}</span>`;\n'
         '      el.addEventListener("click", () => {\n'
         '        rows.scrollTop = h.offsetTop - rows.offsetTop - heads.indexOf(h) * BR_H;\n'
         '      });\n'
         '      return el;\n'
         '    };\n'
         '    railT.replaceChildren(...above.map(brRow));\n'
         '    railB.replaceChildren(...below.map(brRow));\n'
         '  }\n'
         '  // v24: re-run the pip after the left panel finishes its width\n'
         '  // transition — it gets sized during the splash-collapsed layout and\n'
         '  // can stay stale-active over a list that does not overflow.\n'
         '  document.getElementById("panel-left").addEventListener("transitionend", e => {\n'
         '    if (e.propertyName === "width") updatePip("rows", "list-pip");\n'
         '  });\n'
         '  function updatePip(scrollId, pipId) {\n'
         '    if (scrollId === "rows") updateBinRails();\n'
         '    const scrollEl = document.getElementById(scrollId);',
         "bin-rails-js"),
        ('    pip.style.top   = (41 + ratio * (trackHeight - thumbHeight)) + "px";',
         '    pip.style.top   = (scrollEl.offsetTop + ratio * (trackHeight - thumbHeight)) + "px";',
         "pip-track-offset"),
        # v14/v19: the sort keys leave the header line; v19 renders them
        # per-bin instead (inside each OPEN collection, under its header —
        # see NEW_PHASE_DIVIDER_B), so no static strip remains.
        ('        <div class="sort-mini">\n'
         '          <button class="sort-hd" data-sort-col="id">ID<span class="sort-arrow" id="sa-id"></span></button>\n'
         '          <button class="sort-hd" data-sort-col="phase">Phase<span class="sort-arrow" id="sa-phase"></span></button>\n'
         '          <button class="sort-hd" data-sort-col="year">Year<span class="sort-arrow" id="sa-year"></span></button>\n'
         '        </div>\n'
         '      </div>\n'
         '      <div class="lp-search" id="lp-search">',
         '      </div>\n'
         '      <div class="lp-search" id="lp-search">',
         "sort-out-of-head"),
        # v12: facet colours become a SPECTRUM (Brandon: a mixed set of
        # selected tags should read linearly). Tokens are recoloured so the
        # panel's existing group order — Collection, Areas, Item type,
        # Drawing type, Made by, Built status — runs warm\u2192cool: sienna,
        # ochre, olive, teal, navy, plum. The category\u2192class mapping is
        # untouched, so the record-pane pills recolour in lockstep by
        # construction. Also fixes drawtype navy \u2248 collection navy.
        ("""  .pc-sage  {--pf:#7a5820}  /* amber/ochre \u2014 areas */
  .pc-stone {--pf:#7a4020}  /* sienna \u2014 item type */
  .pc-slate {--pf:#284878}  /* steel blue \u2014 drawing type */
  .pc-clay  {--pf:#6a2068}  /* plum \u2014 creator */
  .pc-moss  {--pf:#386028}  /* olive \u2014 built status */
  .pc-indigo{--pf:var(--copper-deep)}
  .pc-denim {--pf:#283878}  /* navy \u2014 collection */""",
         """  .pc-denim {--pf:#7a4020}  /* LAB B spectrum 1 sienna \u2014 collection */
  .pc-sage  {--pf:#7a5820}  /* LAB B spectrum 2 ochre \u2014 areas */
  .pc-stone {--pf:#386028}  /* LAB B spectrum 3 olive \u2014 item type */
  .pc-slate {--pf:#1a6b70}  /* LAB B spectrum 4 teal \u2014 drawing type */
  .pc-clay  {--pf:#283878}  /* LAB B spectrum 5 navy \u2014 made by */
  .pc-moss  {--pf:#6a2068}  /* LAB B spectrum 6 plum \u2014 built status */
  .pc-indigo{--pf:var(--copper-deep)}""",
         "facet-spectrum-light"),
        ("""  html.dark .pc-sage  {--pf:#c09858}
  html.dark .pc-stone {--pf:#b09870}
  html.dark .pc-slate {--pf:#7898b8}
  html.dark .pc-clay  {--pf:#a07898}
  html.dark .pc-moss  {--pf:#88a070}
  html.dark .pc-denim {--pf:#6890a8}""",
         """  html.dark .pc-denim {--pf:#b08468}
  html.dark .pc-sage  {--pf:#c09858}
  html.dark .pc-stone {--pf:#88a070}
  html.dark .pc-slate {--pf:#68a8a0}
  html.dark .pc-clay  {--pf:#7898b8}
  html.dark .pc-moss  {--pf:#a07898}""",
         "facet-spectrum-dark"),
        # v11: applied-filter pills mirror the browse chips — same bracket
        # convention, same per-category colour — so the active filters above
        # the list read as the same objects the visitor just clicked.
        ('      bar.innerHTML =\n'
         '        `<span class="af-lbl">Filters</span>` +\n'
         '        AF_GROUPS.flatMap(([g, s]) => [...s].map(v =>\n'
         '          `<button class="af-pill" data-af-g="${g}" data-af-v="${escapeHTML(v)}">${escapeHTML(v)}<span class="x">\u00d7</span></button>`\n'
         '        )).join("") +',
         '      const AF_PC = { collection:PC.denim, area:PC.sage, itype:PC.stone,\n'
         '                      drawtype:PC.slate, creator:PC.clay, builtstatus:PC.moss };   // LAB B: chip colours\n'
         '      bar.innerHTML =\n'
         '        `<span class="af-lbl">Filters</span>` +\n'
         '        AF_GROUPS.flatMap(([g, s]) => [...s].map(v =>\n'
         '          `<button class="af-pill ${pillCls(AF_PC[g])}" data-af-g="${g}" data-af-v="${escapeHTML(v)}">${escapeHTML(v)}<span class="x">\u00d7</span></button>`\n'
         '        )).join("") +',
         "af-pill-brackets"),
    ], version="25", tray=False)

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
    ], version="05")

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
    ], version="05")

if __name__ == "__main__":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    main()
