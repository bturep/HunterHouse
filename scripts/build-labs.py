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
  /* ══ LAB B v40 — consolidated (design spec 7a + the v20-v39 system) ══ */
  /* — bin header (v40e): block layout replaces the base grid; chevron
     hangs in the gutter so name/gloss/ID/title share one left edge;
     count reads label-first; Year sort lives on the gloss line. — */
  .phase-divider.ph-head{display:block;position:relative;cursor:pointer;
    padding:13px 20px 13px;letter-spacing:normal;text-transform:none}   /* v58: same breathing as rows (14/20) */
  .ph-chev{position:absolute;left:6px;top:15px;font-size:11px;color:var(--muted)}
  .ph-head:hover .ph-chev{color:var(--ink)}
  .ph-head.closed{border-bottom-style:dashed}
  .ph-line1,.ph-line2{display:flex;justify-content:space-between;align-items:baseline;gap:14px}
  .ph-line2{margin-top:3px}
  .ph-name{font-family:var(--mono);font-size:12.5px;font-weight:500;letter-spacing:0.08em;text-transform:uppercase;color:var(--ink);line-height:1.35}   /* v59: back to 12.5 — hierarchy fixed by demoting the title instead */
  .ph-count{font-family:var(--mono);font-size:10.5px;letter-spacing:0.08em;text-transform:uppercase;color:var(--muted);white-space:nowrap}   /* v58: matches the rows' kicker size */
  .ph-count b{color:var(--ink);font-weight:500}
  .ph-gloss{font-family:var(--mono);font-size:9px;letter-spacing:0.04em;text-transform:none;color:var(--hint);line-height:1.5;white-space:normal;min-width:0}
  .ph-sort{font-family:var(--mono);font-size:10px;letter-spacing:0.08em;text-transform:uppercase;color:var(--ink);background:none;border:0;padding:0;cursor:pointer;white-space:nowrap}
  /* v61: the Year bar is gone entirely — authored order is the only
     ordering; sortCol "year" is unreachable from the UI (URL ?sort=year
     still honoured). */
  .ph-sort .sort-arrow{font-family:var(--mono);font-size:9px;display:inline-block;min-width:8px}
  /* — chrome toolbar (v40c): Catalogue · search · Filter share ONE row
     behind full-height separators. Catalogue demoted below the wordmark
     (v40d): chrome ranks by dimness+tracking, content by ink. — */
  .lp-toolbar{display:flex;align-items:center;gap:12px;height:41px;box-sizing:border-box;
    padding:0 20px 0 29px;background:var(--bg);flex-shrink:0;
    border-bottom:1px solid var(--rule)}   /* v66/v69: a TITLE BAR — explicit 41px, same as .meta-head (was padding-driven ~40) */
  /* v55: type hierarchy + one left edge — the wordmark reads above
     CATALOGUE (12.5 > 11.5), and Hunter House Archive / Catalogue /
     collection titles all start at x=29 (gutter + spine + padding). */
  .site-top{padding-left:29px;height:28px}   /* v70: the ENTRY frame gauge — 28px all round, the frame never changes between splash and archive (supersedes v63's 44) */
  .site-top .mk-static,.site-top .mk-page{font-size:12.5px}
  .lp-toolbar .lh-title{font-family:var(--mono);font-size:11.5px;font-weight:500;letter-spacing:0.10em;text-transform:uppercase;color:color-mix(in srgb, var(--ink) 72%, transparent);cursor:default}
  .lp-toolbar #lp-search-input{flex:1;min-width:0;background:none;border:0;outline:none;font-family:var(--mono);font-size:11px;letter-spacing:0.02em;color:var(--ink)}
  .lp-toolbar #lp-search-input::placeholder{color:var(--hint);text-transform:lowercase;letter-spacing:0.06em}
  .tb-vsep{width:1px;align-self:stretch;background:var(--rule);flex:none}
  .lh-filter{font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:0.12em;
    text-transform:uppercase;color:var(--muted);background:none;border:0;padding:0;border-radius:0;
    display:flex;align-items:center;gap:8px;cursor:pointer;flex-shrink:0}
  .lh-filter .filter-chevron{font-size:13px;color:var(--muted);letter-spacing:0;font-weight:400;line-height:1}
  .lh-filter:hover,.lh-filter.fp-open{color:var(--ink)}
  .lh-filter:hover .filter-chevron,.lh-filter.fp-open .filter-chevron{color:var(--ink)}
  /* active-tag row — exists only while filters are active ([hidden] via
     renderAfPills); clear-all folds inline after the last tag. */
  .lp-filter{padding:0 20px 12px;background:var(--bg);border-bottom:1px solid var(--rule)}
  #lf-pills{display:flex;flex-wrap:wrap;gap:3px 9px;align-items:baseline;min-width:0}
  #lf-pills .af-clear{font-family:var(--mono);font-size:10px;letter-spacing:0.10em;text-transform:uppercase;
    color:color-mix(in srgb, var(--muted) 40%, transparent);background:none;border:0;padding:0;margin-left:2px;cursor:pointer}
  #lf-pills .af-clear:hover{color:var(--muted)}
  @media (min-width:768px){ .panel-left .filter-panel{top:40px;bottom:28px} }   /* flush under the toolbar; stops above the foot like the ? pane */
  /* v57: the tray joins the pip system — native scrollbar hidden, pip in
     the slot, above the overlay. The Show action moves to the list foot
     while the tray is open; the overlay keeps only Clear all. */
  .filter-panel{scrollbar-width:none}
  .filter-panel::-webkit-scrollbar{display:none}
  #filter-pip{z-index:51}
  .fp-show{display:none}
  #lf-show{display:none;font-family:var(--mono);font-size:11px;font-weight:500;letter-spacing:0.12em;
    text-transform:uppercase;color:var(--ink);background:none;border:0;padding:0;cursor:pointer;margin-left:auto}
  #lf-show:hover{color:var(--copper-deep)}
  .panel-left:has(#filter-panel:not([hidden])) #lf-count{display:none}
  .panel-left:has(#filter-panel:not([hidden])) #lf-show{display:inline-flex}
  /* applied tags — the browse chips' bracket convention, category colour */
  .af-pill{font-family:var(--mono);font-size:11px;font-weight:400;letter-spacing:0.02em;
    text-transform:capitalize;line-height:1.6;background:transparent;border:0;
    padding:0;border-radius:0;color:var(--pf,var(--ink))}
  .af-pill::before{content:"["}
  .af-pill::after{content:"]"}
  .af-pill:hover{opacity:0.75}
  .af-pill .x{margin-left:5px;color:var(--muted)}
  .af-pill:hover .x{color:var(--red-deep)}
  /* — row (v40a/b/f): stacked block, all-mono, no separators — rhythm
     from padding; kicker holds ID (with the type mark) left, year right;
     subtitles wrap, never truncate. — */
  .pane-list .row{display:flex;flex-direction:column;align-items:stretch;gap:5px;padding:14px 20px;
    border-bottom:1px dashed color-mix(in srgb, var(--rule) 45%, transparent)}   /* v41: very light dashed dividers back between items */
  .pane-list .row:last-child,.pane-list .row.sel,.pane-list .row:has(+ .ph-head){border-bottom-color:transparent}
  .r-kick{display:flex;justify-content:space-between;align-items:baseline;font-family:var(--mono);font-size:10.5px;letter-spacing:0.06em}
  .r-kick .archid{font-size:10.5px;color:color-mix(in srgb, var(--ink) 72%, transparent)}
  .pane-list .row .year{font-family:var(--mono);font-size:10.5px;color:var(--muted);font-variant-numeric:tabular-nums}
  .r-title{font-family:var(--mono);font-size:12px;font-weight:500;letter-spacing:0.01em;color:var(--ink);line-height:1.45}   /* v59: below the 12.5px collection name */
  .r-note{font-family:var(--mono);font-size:10.5px;color:var(--hint);line-height:1.5;white-space:normal}
  /* — all-mono BOTH panes (Brandon): the record pane joins the list — */
  .panel-right .panel-content{font-family:var(--mono)}
  .panel-right.pane-meta .meta-title{font-family:var(--mono);font-size:14px;letter-spacing:0.01em;line-height:1.5}   /* v59: scaled to the new list (title 12 / collection 12.5) */
  .pane-meta .kv dd{font-size:12px}
  .graph-path .node .lbl{font-family:var(--mono);letter-spacing:0.01em}
  /* — tonal tiers (v21) + depth ladder (v25-v29): chrome > collections >
     rows > stage, warm near-black family (wider v28 steps reverted). — */
  .phase-divider.ph-head{background:var(--soft)}
  .row.in-bin{background:color-mix(in srgb, var(--bg) 96.5%, var(--ink))}
  html.dark body .pane-image,html.dark body .image-stage{background:#191614}   /* v55: stage lifted a touch; the chosen item matches it */
  html.dark body .row.in-bin{background:#1e1b19}
  html.dark body .phase-divider.ph-head,html.dark body .br-row{background:#252220}
  html.dark body .site-top,html.dark body .lp-toolbar,html.dark body .lp-filter,
  html.dark body .meta-head,html.dark body .image-foot,html.dark body .panel-handle{background:#2b2823}
  html.dark body .panel-handle::before{background:#8a847c}
  html.dark body .panel-right{background:#2b2823}
  html.dark body .panel-left{background:#2b2823}
  /* — spine (v22/v24): sienna marks the extent of an OPEN collection —
     header, rows, rail shadow; closed bars carry a transparent stub. — */
  /* v62: each collection owns a colour — spine, selection lines and rail
     ticks inherit it via --bin (fallback: the copper green). Identity
     colour, not facet coding: the tray's category chips stay as they are. */
  [data-phase="CAA"],[data-bin="CAA"]{--bin:#7a4020}
  [data-phase="HHC"],[data-bin="HHC"]{--bin:#4f7a6b}
  [data-phase="IHC"],[data-bin="IHC"]{--bin:#284878}
  [data-phase="EGC"],[data-bin="EGC"]{--bin:#7a5820}
  [data-phase="FRH"],[data-bin="FRH"]{--bin:#6a2068}
  html.dark [data-phase="CAA"],html.dark [data-bin="CAA"]{--bin:#b08468}
  html.dark [data-phase="HHC"],html.dark [data-bin="HHC"]{--bin:#7aaa98}
  html.dark [data-phase="IHC"],html.dark [data-bin="IHC"]{--bin:#7898b8}
  html.dark [data-phase="EGC"],html.dark [data-bin="EGC"]{--bin:#c09858}
  html.dark [data-phase="FRH"],html.dark [data-bin="FRH"]{--bin:#a07898}
  .phase-divider.ph-head,.row.in-bin{border-left:2px solid transparent}
  .ph-head:not(.closed),.row.in-bin{border-left-color:color-mix(in srgb, var(--bin, var(--copper)) 55%, transparent)}
  /* — selection (v30/v39): the row in the viewer sinks to stage depth;
     the box opens right, spine carries the left, sienna lines top+bottom. — */
  .pane-list .row.sel{background:var(--soft);
    box-shadow:inset 0 1px 0 color-mix(in srgb, var(--bin, var(--copper)) 55%, transparent),
               inset 0 -1px 0 color-mix(in srgb, var(--bin, var(--copper)) 55%, transparent)}
  /* v60: the spine runs THROUGH the selection as its left edge — same
     2px, same copper, seamless; the top/bottom lines meet it. */
  .pane-list .row.sel::before{display:none}   /* v58: the base 3px red indicator was the real extra left thickness */
  html.dark body .row.sel{background:#191614}
  /* — bin rail (v23/v32): passed collections stack compact at the top;
     the pane ends in a 41px chrome foot carrying the item count (v33). — */
  #bin-rail-top{position:absolute;left:7px;right:7px;z-index:8;overflow:hidden}
  .br-row{display:flex;justify-content:space-between;align-items:center;height:25px;box-sizing:border-box;
    padding:0 20px 0 12px;background:var(--soft);border-bottom:1px solid var(--rule);
    border-left:2px solid transparent;cursor:pointer;
    font-family:var(--mono);font-size:10px;font-weight:500;letter-spacing:0.18em;text-transform:uppercase;color:var(--copper-deep)}
  .br-row.open{border-left-color:color-mix(in srgb, var(--bin, var(--copper)) 55%, transparent)}
  .br-row .r{color:var(--muted);letter-spacing:0.06em;font-size:9px}
  .br-row:hover{color:var(--ink)}
  .br-row .ph-chev{position:static;display:inline-block;width:14px;font-size:10px;color:var(--muted)}
  #list-foot{height:28px;box-sizing:border-box;flex-shrink:0;border-top:1px solid var(--rule);background:var(--bg);
    display:flex;align-items:center;padding:0 20px;
    font-family:var(--mono);font-size:10px;color:var(--muted);letter-spacing:0.06em}
  html.dark body #list-foot{background:#2b2823}
  /* — pip slot + mirrored gutters (v35/v37/v38); v42 extends the same
     slots to the record pane — content inset between two 7px lanes, the
     meta pip runs in the inner one. Chrome (head, data footer) stays
     full-width. — */
  .scroll-pip{z-index:7}
  .shell .scroll-pip.active{opacity:0.22}   /* v52: quieter pips (base 0.4); outranks the later base rule */
  #rows{margin:0 7px}
  /* v43: the inset record body also takes the collections-tier tone —
     a recessed content block within the chrome panel, same step as the
     collection bars on the left. */
  .pane-meta .meta-body{margin:0 7px;background:var(--soft)}
  html.dark body .pane-meta .meta-body{background:#252220}
  /* v44: no rule under ITEM RECORD — the recessed body's own edge is the
     separator, mirroring the left toolbar's seamless seam. */
  .pane-meta .meta-head{border-bottom:1px solid var(--rule)}   /* v66: title bar again — reverses v44/v47; the recessed body changed what the line sits against */
  .pane-meta .meta-head .l{color:color-mix(in srgb, var(--ink) 72%, transparent)}   /* v52: same white intensity as CATALOGUE */
  /* v45/v49: the technical links live at the end of the SCROLL, quiet;
     the pane still ENDS in a 41px chrome foot — empty frame, continuing
     the bottom line across all three panes. */
  .meta-foot{height:28px;box-sizing:border-box;flex-shrink:0;border-top:1px solid var(--rule);background:var(--bg);
    display:flex;align-items:center;justify-content:flex-end;gap:16px;padding:0 22px}
  html.dark body .meta-foot{background:#2b2823}
  /* v50/v53: only the ? lives here (Aa + fullscreen went home to the top
     bar). The info pane occupies the ITEM RECORD space — it stops above
     this foot — and while it is open the ? reads as \u2715 in the exact
     same spot: open and close share one location. */
  .meta-foot button{background:none;border:0;padding:0;cursor:pointer;color:var(--ink);
    font-family:var(--mono);font-weight:500;line-height:1;display:inline-flex;align-items:center}
  .meta-foot button:hover{opacity:0.5}
  .meta-foot #rec-info{font-size:14px}
  .panel-right #info-pane{bottom:28px}
  /* v56: signed-out unlock lives in ? now, not under the record */
  body:not(.is-researcher) #meta-content #rn-panel{display:none}
  #rn-unlock-ip{margin-top:22px;padding-top:16px;border-top:1px solid var(--rule)}
  .panel-right #info-pane-close{display:none}
  #panel-right:has(#info-pane.open) #rec-info{font-size:0}
  #panel-right:has(#info-pane.open) #rec-info::after{content:"\u2715";font-size:13px}
  #meta-content{display:flex;flex-direction:column;flex:1}
  .pane-meta .data-footer{height:auto;background:transparent;border-top:1px solid var(--rule);
    padding:14px 0 2px;margin-top:28px;display:flex;flex-wrap:wrap;gap:12px 14px}
  /* — top-right cluster separators (v33) — */
  .tr-vsep{width:1px;align-self:stretch;background:var(--rule);flex:none}
  .site-topright .tr-div{height:auto;align-self:stretch}
  /* — splash frame (v31) — */
  #splash-foot{position:fixed;left:0;right:0;bottom:0;height:28px;z-index:30;
    background:var(--bg);border-top:1px solid var(--rule);
    opacity:0;pointer-events:none;transition:opacity 240ms ease}
  body.hh-splash #splash-foot{opacity:1}
  html.dark body #splash-foot{background:#2b2823}
  /* — pull tabs (v10/v18) — */
  .panel-handle{width:12px;height:44px;background:var(--bg);border:1px solid var(--rule)}
  .panel-left .panel-handle{right:-13px;border-left:0;border-radius:0 4px 4px 0}
  .panel-right .panel-handle{left:-13px;border-right:0;border-radius:4px 0 0 4px}
  .panel-handle::before{content:"";width:1px;height:14px;background:var(--muted);transition:background 0.15s}
  .panel-handle:hover{background:var(--bg)}
  .panel-handle:hover::before{background:var(--ink)}
  .panel-handle .handle-chevron{display:none}
  .panel-left.pane-list,.panel-right.pane-meta{overflow:visible}
  /* v63/v68: feet at 28px — the collapsed sliver width; the frame is
     one dimension all round (slivers, feet, splash strip). */
  .pane-image .image-foot{height:28px}
  /* v63: the collapsed record sliver names itself — vertical label,
     whole sliver clickable (pull tab still works). Hidden during splash. */
  .panel-right.out{cursor:pointer}
  .panel-right.out::after{content:"ITEM RECORD";position:absolute;top:50%;left:50%;
    transform:translate(-50%,-50%);writing-mode:vertical-rl;white-space:nowrap;
    font-family:var(--mono);font-size:10px;font-weight:500;letter-spacing:0.18em;
    text-transform:uppercase;color:var(--muted);pointer-events:none}
  body.hh-splash .panel-right.out::after{content:none}
  /* v64: the catalogue sliver gets the same treatment */
  .panel-left.out{cursor:pointer}
  .panel-left.out::after{content:"CATALOGUE";position:absolute;top:50%;left:50%;
    transform:translate(-50%,-50%);writing-mode:vertical-rl;white-space:nowrap;
    font-family:var(--mono);font-size:10px;font-weight:500;letter-spacing:0.18em;
    text-transform:uppercase;color:var(--muted);pointer-events:none}
  body.hh-splash .panel-left.out::after{content:none}
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
    // LAB B: the COLLECTIONS are the shape. v40 (design 7a): chevron hangs
    // in the gutter; name, gloss, ID and title share one left edge; count
    // reads label-first; the Year control lives on the gloss line and
    // cycles year-asc \u2192 year-desc \u2192 authored default (collection
    // order, ID ascending). Bins: contracted at rest, auto-open under
    // search/filter, manual close wins (v36). Glosses are AUTHORED —
    // exactly 12 words each, ending in a contents list; never derived.
    const GLOSS = {
      CAA: "Richard Hunter's career donations to the University of Calgary, 1955\u20132010. Drawings; photographs.",
      HHC: "The residence's own record, passed with the house in 2024. Drawings; documents.",
      IHC: "Ivan Hunter's first photographic survey of the residence, captured February 2024. Photographs.",
      EGC: "Furniture drawings gifted to cabinetmaker Eric Gesinger, photographed in situ. Drawings; photographs.",
      FRH: "Papers of Frances Hunter; correspondence gated to researchers. Photographs; invitations; flyers; programs.",
      FUL: "John Fulker's photographs, held at the West Vancouver Museum; catalogue pending. Photographs.",
    };
    const gkeyOf = it => (state.sortCol !== "phase"
      ? (archiveAbbrev(collectionOf(it)) || "\u2014")
      : (it.phase || "\u2014"));
    const glabelOf = k => (state.sortCol !== "phase" && COLLECTION_INFO[k]?.title)
      ? `${k} \u2014 ${COLLECTION_INFO[k].title}` : k;
    const glossOf = k => (state.sortCol !== "phase" && GLOSS[k]) || "";
    const emd = t => t.replace(/ - /g, " \u2014 ");   // v40h: display-only em dashes
    const searchOpen = !!state.search.trim();
    let groupOpen = true;
    state.filtered.forEach((it, _idx) => {
      const gkey = gkeyOf(it);
      if (grouped && gkey !== lastPhase) {
        lastPhase = gkey;
        const count = state.filtered.filter(x => gkeyOf(x) === gkey).length;
        const d = document.createElement("div");
        const open = phaseExpanded.has(gkey) || ((searchOpen || afActive) && !phaseCollapsed.has(gkey));   // v36/v48: contracted at rest; search/filter auto-open; manual close wins
        d.className = "phase-divider ph-head" + (open ? "" : " closed");
        d.dataset.phase = gkey;
        d.dataset.count = String(count).padStart(2,"0");   // the rail reads this
        const gloss = glossOf(gkey);
        const yrOn = state.sortCol === "year";
        d.innerHTML =
          `<span class="ph-chev">${open ? "\u2304" : "\u203a"}</span>` +
          `<span class="ph-line1"><span class="ph-name">${escapeHTML(glabelOf(gkey))}</span><span class="ph-count">Items <b>${String(count).padStart(2,"0")}</b></span></span>` +
          `<span class="ph-line2"><span class="ph-gloss">${gloss ? escapeHTML(gloss) : ""}</span></span>`;
        d.addEventListener("click", () => {
          if (open) { phaseExpanded.delete(gkey); phaseCollapsed.add(gkey); }
          else { phaseCollapsed.delete(gkey); phaseExpanded.add(gkey); }
          renderList();
        });
        frag.appendChild(d);
        groupOpen = open;
      }
      if (grouped && !groupOpen) return;   // contracted = header only
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
         "  const phaseExpanded = new Set();    // LAB B: opened groups (contracted by default, session-scope)\n"
         "  const phaseCollapsed = new Set();   // LAB B v36: manual closes that override auto-open (search/filter)\n"
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
         '      row.dataset.bin = gkey;   // v62: collection identity drives the colour\n'
         '      row.className = "row" + (grouped ? " in-bin" : "") + (it.id === state.selectedId ? " sel" : "")',
         "row-in-bin"),
        (OLD_PHASE_DIVIDER, NEW_PHASE_DIVIDER_B, "collapsible-headers"),
        # v10: curated row label (Brandon 2026-07-11).
        ('<div class="fp-lbl">Curators</div>',
         '<div class="fp-lbl">Curated selections by</div>',
         "curators-label"),
        # v51: no curated selections in this lab — the For Theodora row is
        # a next.html concern (the live mentor preview link); the lab skips
        # loading the index entirely, so the row never renders.
        ('      await loadCurationIndex();   // populate [Curated] entry (tiny local JSON; no-op if absent)',
         '      // LAB B v51: curation index not loaded — no curated-selections row in this lab.',
         "no-curations"),
        # v56: Guided tour + Platform sections leave the ? pane.
        ('      <p class="ip-grp">Guided tour</p>\n'
         '      <p class="ip-note"><a href="#" onclick="hhReplayTour();return false;">Replay the interface walkthrough \u21bb</a> \u2014 a quick, spotlit tour of the controls.</p>\n'
         '\n'
         '      <p class="ip-grp">Platform</p>\n'
         '      <p class="ip-note"><a href="https://hunterhouse.wikibase.cloud/wiki/Main_Page" target="_blank" rel="noopener">Wikibase Main Page \u2014 archive structure, rights &amp; endpoints \u2197</a></p>\n'
         '\n',
         '',
         "no-tour-platform"),
        # v56: research-mode unlock moves to the BOTTOM of the ? pane
        # (renderRN already takes a target panel id); the record pane's
        # signed-out unlock row is suppressed via CSS.
        ('        marking, and your own shortcuts.</p>`;\n'
         '    document.getElementById("ip-inner").innerHTML = html;',
         '        marking, and your own shortcuts.</p>\n'
         '      <div id="rn-unlock-ip"></div>`;\n'
         '    document.getElementById("ip-inner").innerHTML = html;\n'
         '    if (!rnSession()) renderRN(state.selectedId, "rn-unlock-ip");   // LAB B v56: unlock lives at the bottom of ?',
         "unlock-in-info"),
        # v40c: ONE chrome row — Catalogue · search · Filter behind full-
        # height separators; the active-tag row below exists only while
        # filters are active. #list-info survives for mobile. Replaces the
        # whole list-head + lp-search stack; ids travel so wiring holds.
        ('      <div class="list-head">\n'
         '        <button class="l" id="filter-toggle" title="Filter">Browse items<span class="filter-badge" id="filter-badge"></span><span class="filter-chevron">›</span></button>\n'
         '        <button id="list-info" type="button" title="About this archive" aria-label="About this archive">?</button>\n'
         '        <div class="sort-mini">\n'
         '          <button class="sort-hd" data-sort-col="id">ID<span class="sort-arrow" id="sa-id"></span></button>\n'
         '          <button class="sort-hd" data-sort-col="phase">Phase<span class="sort-arrow" id="sa-phase"></span></button>\n'
         '          <button class="sort-hd" data-sort-col="year">Year<span class="sort-arrow" id="sa-year"></span></button>\n'
         '        </div>\n'
         '      </div>\n'
         '      <div class="lp-search" id="lp-search">\n'
         '        <span class="pfx">/</span>\n'
         '        <input id="lp-search-input" type="text" placeholder="search archive" autocomplete="off" autocorrect="off" spellcheck="false" aria-label="Search the archive">\n'
         '      </div>\n'
         '      <div class="filter-panel" id="filter-panel" hidden></div>',
         '      <div class="lp-toolbar">\n'
         '        <span class="l lh-title">Catalogue</span>\n'
         '        <span class="tb-vsep" aria-hidden="true"></span>\n'
         '        <input id="lp-search-input" type="text" placeholder="search archive" autocomplete="off" autocorrect="off" spellcheck="false" aria-label="Search the archive">\n'
         '        <span class="tb-vsep" aria-hidden="true"></span>\n'
         '        <button class="l lh-filter" id="filter-toggle" title="Filter">Filter<span class="filter-badge" id="filter-badge"></span><span class="filter-chevron">›</span></button>\n'
         '        <button id="list-info" type="button" title="About this archive" aria-label="About this archive">?</button>\n'
         '      </div>\n'
         '      <div class="lp-filter" id="lp-filter" hidden><span id="lf-pills"></span></div>\n'
         '      <div class="filter-panel" id="filter-panel" hidden></div>',
         "toolbar"),
        # v45: the permalink/cite/data links move INTO the scrollable record
        # body (renderMeta rebuilds #meta-content, so the footer node
        # survives); the fixed bottom-right bar becomes one prominent
        # action: Show item record -> the item's static permalink page.
        ('      <div class="meta-body" id="meta-body">\n'
         '        <div class="empty">Select an item from the list</div>\n'
         '      </div>\n'
         '      <div class="data-footer" id="data-footer">\n'
         '        <a id="df-permalink" href="#" onclick="return false" style="opacity:0.4" title="Copy this item\'s permanent link">Permalink ⧉</a>\n'
         '        <a id="df-cite" href="#" onclick="return false" style="opacity:0.4" title="Copy a citation for this item">Cite ⧉</a>\n'
         '        <a id="df-wikibase" href="#" onclick="return false" style="opacity:0.4">Wikibase ↗</a>\n'
         '        <a id="df-sparql"   href="#" onclick="return false" style="opacity:0.4">SPARQL ↗</a>\n'
         '        <a id="df-json"     href="#" onclick="return false" style="opacity:0.4">JSON ↗</a>\n'
         '      </div>',
         '      <div class="meta-body" id="meta-body">\n'
         '        <div id="meta-content">\n'
         '          <div class="empty">Select an item from the list</div>\n'
         '        </div>\n'
         '        <div class="data-footer" id="data-footer">\n'
         '          <a id="df-permalink" href="#" onclick="return false" style="opacity:0.4" title="Copy this item\'s permanent link">Permalink ⧉</a>\n'
         '          <a id="df-cite" href="#" onclick="return false" style="opacity:0.4" title="Copy a citation for this item">Cite ⧉</a>\n'
         '          <a id="df-wikibase" href="#" onclick="return false" style="opacity:0.4">Wikibase ↗</a>\n'
         '          <a id="df-sparql"   href="#" onclick="return false" style="opacity:0.4">SPARQL ↗</a>\n'
         '          <a id="df-json"     href="#" onclick="return false" style="opacity:0.4">JSON ↗</a>\n'
         '        </div>\n'
         '      </div>\n'
         '      <div class="meta-foot" id="meta-foot">\n'
         '        <button id="rec-info" title="About this archive &amp; shortcuts [?]" aria-label="Info">?</button>\n'
         '      </div>',
         "record-foot-cta"),
        # v45: renderMeta writes into #meta-content so the in-scroll footer
        # survives rebuilds; the CTA follows the selected item.
        ('  function renderMeta(item) {\n    const body = $("#meta-body");',
         '  function renderMeta(item) {\n    const body = $("#meta-content");',
         "meta-content-target"),
        # v63: record pane defaults CLOSED again (Brandon) — Continue opens
        # only the left panel; the collapsed sliver carries a vertical
        # ITEM RECORD label and opens on click.
        ('      closeAboutPane();\n'
         '      leftP.classList.remove("out");\n'
         '      rightP.classList.remove("out");\n'
         '      syncFsBtn();',
         '      closeAboutPane();\n'
         '      leftP.classList.remove("out");   // LAB B v63: record stays collapsed by default\n'
         '      syncFsBtn();',
         "right-closed-default"),
        ('      document.getElementById("right-handle").addEventListener("click", () => { if (document.body.classList.contains("lens-info")) { closeInfoPane(); return; } togglePanel("right"); syncFsBtn(); });',
         '      document.getElementById("right-handle").addEventListener("click", () => { if (document.body.classList.contains("lens-info")) { closeInfoPane(); return; } togglePanel("right"); syncFsBtn(); });\n'
         '      document.getElementById("panel-right").addEventListener("click", e => {   // LAB B v63: the collapsed sliver opens the record\n'
         '        if (e.currentTarget.classList.contains("out") && !e.target.closest(".panel-handle")) { togglePanel("right"); syncFsBtn(); }\n'
         '      });\n'
         '      document.getElementById("panel-left").addEventListener("click", e => {   // LAB B v64: same for the catalogue sliver\n'
         '        if (e.currentTarget.classList.contains("out") && !e.target.closest(".panel-handle")) { togglePanel("left"); syncFsBtn(); }\n'
         '      });',
         "sliver-opens-record"),
        # v40b: the row restacks — kicker (ID + type mark left, year right),
        # title, note. Researcher furniture (flags, drag, curation seq) is
        # re-housed untouched; styling it is deferred (Brandon).
        ('        ${reorderHTML}\n        <span class="col-id">',
         '        ${reorderHTML}\n        <span class="r-kick">\n        <span class="col-id">',
         "row-kick-open"),
        ('        <div class="title-wrap">\n'
         '          <div class="title">${escapeHTML(it.title)}</div>\n'
         '          <div class="ph">${phSlotHTML}</div>\n'
         '        </div>\n'
         '        <span class="year">${escapeHTML(yearOf(it.date))}</span>',
         '        <span class="year">${escapeHTML(yearOf(it.date))}</span>\n'
         '        </span>\n'
         '        <div class="r-title">${emd(escapeHTML(it.title))}</div>\n'
         '        ${phSlotHTML ? `<div class="r-note">${emd(phSlotHTML)}</div>` : ""}',
         "row-restack"),
        # v23: rail containers — siblings of #rows inside .panel-content.
        ('      <div class="rows" id="rows"></div>',
         '      <div class="rows" id="rows"></div>\n'
         '      <div class="scroll-pip" id="filter-pip" aria-hidden="true"></div>\n'
         '      <div id="bin-rail-top" aria-hidden="true"></div>\n'
         '      <div id="list-foot"><span id="lf-count"></span><button id="lf-show" type="button" title="Apply and close the filter">Show \u2192</button></div>',
         "bin-rail-markup"),
        # v31: splash bottom strip — fixed, so DOM placement is free.
        ('</body>',
         '<div id="splash-foot" aria-hidden="true"></div>\n</body>',
         "splash-foot-markup"),
        # v23: rails logic rides on updatePip, which already fires on every
        # list render, scroll and resize; pip track top derives from the
        # scroller's real offset (was hardcoded 41px — in this lab the rows
        # start lower, so the pip bled into the filter/search row).
        ('  function updatePip(scrollId, pipId) {\n    const scrollEl = document.getElementById(scrollId);',
         '  const BR_H = 25;   // LAB B v23: rail row height\n'
         '  function updateBinRails() {\n'
         '    const rows = document.getElementById("rows");\n'
         '    const railT = document.getElementById("bin-rail-top");\n'
         '    if (!rows || !railT) return;\n'
         '    const heads = [...rows.querySelectorAll(".ph-head")];\n'
         '    const rect  = rows.getBoundingClientRect();\n'
         '    railT.style.top = rows.offsetTop + "px";\n'
         '    const above = [];\n'
         '    for (const h of heads) {\n'
         '      if (h.getBoundingClientRect().top < rect.top + above.length * BR_H) above.push(h); else break;\n'
         '    }\n'
         '    const brRow = h => {\n'
         '      const el = document.createElement("div");\n'
         '      el.className = "br-row" + (h.classList.contains("closed") ? "" : " open");\n'
         '      el.dataset.bin = h.dataset.phase;   // v62: identity colour\n'
         '      el.innerHTML = `<span><span class="ph-chev">${h.classList.contains("closed") ? "\\u203a" : "\\u2304"}</span>${escapeHTML(h.dataset.phase || "")}</span><span class="r">${escapeHTML(h.dataset.count || "")}</span>`;\n'
         '      el.addEventListener("click", () => {\n'
         '        rows.scrollTop = h.offsetTop - rows.offsetTop - heads.indexOf(h) * BR_H;\n'
         '      });\n'
         '      return el;\n'
         '    };\n'
         '    railT.replaceChildren(...above.map(brRow));\n'
         '  }\n'
         '  // v24: re-run the pip after the left panel finishes its width\n'
         '  // transition — it gets sized during the splash-collapsed layout and\n'
         '  // can stay stale-active over a list that does not overflow.\n'
         '  document.getElementById("panel-left").addEventListener("transitionend", e => {\n'
         '    if (e.propertyName === "width") updatePip("rows", "list-pip");\n'
         '  });\n'
         '  document.getElementById("panel-right").addEventListener("transitionend", e => {   // v49: same stale-size fix for the record pip\n'
         '    if (e.propertyName === "width") updatePip("meta-body", "meta-pip");\n'
         '  });\n'
         '  function updatePip(scrollId, pipId) {\n'
         '    if (scrollId === "rows") updateBinRails();\n'

         '    const scrollEl = document.getElementById(scrollId);',
         "bin-rails-js"),
        ('    pip.style.top   = (41 + ratio * (trackHeight - thumbHeight)) + "px";',
         '    pip.style.top   = (scrollEl.offsetTop + ratio * (trackHeight - thumbHeight)) + "px";',
         "pip-track-offset"),
        # v33: list-foot count — "252 items" at rest, "132 / 252 items" when
        # a filter or search narrows the list. Same source as mob-count.
        ('  function updateMobCount() {\n'
         '    const el = document.getElementById("mob-count");\n'
         '    if (!el) return;\n'
         '    const f = state.filtered.length, t = state.items.length;\n'
         '    el.textContent = (f < t) ? `${f} / ${t}` : `${t}`;\n'
         '  }',
         '  function updateMobCount() {\n'
         '    const f = state.filtered.length, t = state.items.length;\n'
         '    const txt = (f < t) ? `${f} / ${t}` : `${t}`;\n'
         '    const lf = document.getElementById("lf-count");   // LAB B v33: list-foot count\n'
         '    if (lf) lf.textContent = txt + " items";\n'
         '    const el = document.getElementById("mob-count");\n'
         '    if (!el) return;\n'
         '    el.textContent = txt;\n'
         '  }',
         "list-foot-count"),
        # v50: ?, Aa and fullscreen relocate to the bottom-right corner bar
        # (the meta foot); their top-bar homes are stripped here.
        ('    <button id="rec-info" title="About this archive &amp; shortcuts [?]" aria-label="Info">?</button>\n'
         '    <!-- Aa text-size toggle.',
         '    <!-- Aa text-size toggle.',
         "strip-rec-info"),

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
         """  html.dark .pc-denim {--pf:#aa8572}  /* v40g: ~40% toward warm grey */
  html.dark .pc-sage  {--pf:#aa9168}
  html.dark .pc-stone {--pf:#899676}
  html.dark .pc-slate {--pf:#769b93}
  html.dark .pc-clay  {--pf:#7f91a1}
  html.dark .pc-moss  {--pf:#977e8e}""",
         "facet-spectrum-dark"),
        # v34: the active tags live IN the filter row beside FILTER — no
        # separate bar above the list, no "Filters" label. Pills keep the
        # browse chips' bracket + per-category colour. clear-all binding
        # stays with the existing renderList code (it queries by id and
        # runs after these calls in both branches).
        ('    const afBar = () => {\n'
         '      const bar = document.createElement("div");\n'
         '      bar.className = "af-bar";\n'
         '      bar.innerHTML =\n'
         '        `<span class="af-lbl">Filters</span>` +\n'
         '        AF_GROUPS.flatMap(([g, s]) => [...s].map(v =>\n'
         '          `<button class="af-pill" data-af-g="${g}" data-af-v="${escapeHTML(v)}">${escapeHTML(v)}<span class="x">\u00d7</span></button>`\n'
         '        )).join("") +\n'
         '        `<button class="af-clear" id="filter-clear-all">\u2715 clear all</button>`;\n'
         '      bar.querySelectorAll(".af-pill").forEach(p => p.addEventListener("click", e => {\n'
         '        e.stopPropagation();\n'
         '        const set = new Map(AF_GROUPS).get(p.dataset.afG);\n'
         '        if (set) set.delete(p.dataset.afV);\n'
         '        applyFilters(); renderList(); updateFilterBadge(); renderFilterPanel();\n'
         '      }));\n'
         '      return bar;\n'
         '    };',
         '    const AF_PC = { collection:PC.denim, area:PC.sage, itype:PC.stone,\n'
         '                    drawtype:PC.slate, creator:PC.clay, builtstatus:PC.moss };   // LAB B: chip colours\n'
         '    const renderAfPills = () => {   // LAB B v34: pills render into the filter row\n'
         '      const slot = document.getElementById("lf-pills");\n'
         '      if (!slot) return;\n'
         '      const wrap = document.getElementById("lp-filter");\n'
         '      if (wrap) wrap.hidden = !afActive;   // v40: the tag row exists only while filters are active\n'
         '      if (!afActive) { slot.innerHTML = ""; return; }\n'
         '      slot.innerHTML =\n'
         '        AF_GROUPS.flatMap(([g, s]) => [...s].map(v =>\n'
         '          `<button class="af-pill ${pillCls(AF_PC[g])}" data-af-g="${g}" data-af-v="${escapeHTML(v)}">${escapeHTML(v)}<span class="x">\u00d7</span></button>`\n'
         '        )).join("") +\n'
         '        `<button class="af-clear" id="filter-clear-all">\u2715 clear all</button>`;\n'
         '      slot.querySelectorAll(".af-pill").forEach(p => p.addEventListener("click", e => {\n'
         '        e.stopPropagation();\n'
         '        const set = new Map(AF_GROUPS).get(p.dataset.afG);\n'
         '        if (set) set.delete(p.dataset.afV);\n'
         '        applyFilters(); renderList(); updateFilterBadge(); renderFilterPanel();\n'
         '      }));\n'
         '    };',
         "af-pills-in-filter-row"),
        ('      if (afActive) container.appendChild(afBar());',
         '      renderAfPills();',
         "af-call-empty"),
        # v67: no "Try a different search term" note — the empty state
        # keeps only the filter-overlap hint (which is load-bearing).
        ('      const hint = document.createElement("div");\n'
         '      hint.className = "empty-hint";\n'
         '      hint.textContent = afActive\n'
         '        ? "Remove a filter above to widen the selection \u2014 an empty result means these facets don\'t overlap in the catalogue."\n'
         '        : "Try a different search term.";\n'
         '      container.appendChild(hint);',
         '      if (afActive) {   // LAB B v67: search-empty carries no hint\n'
         '        const hint = document.createElement("div");\n'
         '        hint.className = "empty-hint";\n'
         '        hint.textContent = "Remove a filter above to widen the selection \u2014 an empty result means these facets don\'t overlap in the catalogue.";\n'
         '        container.appendChild(hint);\n'
         '      }',
         "no-search-hint"),
        ('    if (afActive) frag.appendChild(afBar());',
         '    renderAfPills();',
         "af-call-main"),
        # v57: the Show action lives in the list foot while the tray is
        # open (mirrors the ? pane: overlay above, action in the frame);
        # the overlay pip refreshes on every panel render.
        ('    panel.querySelector("#fp-clear-btn")?.addEventListener("click", e => {',
         '    const lfShow = document.getElementById("lf-show");\n'
         '    if (lfShow) lfShow.textContent = `Show ${state.filtered.length} \u2192`;\n'
         '    requestAnimationFrame(() => updatePip("filter-panel", "filter-pip"));\n'
         '    panel.querySelector("#fp-clear-btn")?.addEventListener("click", e => {',
         "lf-show-label"),
        # v57: overlay scroll + any click keeps the filter pip honest; the
        # foot Show proxies the overlay's own (hidden) Show button.
        ('    document.getElementById("rows").addEventListener("scroll",\n'
         '      () => updatePip("rows", "list-pip"), { passive: true });',
         '    document.getElementById("rows").addEventListener("scroll",\n'
         '      () => updatePip("rows", "list-pip"), { passive: true });\n'
         '    document.getElementById("filter-panel").addEventListener("scroll",\n'
         '      () => updatePip("filter-panel", "filter-pip"), { passive: true });\n'
         '    document.addEventListener("click", () => requestAnimationFrame(() => updatePip("filter-panel", "filter-pip")));\n'
         '    document.getElementById("lf-show")?.addEventListener("click", () => document.getElementById("fp-show-btn")?.click());',
         "filter-pip-wiring"),
    ], version="70", tray=False)

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
