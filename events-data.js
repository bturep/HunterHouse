/* ============================================================
   The Hunter timeline — reviewed list, Brandon 2026-08-23.

   One combined chronology: the full life-side record (life · zen ·
   practice · writing · art) with the HOUSE held to three hits —
   1970 design/build, the 1990 addition, the 2018 dining room.
   Death is the last entry. 31 events (the page holds ~30
   comfortably; accepted).

   Sources: Timeline Audit 2026-05-28 (FH07–15 finding-aid refs,
   Wikidata Q139959908, Wikibase Q234); catalogue items where an
   HH-…-#### ID is given. Sensitive family detail deliberately
   held out (per the audit).
   ============================================================ */
window.TL = {
  span: [1928, 2026],
  threads: {
    life:     { label:"Life",     color:"#8c877e" },
    zen:      { label:"Zen",      color:"#6fa08c" },
    practice: { label:"Practice", color:"#7c889e" },
    writing:  { label:"Writing",  color:"#a07c94" },
    art:      { label:"Art",      color:"#b08145" },
    house:    { label:"House",    color:"#c4826e" },
  },
  order: ["life","zen","practice","writing","art","house"],
  events: [
    {y:1930, thread:"life", short:"Born", title:"Born, Phoenix, Arizona", place:"Phoenix, AZ", date:"4 November 1930", src:"Wikidata", wd:"Q139959908", key:true,
      note:"Richard Morrow Hunter."},
    {y:1955, thread:"writing", short:"Mendelsohn Portfolio", title:"Eric Mendelsohn Portfolio", date:"1955", src:"FH09", key:true,
      note:"A student portfolio on Eric Mendelsohn — the master he would return to in writing fifty years later."},
    {y:1958, thread:"practice", short:"Oklahoma · Goff", title:"Graduates, University of Oklahoma", place:"Norman, OK", date:"1958", src:"FH09",
      note:"An architecture degree in the orbit of Bruce Goff and the American School of organic architecture."},
    {y:1958, thread:"zen", short:"Japan · Daitoku-ji", title:"First trip to Japan", place:"Kyoto, Japan", date:"1958", src:"FH09", key:true,
      note:"Studies Zen Buddhism at Daitoku-ji, among the temples and gardens of Kyoto."},
    {y:1959, y2:1961, thread:"practice", short:"Welton Becket", title:"Welton Becket Assoc., San Francisco", place:"San Francisco", date:"1959–61", src:"FH09",
      note:"Big-firm years — work on the SFO airport."},
    {y:1961, y2:1962, thread:"practice", short:"Fairbanks Airport", title:"Fairbanks Int'l Airport, unbuilt", place:"Fairbanks, Alaska", date:"1961–62", src:"FH15",
      note:"The unbuilt terminal — he wrote his 1961 letters on its diazo prints."},
    {y:1962, y2:1964, thread:"zen", short:"Kyoto years", title:"Lives in Kyoto", place:"Kyoto, Japan", date:"1962–64", src:"FH09",
      note:"Village architecture, Zen gardens, the Japanese language."},
    {y:1964, y2:1968, thread:"practice", short:"Architect, Fairbanks", title:"Architect in Fairbanks, Alaska", place:"Fairbanks, Alaska", date:"1964–68", src:"FH09",
      note:"The Alaska houses — Tor Aurora, Pomeroy, Rabinowitz — date from these years."},
    {y:1966, thread:"writing", short:"East Asia photographs", title:"A Concise History of East Asia — photographs", date:"1966", src:"FH09",
      note:"Photographs credited in the volume."},
    {y:1968, thread:"life", short:"To Victoria", title:"Moves to Victoria, B.C.", place:"Victoria, BC", date:"1968", src:"FH09",
      note:"Arrives on Vancouver Island, where the house will stand."},
    {y:1969, y2:1974, thread:"practice", short:"Private practice I", title:"Private practice I, Victoria", place:"Victoria, BC", date:"1969–74", src:"FH09",
      note:"Including the Mt. Baldy Zen Centre master plan."},
    {y:1970, y2:1973, thread:"house", short:"The Residence", title:"Designs and builds the Hunter Residence, 203 Goward Rd", place:"203 Goward Rd, Saanich", date:"1970–73", src:"Wikibase Q234", key:true,
      note:"Architect, client and resident all Hunter. The newly finished residence is photographed."},
    {y:1974, thread:"life", short:"Citizenship", title:"Canadian citizenship", date:"1974", src:"FH09",
      note:"Becomes a Canadian citizen."},
    {y:1974, thread:"art", short:"In Praise of Hands", title:"In Praise of Hands, Toronto — chemigraphy", place:"Toronto", date:"1974", src:"FH09",
      note:"Chemigraphy shown in the World Crafts Council exhibition."},
    {y:1974, y2:1981, thread:"practice", short:"B.C. Government", title:"Design architect, B.C. Government", place:"Victoria, BC", date:"1974–81", src:"FH08",
      note:"Seven years as a design architect for the province."},
    {y:1975, thread:"zen", short:"Sasaki Roshi", title:"Hosts Sasaki Roshi — two talks at 203 Goward", place:"203 Goward Rd · UVic", date:"10–11 June 1975", src:"FH07", key:true,
      note:"Two talks, at the house and at UVic — the flyer survives in the archive."},
    {y:1976, thread:"art", short:"Habitat UN", title:"Habitat UN Conference, Vancouver", place:"Vancouver", date:"1976", src:"FH09",
      note:"Shown at the Habitat UN Conference on Human Settlements."},
    {y:1977, thread:"art", short:"Fiberworks", title:"Fiberworks, Cleveland Museum of Art", place:"Cleveland", date:"1977", src:"FH09",
      note:"In the Fiberworks exhibition at the Cleveland Museum of Art."},
    {y:1978, thread:"practice", short:"Skeenaview", title:"Skeenaview Care Home, Terrace", place:"Terrace, BC", date:"1978", src:"FH15",
      note:"Care facility for the province."},
    {y:1980, thread:"practice", short:"100 Mile House", title:"100 Mile House care facility", place:"100 Mile House, BC", date:"1980", src:"FH15",
      note:"Care facility for the province."},
    {y:1981, y2:1982, thread:"zen", short:"Ten-month journey", title:"Ten-month family journey: Japan, China, India, Egypt, England", date:"1981–82", src:"FH08", key:true,
      note:"Ten months around the world with the family."},
    {y:1981, y2:1986, thread:"practice", short:"Private practice II", title:"Private practice II, Victoria", place:"Victoria, BC", date:"1981–86", src:"FH08",
      note:"The second run of independent practice."},
    {y:1983, thread:"practice", short:"Vietnamese Buddhist plan", title:"Vietnamese Buddhist community master plan, Vancouver", place:"Vancouver", date:"1983", src:"FH08",
      note:"Master plan for the Vietnamese Buddhist community."},
    {y:1984, thread:"practice", short:"Lady Minto Hospital", title:"Lady Minto Hospital, Ganges", place:"Ganges, Salt Spring Island", date:"1984", src:"FH15",
      note:"Hospital work on Salt Spring Island."},
    {y:1986, thread:"writing", short:"Portfolio published", title:"Hunter portfolio published", date:"1986", src:"HH-HHC-0115", archive:true, key:true,
      note:"Richard Hunter · Architect — the 1986 portfolio, held in the archive."},
    {y:1986, thread:"art", short:"Music for Solo Performer", title:"Performs Lucier's Music for Solo Performer, UVic", place:"University of Victoria", date:"14 November 1986", src:"FH12", key:true,
      note:"The brain-wave piece, performed at the UVic Sonic Lab."},
    {y:1988, thread:"practice", short:"The Pumple letter", title:"Disowns client alterations — the \"Pumple letter\"", date:"11 October 1988", src:"CAA 2021.01", archive:true, key:true,
      note:"Formally disowns a client's alterations to his work."},
    {y:1990, thread:"house", short:"West Wing", title:"West Wing addition — permit and construction", place:"203 Goward Rd", date:"1990", src:"HH-HHC", key:true,
      note:"The 1990 addition, permitted and built — the densest year of drawings in the early record."},
    {y:2005, y2:2006, thread:"writing", short:"Mendelsohn essay", title:"\"On the Early Sketches of Eric Mendelsohn\"", date:"2005–06", src:"Structurist (pending)",
      note:"The late essay — a return to the 1955 portfolio's subject."},
    {y:2018, thread:"house", short:"Dining room", title:"Dining room design addition", place:"203 Goward Rd", date:"2018", src:"HH-HHC", key:true,
      note:"Permit sets and eight dining-room schemes — the densest year in the entire archive."},
    {y:2023, thread:"life", short:"Dies in Victoria", title:"Dies in Victoria", place:"Victoria, BC", date:"14 January 2023", src:"Wikidata", wd:"Q139959908", key:true,
      note:"Richard Hunter dies in Victoria. The house and its archive pass into the care of the Hunter House Foundation."},
  ],
};
window.TL.events.forEach((e,i)=> e.id=i);
