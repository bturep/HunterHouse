# Site-structure survey — how institutions wrap a research archive

> **⚠ WORKING NOTES — DELETE WHEN THE MAIN SITE IS RESOLVED.** This is
> internal research material, committed to the (public) repo only so it syncs
> across machines and is findable by sessions working on the site design.
> Per Brandon (2026-07-11): flag for deletion once the site structure is
> settled. If you are a Claude session and the main-site design has shipped,
> remind Brandon to delete this file.

Research fan-out, 2026-07-10. Two background research agents surveyed how
artist/designer foundations and architecture institutions structure the public
pages **around** a collection/archive. Context for the study: the Hunter House
digital archive (browse.html / next.html) exists and is research-grade; the
main public site does **not** exist yet. The working model: the archive stays
research-only at its core; general visitors will enter through "doorways" —
curated, essential selections — from the future main pages.

This document preserves both agent reports verbatim, then the synthesis.
Companion study (same day, in-session only): a four-agent survey of archive
*UI* patterns (museum facets, archival systems, single-artist catalogues,
faceted-search UX evidence) that drove the browse.html v1.08.05–.07 filter
promotions and the lab-b grouped-list direction. Key conclusions from that
companion study are folded into the synthesis here where they touch site
structure.

---

# PART 1 — Artist/designer foundation websites

Research date: 2026-07-10. All structure read from live pages (noguchi.org
fetched raw and parsed; others via rendered fetches).

## 1. The Noguchi Museum + The Isamu Noguchi Catalogue Raisonné

**URLs:** https://www.noguchi.org/ · https://catalogue.noguchi.org/ · https://www.noguchi.org/isamu-noguchi/archives/

**(a) Top-level nav, verbatim:**
- **Isamu Noguchi** → Digital Features, Biography, Chronology, Exhibition History, Selected Bibliography, Videos, **Archives**
- **Museum** → Visit, Exhibitions, Calendar, Education, Support
- **Artworks** → **Collection**, **Catalogue Raisonné**, Public Works
- **Akari & Shop** → Akari Light Sculptures, Noguchi Shop
- Utility: "Visit: Open Today until 6 pm", Access, 日本語. Footer adds **About** (Mission & History, Board of Trustees, Job Opportunities, Contact, Press).

This is the cleanest three-way conceptual split of any site surveyed: **the
person / the place / the work**, each a top-level door.

**(b) Landing page leads with:** the current exhibition, then a run of
**Digital Features** (curated narrative stories: "History of The Noguchi
Museum," "Representing America: Isamu Noguchi at the 1986 Venice Biennale,"
"History of Akari Light Sculptures"), a Biography intro, an "Archival
Presentation," Support, "Explore the Museum" (Mobile Guide, Noguchi Worldwide,
Public Works, "Archives — Multimedia Collection"), Upcoming Programs, then a
single **collection spotlight** — one sculpture (*Seeking*, 1974) with
Noguchi's own words about it. The homepage never shows the database; it shows
one object, narrated.

**(c) Collection/archive door:** two doors, deliberately distinct. "Artworks →
Collection" is the curated door; "Artworks → Catalogue Raisonné" and "Isamu
Noguchi → Archives" are the research doors. The catalogue lives at its own
subdomain but **shares the parent site's full nav** — same brand, one world.

