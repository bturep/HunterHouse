/* ============================================================
   The Hunter House — a fifty-year design record.

   The HOUSE is the spine. Only the essential life events that lead
   up to its design are kept; everything else is the house's own
   making — schemes, permits and construction, 1969–2020 — drawn
   from the catalogue (HHC + CAA collections, ~640 dated items
   across ~40 project phases).

   Threads: Life (the lead-up) · Design (schemes & drawings) ·
   Build (permits, construction, engineering).

   Sources: Hunter House catalogue (live Wikibase, phase + date per
   item) for the house thread; Timeline Audit 2026-05-28 (FH08–09,
   FH15, Wikidata Q139959908, Wikibase Q234) for the lead-up.
   Sensitive family detail is deliberately held out (per the audit).
   ============================================================ */
window.TL = {
  span: [1928, 2026],
  threads: {
    life:   { label:"Life",   color:"#8c877e" },
    design: { label:"Design", color:"#c9a44e" },
    build:  { label:"Build",  color:"#c4826e" },
  },
  order: ["life","design","build"],
  events: [
    // ── the lead-up: only the essentials before the house ──
    {y:1930, thread:"life", short:"Born", title:"Born in Phoenix, Arizona", place:"Phoenix, AZ", date:"4 November 1930", src:"Wikidata", key:true,
      note:"Richard Morrow Hunter."},
    {y:1958, thread:"life", short:"Oklahoma · Goff", title:"Graduates, University of Oklahoma", place:"Norman, OK", date:"1958", src:"FH09",
      note:"An architecture degree in the orbit of Bruce Goff and the American School of organic architecture — the way of building the house would carry."},
    {y:1958, thread:"life", short:"Japan · Daitoku-ji", title:"First trip to Japan", place:"Kyoto, Japan", date:"1958", src:"FH09", key:true,
      note:"Studies Zen Buddhism at Daitoku-ji, among the temples and gardens of Kyoto — the sensibility the house would be built around."},
    {y:1962, y2:1964, thread:"life", short:"Kyoto years", title:"Lives in Kyoto, Japan", place:"Kyoto, Japan", date:"1962–64", src:"FH09",
      note:"Village architecture, Zen gardens, the Japanese language — the deepest source of the house's character."},
    {y:1968, thread:"life", short:"To Victoria", title:"Moves to Victoria, B.C.", place:"Victoria, BC", date:"1968", src:"FH09",
      note:"Arrives on Vancouver Island, where the house will stand."},

    // ── the house: 1969–2020 (drawn from the catalogue) ──
    {y:1969, thread:"design", short:"Design begins", title:"Pre-Cottage — Phase I, Schemes I & II", place:"203 Goward Rd", date:"1969", src:"HH-HHC", key:true,
      note:"The first drawings — Scheme I [Star-Pinwheel] and Scheme II [Tilted]. The house begins as a search for a plan."},
    {y:1969, thread:"build", short:"Site surveyed", title:"First land survey, 203 Goward Road", place:"Prospect Lake, Saanich", date:"1969", src:"HH-HHC",
      note:"The land measured — the start of a survey record that runs the length of the project, to 2018."},
    {y:1970, thread:"design", short:"The cottage", title:"Cottage for Ric & Frances Hunter — Phase I", place:"203 Goward Rd", date:"1970", src:"HH-HHC",
      note:"The original cottage, drawn out."},
    {y:1970, y2:1973, thread:"build", short:"Cottage built", title:"Original cottage — permit & construction", place:"203 Goward Rd", date:"1970–73", src:"Wikibase Q234", key:true,
      note:"The house is built — architect, client and resident all Hunter. The newly-finished residence is photographed."},
    {y:1977, y2:1978, thread:"design", short:"Zendo", title:"Zendo (speculative)", place:"203 Goward Rd", date:"1977–78", src:"HH-HHC",
      note:"A speculative meditation hall — the Zen thread turned toward the house itself."},
    {y:1979, thread:"build", short:"Pier", title:"Pier for 203 Goward Road", place:"Prospect Lake", date:"1979", src:"HH-HHC",
      note:"A pier built down on the lake."},
    {y:1986, thread:"design", short:"Phase II", title:"Hunter House — Phase II, Schemes I & II", place:"203 Goward Rd", date:"1986", src:"HH-HHC", key:true,
      note:"The first major reimagining of the house, worked out in two schemes."},
    {y:1987, thread:"build", short:"Cascade Deck", title:"Cascade Deck", place:"203 Goward Rd", date:"1987", src:"HH-HHC",
      note:"A deck stepped down the slope."},
    {y:1990, thread:"design", short:"Studio & Garden", title:"Studio and Garden — Phase II, Scheme II", place:"203 Goward Rd", date:"1990", src:"HH-HHC",
      note:"Studio and garden drawn into the Phase II addition."},
    {y:1990, thread:"build", short:"West Wing", title:"Haus Addition permit & West Wing construction", place:"203 Goward Rd", date:"1990", src:"HH-HHC", key:true,
      note:"The West Wing — permitted and built. 1990 is the single densest year of drawings in the early record."},
    {y:1992, thread:"design", short:"Colour Studies", title:"Colour Studies for Hunter House", place:"203 Goward Rd", date:"1992", src:"CAA",
      note:"A campaign of colour studies for the house."},
    {y:1995, thread:"build", short:"Roof", title:"Roof permit set", place:"203 Goward Rd", date:"1995", src:"HH-HHC",
      note:"Re-roofing, permitted."},
    {y:1996, thread:"build", short:"Tower & Apartment", title:"Beam repairs · Tower & Apartment", place:"203 Goward Rd", date:"1996", src:"HH-HHC",
      note:"Structural beam repairs (Brown & Grant Engineering) and a tower-and-apartment addition."},
    {y:2002, thread:"build", short:"Entry Door", title:"Entry door set", place:"203 Goward Rd", date:"2002", src:"HH-HHC",
      note:"A new entry door, with a bedroom-closet set drawn two years before."},
    {y:2005, y2:2015, thread:"design", short:"Entry Garden", title:"Entry Garden design arc", place:"203 Goward Rd", date:"2005–15", src:"HH-HHC", key:true,
      note:"A decade-long design of the entry garden and walkway — the longest single design arc in the whole record."},
    {y:2008, thread:"design", short:"East Wing begins", title:"Hunter Haus — Phase 2 (East Wing)", place:"203 Goward Rd", date:"2008", src:"HH-HHC", key:true,
      note:"The East Wing — the last great chapter of the house — begins."},
    {y:2008, thread:"build", short:"East Wing built", title:"East Wing construction", place:"203 Goward Rd", date:"2008", src:"HH-HHC",
      note:"East Wing construction, with kitchen counter and dining-room work close behind."},
    {y:2009, y2:2010, thread:"design", short:"East Wing rooms", title:"East Wing dining room & kitchen", place:"203 Goward Rd", date:"2009–10", src:"HH-HHC",
      note:"Designing the rooms of the East Wing."},
    {y:2015, thread:"build", short:"Veranda · Kotatsu", title:"Veranda roof · Kotatsu table", place:"203 Goward Rd", date:"2015", src:"HH-HHC",
      note:"A veranda roof and a built-in kotatsu table."},
    {y:2016, thread:"design", short:"East Wing office", title:"East Wing office", place:"203 Goward Rd", date:"2016", src:"HH-HHC",
      note:"An office worked into the East Wing."},
    {y:2018, thread:"design", short:"East Wing permit", title:"East Wing permit & dining-room schemes", place:"203 Goward Rd", date:"2018", src:"HH-HHC", key:true,
      note:"The great late push — first and resubmitted permit sets, eight dining-room schemes, and extensive design development. 2018 is the densest year in the entire archive."},
    {y:2019, thread:"build", short:"Windows · construction", title:"East Wing construction & site-built windows", place:"203 Goward Rd", date:"2019", src:"HH-HHC",
      note:"East Wing construction, with site-built windows engineered by Harold Engineering."},
    {y:2020, thread:"build", short:"Final drawings", title:"East Wing refinement — final drawings", place:"203 Goward Rd", date:"2020", src:"Wikibase Q234", key:true,
      note:"The last drawings. Fifty years of continuous design on one house, closed."},

    // ── after ──
    {y:2023, thread:"life", short:"Stewardship", title:"Hunter dies; the residence enters Foundation stewardship", place:"Victoria, BC", date:"14 January 2023", src:"Wikidata", key:true,
      note:"Richard Hunter dies in Victoria. The house and its archive pass into the care of the Hunter House Foundation."},
    {y:2024, thread:"build", short:"Photographed", title:"Photographic survey of the residence", place:"203 Goward Rd", date:"2024", src:"HH-IHC",
      note:"Ivan Hunter's photographic survey — the house as it stands today."},
  ],
};
window.TL.events.forEach((e,i)=> e.id=i);