**(d) Research access framing:** The Archive page is open-browse (Photography,
Manuscript, Architectural, Business & Legal, Publication & Press, Multimedia
collections; "Search the Archive"; a "User Guide"; "About The Archive") but
carries a **"Researcher Login"** button — a two-tier system inside one open
interface. The catalogue.noguchi.org landing is a threshold page: title, one
mission sentence ("an ongoing project… committed to documenting the artistic
practice of Isamu Noguchi (1904–1988)"), a single **"Enter"** button, and a
terms-of-use modal. Access is open but ceremonially gated — you cross a
doorstep.

**(e) Curated → deep linking — the model sentence of the whole survey.** The
Collection page says: *"Available to browse here are works from the Museum's
permanent collection… His texts accompany the works shown here. **For more
comprehensive documentation on Noguchi's works, including those not owned by
the Museum, please consult The Isamu Noguchi Catalogue Raisonné.**"* The
curated layer is explicitly the annotated subset (filters: Decade, Category,
On View, "Original Collection"; quotations from Noguchi's own 1987 catalogue),
and it names the deep layer as where comprehensiveness lives. The Archive page
likewise has a **"Highlights from the Archive"** strip above the raw
collections.

**(f) Tone/density:** calm, image-led, low text density on the public side;
the archive/catalogue side is dense but clean. The clearest example of
curated-with-voice (artist's own texts) vs comprehensive-without-voice.

## 2. Judd Foundation

**URLs:** https://juddfoundation.org/ · https://juddfoundation.org/archives/research/ · https://juddfoundation.org/archives/catalogue-raisonne/

**(a) Top-level nav, verbatim:**
- **Donald Judd** → Biography, Chronology, Art, Architecture, Furniture, Writing
- **Foundation** → About (Mission, Board & Staff, Marfa Restoration Plan, Press & Rights, Contact), Support, Program (Exhibitions, Events, Talks), News, Bookshop
- **Archives** → **Research, Catalogue Raisonné, Library** (external: library.juddfoundation.org), **Oral History Project, Local History, Index of Works**
- **Spaces** → New York (101 Spring Street), Marfa (Architecture Office, Architecture Studio, Art Studio, The Block, Cobb House, Print Building, Ranch Office, Whyte Building), Ranch (Las Casas, Casa Morales, Casa Perez)
- **Visit** → Book New York, Book Marfa

**(b) Landing page leads with:** almost nothing textual — a full-bleed visual
site. The buildings do the talking. The most relevant precedent for a *house*
foundation: **the architecture is the hero, and "Spaces" is its own top-level
category with one page per building.**

**(c) Collection/archive door:** **"Archives" is a top-level nav item** — the
strongest elevation of the archive in the survey — presented as a *menu of
parallel resources* rather than one database: Research, Catalogue Raisonné,
Library, Oral History, Local History, Index of Works.

**(d) Research access framing — the most gated:** "Researchers are required to
**submit a research application** prior to receiving research assistance"
(archives@juddfoundation.org); on-site in Marfa; remote requests for processed
material accommodated for "curators, educators, scholars, and other qualified
researchers." Downloadable **finding aid** for the Donald Judd Papers. The
Catalogue Raisonné is *not yet published* — the page is a public **call for
information**, with the explicit disclaimer "Judd Foundation does not
authenticate or provide valuations of works of art."

**(e) Curated → deep linking:** weakest of the group — the archive resources
are siloed doors off a hub, not woven into narrative pages. The "Donald Judd"
essays and the Archives sit in **separate worlds**; the public path is
Spaces/Visit, the scholar path is Archives, and they barely cross.

**(f) Tone/density:** austere, minimal, very Judd. Dense hierarchical nav,
near-zero marketing copy. The lesson is as much cautionary as exemplary: total
separation of public and research worlds means casual visitors never touch
archival material.

## 3. Georgia O'Keeffe Museum

**URLs:** https://www.okeeffemuseum.org/ · https://www.okeeffemuseum.org/art-and-research/library-and-archive/ · Access O'Keeffe portal: http://access-ok.okeeffemuseum.org/

**(a) Top-level nav, verbatim:** **Visit** (Hours & Locations, Tickets &
Tours, Visitor Information, Accessibility, FAQs) · **Art & Research** (About
Georgia O'Keeffe, **Access O'Keeffe | Collections Search**, Collections Loans
& Research Support, Historic Homes, Library & Archive, Museum Blog &
Publications, Past Talks) · **Exhibitions** · **Calendar** · **Learn &
Engage** · **Future Museum** · **Join & Give** · **Store**

**(b) Landing page leads with:** one painting (*Pedernal*, 1941), practical
visit info, then "**Discover the Art & Life of Georgia O'Keeffe**," locations,
exhibitions, the home experience, programs, membership. Visit-first,
art-as-hero.

**(c) Collection/archive door:** consolidated under a single **"Art &
Research"** menu — the artist bio, the collections portal, loans, the historic
homes, and the library/archive all live behind one door. The portal has a
branded proper name, **"Access O'Keeffe."**

**(d) Research access framing:** two-channel. Digital = fully open (portal, no
gate). Physical = the "Michael S. Engl Family Foundation Library and Archive,"
**"Visit by Appointment Only,"** with a "Research Appointment Request form."
Framed generously: it "**serves the public** by collecting, providing access
to, and preserving information about Georgia O'Keeffe and her contemporaries,
related regional histories, and Modernism." Research guides and finding aids
are published openly.

**(e) Curated → deep linking:** Access O'Keeffe's landing leads with **curated
highlights and thematic tiles** (sections verbatim: *Artwork, Archive,
Artist's Belongings, Historic Exhibitions, People & Organizations*, plus
*Information for Researchers* and *About Access O'Keeffe*), an artist quote,
and 2–3-sentence category summaries — a curated vestibule *inside* the deep
catalogue. Note "Artist's Belongings" as a category — directly relevant to a
house museum's object holdings.

**(f) Tone/density:** the most welcoming/visitor-services register of the
five; research framed as a public service, not a privilege.

## 4. Calder Foundation

**URLs:** https://calder.org/ · https://calder.org/foundation/about/ · archive browse: https://calder.org/archive/all/works/

**(a) Top-level nav, verbatim (only three doors — the leanest):**
- **Calder's Work & Life** → Introduction, Timelines, **Archive**
- **On View** → Current & Upcoming Exhibitions, Calder Around the World
- **The Foundation** → About, Contact, Calder Gardens, Atelier Calder, Calder Prize, Film Commissions

**(b) Landing page leads with:** film — four documentary thumbnails
(1944–1968) — then "Calder's Life & Work" organized into seven chronological
periods. Narrative-chronology-first, no visit info (no physical museum).

**(c) Collection/archive door:** "Archive" sits *inside* "Calder's Work &
Life," third after Introduction and Timelines — i.e., the archive is framed as
**the evidentiary layer under the biography**, not a separate research wing.

**(d) Research access framing — the most explicit two-audience statement:**
the About page says outright, *"**The archive is a resource for curators and
scholars but it is not open to the general public**,"* while "selected
materials are made accessible online," including "extensive bibliography and
exhibition history, archival photographs and ephemera." Scale is stated as
authority: 26,000+ photographs, registrations for 22,000+ works. So: the
*physical/full* archive is closed; the *online selection* is everyone's.

**(e) Curated → deep linking — the most integrated:** the online archive is
one faceted system crossing **Life period (eight phases, e.g. "1926–1930: Wire
Sculpture and the Circus") × Type (Works, Exhibitions, Historical Photos,
Bibliography, Chronology, Films) × Work category (23)**. The curated
"Timelines" narrative and the raw archive share the period structure, so story
and catalogue interlock rather than merely cross-link. Fully open browse, no
login.

**(f) Tone/density:** curatorial, chronological, authoritative. The archive
*is* the site's spine.

## 5. The Andy Warhol Museum

**URLs:** https://www.warhol.org/ · https://www.warhol.org/museum-info/research/

**(a) Top-level nav, verbatim:** **Visit** · **What's On** · **Andy Warhol**
(Biography, **The Collection**, **Research**, Publications) · **Learn** ·
**About**. Utility: Store, Donate, Tickets.

**(b) Landing page leads with:** video hero + one mission sentence: "The Andy
Warhol Museum tells Andy Warhol's story and explores his legacy through **the
largest collection of Warhol art and archives in the world**" — the archive's
scale is the brand claim itself.

**(c) Collection/archive door:** inside the **"Andy Warhol"** person-menu:
Biography, The Collection, Research, Publications sit side by side — the
artist section is simultaneously the collection section.

**(d) Research access framing:** an **"Archives Study Center"** with
rights/reproduction routed to rights@warhol.org. Notably thin on procedure,
and (a real gap) the research page doesn't link a browsable database.

**(e) Curated → deep linking:** weak; curated content and research access are
parallel tracks. Included mostly as the "big museum" contrast case — but the
one-sentence positioning move in (b) is very stealable.

## Part 1 synthesis — patterns

### The recurring page inventory

| Body | Typical labels seen | Hunter House equivalent |
|---|---|---|
| **The person** | "Isamu Noguchi" / "Donald Judd" / "Calder's Work & Life" | Richard Hunter — biography, chronology, his own words |
| **The place** | "Spaces" + "Visit" (Judd) / "Historic Homes" (O'Keeffe) | The house itself — rooms, siting, stewardship, access |
| **The work, curated** | "Collection" (Noguchi) / "Access O'Keeffe" highlights / "Timelines" (Calder) | The doorways — curated selections |
| **The work, comprehensive** | "Catalogue Raisonné" / "Archives" / "Archive" | The existing Wikibase catalogue |
| **The institution** | "Foundation" / "About" / "Support" | Hunter House Foundation — mission, people, contact |

Plus, in the stronger sites, a sixth: **stories/features** (Noguchi's "Digital
Features," Calder's period narratives) — the connective tissue between curated
and comprehensive.

### How the public/research split is actually expressed

1. **Two labels for two depths.** "Collection" (curated, annotated, with
   voice) vs "Catalogue Raisonné"/"Archive" (comprehensive, flat,
   research-grade). Noguchi's cross-link sentence is the template — the
   curated page **names its own incompleteness** and points down. The Hunter
   House sentence practically writes itself: *"A fuller record of each object,
   including provenance and documentation, is held in the Hunter House
   Archive."*
2. **A threshold, not a wall.** Noguchi's "Enter" + terms modal; O'Keeffe's
   "Information for Researchers" inside an open portal. Open access with a
   doorstep signals "this is the serious room" without excluding anyone.
   Calder's blunt sentence is the honest way to phrase a closed physical
   collection with an open digital one.
3. **Highlights strips inside the deep layer.** Noguchi's "Highlights from the
   Archive"; Access O'Keeffe's curated landing tiles. The archive itself gets
   a vestibule, so a public visitor who lands deep isn't dropped into raw
   records.
4. **Structural rhyme between story and catalogue.** Calder's masterstroke:
   the biography's eight periods are also the archive's primary facet, so
   every narrative chapter *is* a query. For Hunter House: if the doorways are
   organized by the same facets the catalogue uses (collection, room, object
   type), each doorway is a saved search with an essay on top — cheap to
   build, deeply linked by construction.

Two cautions: **Judd's total separation** means the public never encounters
archival material at all — the anti-pattern for a doorways model; **Warhol's
research page without a database link** shows how a research door can
dead-end.

---

# PART 2 — Architecture institutions whose identity centres on an archive

Research date: 2026-07-10. All findings from live fetches except Soane
(blocked; reconstructed from indexed pages and URL paths — verify labels in a
browser before quoting).

## 1. Canadian Centre for Architecture — cca.qc.ca — *the strongest precedent*

**(a) Top-level nav, verbatim:** `Explore` · `About` · `Calendar` · `Info` —
four items, remarkably minimal.

**(b) Landing page leads:** editorial, not visiting. A hero quote, the current
exhibition, a featured article, then a grid of recent articles. The landing
page behaves like a magazine cover, not a museum brochure.

**(c) Archive/collection door:** `Collection` sits under **About**
(`/en/about-collection`) — deliberately not top-level. The archival research
door proper is the **Guide to archival holdings** (`/en/archives/`): an A–Z
list of ~230 fonds, each entry "name/firm/project + reference code (e.g.
AP164)" linking to a finding aid. Framing sentence: the collection is *"a
repository of ideas, provocations, inspirations, and trials and errors."*

**(d) Research access:** appointment-based Study Room (Mon–Fri 10–17).
Consultation via `ref@cca.qc.ca`; **minimum 2 weeks' notice for primary
sources, 48 hours for secondary**. A dedicated "Collection access and use FAQ"
page carries the procedural detail so collection pages stay clean.

**(e) Editorial → archive linking — verified and exemplary.** The Articles
section (543 articles, organized into thematic "Issues") links *inline* to
collection records. Verified in the Siza/Borasi interview
(`/en/articles/103820/desire-paths`): image captions carry full archival
citations — *"…Chromogenic colour print. **PH2016:0100:050, CCA.** Gift of the
artist"* — with the reference number hyperlinked to the object record. The
object record then links **upward** to its series/fonds, to "View the finding
aid," and to a "Request these items" action. The chain: **article → cited item
→ fonds/finding aid → appointment request** — every editorial page is a
doorway into the research apparatus.

**(f) Visiting's role:** the CCA has galleries but Visit does not dominate;
identity is carried by Explore (ideas) and Collection (evidence).

## 2. Fondation Le Corbusier — fondationlecorbusier.fr

**(a) Nav, verbatim:** `The Foundation` (Fondation, Missions, Partners) · `Le
Corbusier` (Biography, Works, Thematic folders) · `Collections` (Resource
Center, Database, Archives) · `Visit` (Maison La Roche, the apartment-studio,
Villa Le Lac, Other destinations) · `News`.

**(b) Landing leads:** hero image of the man, then three blocks in order:
**Visit** (the three houses), **News**, **Focus** (thematic features).

**(c) Archive door:** top-level `Collections` with three sub-doors: **Resource
Center** (the physical reading room), **Database** (*BaseCorbu*, open online
search, anonymous access), **Archives** (description of holdings: ~450,000
documents; "35.000 plans, 54 models… 15.000 black and white photographs").
Framing leans on provenance: the Foundation is the *"universal beneficiary of
the architect."*

**(d) Research access:** Resource Center **open by appointment, Tuesday and
Thursday afternoons**, explicitly welcoming: open to *"students, experienced
researchers, exhibition curators, as well as to amateurs wishing to deepen
their knowledge."* A named head of research is the contact.

**(e) Editorial → archive:** weak. "Thematic folders" and "Focus" are the
curated doorways, but they don't deep-link into BaseCorbu records. The
database is a silo.

**(f) Houses' effect:** Visit is a full top-level door and the first
landing-page block — but it does **not** displace Collections from the top
level. The cleanest "houses + archive as peers" example: five doors, one per
audience intent (who we are / who he was / research / visit / now).

## 3. Sir John Soane's Museum — soane.org + two satellite domains

*(Reconstructed from indexed pages; verify before quoting.)*

**(a) Nav:** `Visit` · `What's On` · `Collections` · `Learning` · `Get
Involved` · `Venue Hire` · `About`.

**(b) Landing leads:** the house itself — "the smallest of the National
Museums," free entry; visiting dominates.

**(c–e) The three-domain pattern — the key structural lesson:**

| Door | Domain | Audience/mode |
|---|---|---|
| Museum site | `soane.org` | Visitor: plan a visit, what's on, learning, support |
| **Collections online** | `collections.soane.org` | Researcher: full database — Drawings, Books, Archives; advanced search |
| **Explore Soane** | `explore.soane.org` | Curious public: photogrammetry 3D rooms with highlight objects — the *curated doorway* as a whole separate product |

The main site's `Collections` page is a **routing page**, not content: it
forks you by intent to the two satellites, plus to **The Research Library and
Archive** for physical study.

**(d) Research access:** by appointment, Wednesday–Friday, two weeks in
advance, `library@soane.org.uk`. Holdings framed concretely: 30,000
architectural drawings, 7,000 books, Soane's papers.

**(f) House effect:** with a visitable house, Visit leads and the archive
recedes to a Collections sub-page — but the two satellite domains keep
research and exploration first-class *without* fighting for main-nav space.

## 4. Frank Lloyd Wright Foundation — franklloydwright.org — *the cautionary precedent*

**(a) Nav, verbatim:** `Learn` · `Visit` · `Events` · `Join & Give` · `Shop` ·
`Private Events` · `About Us` · `Contact`. Collections sit two levels down:
**Learn → "The Frank Lloyd Wright Foundation Collections."**

**(b) Landing leads:** a booking banner — "Summer tours sell fast." Pure
visitor-conversion.

**(c) Archive door:** buried, and structurally hollowed out: **the Wright
archive left the Foundation in 2012** — drawings/correspondence/photographs to
Avery Library (Columbia), models to MoMA. What remains is framed
experientially.

**(d) Research access:** email with project details; in-person by appointment,
minimum two weeks; researchers redirected off-site to Avery/JSTOR and MoMA.

**(e) Editorial → archive:** effectively none.

**(f) Lesson:** when Visit + Shop + Venue revenue dominates the nav, the
archive reads as an afterthought — and once the archive physically left, the
site's scholarly identity went with it. The anti-model for a foundation whose
identity *is* its archive.

## 5. Alvar Aalto Foundation — alvaraalto.fi

**(a) Nav, verbatim:** `Visit` (six house/building sites) · `Exhibitions and
Events` · `News` · `Architecture and Design` (Aalto Works, Architecture,
Design, Alvar, Aino, Elissa) · `Services` (Collections and research,
restoration supervision, documentation…) · `Alvar Aalto Foundation`.

**(b) Landing leads:** "AALTO WORKS" — the thirteen UNESCO-nominated sites; a
*works-first* framing rather than visit-first or archive-first.

**(c) Archive door:** under **Services → "Collections and research"** — framed
as a professional service, not a public invitation. Holdings stated precisely:
~90,000 original drawings, ~80 shelf-metres of construction documents, ~30,000
letters, ~260 scale models, 60,000+ photographs, the Artek archive.

**(d) Research access:** on-site visits arranged in advance; **services
invoiced per a price list** (the only fee-charging model surveyed); no public
online database.

**(f) Houses' effect:** six visitable sites make Visit the first nav item; the
archive retreats behind "Services." Note the third axis: the *work itself*
("Aalto Works") — not the visit and not the archive — carries the landing.

## Part 2 synthesis — patterns

### The recurring page inventory (all five)

1. **Visit / the place** — dominant wherever a house is publicly visitable;
   absent or demoted otherwise (CCA).
2. **The architect / the work** — biography + works catalogue.
3. **Collections / Archive** — the research door.
4. **Editorial / curated** — Articles (CCA), Thematic folders (FLC), Explore
   Soane. The "doorways" layer.
5. **News / What's On / Calendar.**
6. **About / The Foundation.**
7. **Support / Shop** — only where the operating model needs it.

### Labelling the research door

- **"Collections" is the consensus public label.** It reads as invitation.
- **"Archives" is the researcher-facing sub-label** — fonds, finding aids,
  appointments.
- **"Research" as a label tends to mean *services or access***, not holdings.
- Pattern worth copying: **a quiet routing page labelled Collection/Archive
  that forks by intent** — Soane's `/collections` does it in three sentences.

### Three structural findings that matter for Hunter House

1. **No visitable house → the archive can lead.** Every visit-heavy site
   demotes the archive. The CCA — where visiting is secondary — leads with
   ideas and evidence. Hunter House, with the house *not yet visitable*, is
   free to take the CCA posture now and add a Visit door later without
   restructuring.
2. **The satellite-domain pattern fits already.** Soane's three-domain split
   is precisely the situation: the Wikibase archive is the `collections.`
   domain, already live. The main site's job is to be `soane.org` — the
   router — and the curated doorway can be a section or, later, its own
   product.
3. **Access framing is universally appointment + email, stated warmly.**
   Nobody uses a gatekeeping form. FLC is the most welcoming ("open to all…
   as well as amateurs," Tue/Thu afternoons). For a small foundation, the FLC
   sentence-shape is the one to steal: named days, named contact, explicit
   welcome to non-academics.

---

# PART 3 — Synthesis and site-map sketches for Hunter House

The two studies converge on the following.

**1. The doorway model is the sector's standard, with a canonical sentence.**
Two labels for two depths — curated "Collection"/"Selections" with voice;
comprehensive "Archive" without — where the curated layer names its own
incompleteness and points down (the Noguchi sentence).

**2. No visitable house = the archive can lead.** Take the CCA posture now;
add Visit later without restructuring.

**3. The one convention to adopt before any page design: CCA citation
discipline.** Every image or document that appears anywhere on the public site
carries its archive ID (`HH-XXX-0000`), hyperlinked to its record. Every
future curated page becomes a doorway into the archive automatically. The
Wikibase back-end makes this nearly free.

**4. Access framing: warm appointment language, not gatekeeping** (FLC
register). A threshold, not a wall (Noguchi "Enter"; O'Keeffe's branded portal
with curated tiles inside the deep catalogue).

**5. Structural rhyme (Calder).** Whatever structure the doorways use should
be the same structure the catalogue facets use — story chapters = saved
queries. (In-session decision, same day: the archive list's structure is the
COLLECTIONS — the fonds level — in authored order CAA · HHC · IHC · EGC ·
FRH.)

## Site-map sketches

**Sketch A — "CCA minor" (archive-led; the recommended end state)**

```
hunterhousefoundation.com
├── (landing = one Hunter image/quote + 2–3 featured Stories + archive teaser)
├── Richard Hunter            — biography · the work · the house (as a work)
├── Stories                   — curated essays/features; every image captioned
│                                "HH-EGC-0017, Hunter House Foundation Archive"
│                                with the ID linked to the archive record
├── Archive                   — routing page, three sentences:
│   ├── → Search the archive  (the live archive — exists)
│   ├── Guide to the holdings — what the ~260 items are, how organized
│   └── Research access       — appointment/email framing, named contact
├── The House                 — "not yet open to visitors" + preservation status
│                                (grows into Visit when that day comes)
└── About                     — the Foundation · mission · people · contact · support
```

**Sketch B — "FLC peer doors" (if house/visits should read as coequal from day one)**

```
├── The Foundation        — mission · people · news · contact
├── Richard Hunter        — biography · works · thematic folders (the doorways)
├── Archive               — search · holdings guide · access
├── The House             — the house as subject; visiting-future page
└── Now                   — news/events (fold into About until there's volume)
```

**Sketch C — "Soane satellite" (minimal main site; heaviest reuse of what exists)**

```
hunterhousefoundation.com        — 4-page brochure site:
├── Home                         — routes by intent: "Explore highlights" /
│                                  "Search the archive" / "About the Foundation"
├── Richard Hunter & the House   — one combined narrative page
├── Collection                   — Soane-style fork page:
│     → Highlights / Selections  (future curated product)
│     → the archive              (the research database, already live)
│     → Research access          (appointment paragraph)
└── About / Contact
(the archive itself stays untouched, research-grade)
```

**Recommendation: ship C's skeleton, grow into A.** The single
highest-leverage convention to adopt from day one — before any page design —
is the CCA citation discipline. The Noguchi triptych (person / place / work)
is the alternative top-nav conceptual split if the site should feel like a
small institution from the start; three richer sketches along those lines are
in the Part 1 report above.

Cross-cutting recommendations regardless of sketch: keep the archive at its
own URL but give it the main site's header (the Noguchi one-world trick); put
a "Highlights" vestibule at the archive's front door; write the Noguchi-style
cross-link sentence once and reuse it everywhere curated content appears; lead
the homepage with one object and a voice, never with the database; O'Keeffe's
"serves the public… by appointment" register fits a small foundation better
than Judd's application gate.
