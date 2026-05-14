# Hunter House Foundation — public site

A static site for the Hunter House Foundation, served from GitHub Pages. The information architecture mirrors the planned Foundation site at `hunterhousefoundation.com`; this implementation runs against the Wikibase at [hunterhouse.wikibase.cloud](https://hunterhouse.wikibase.cloud) as a working iteration.

## Pages

```
HunterHouse/
├── index.html            Home — Foundation landing with Hunter epigraph + entry pathways
├── the-house.html        The House — narrative on the Hunter Residence and the drawing record
├── archive.html          About the Archive — how the catalogue is organized
├── browse.html           Browse — every Wikibase Item, grouped by type, with filter and search
├── richard-hunter.html   Richard Hunter — biography, built work, exhibitions
├── about.html            About the Foundation — mandate, people, fellowship, contact
│
├── Main_Page.wiki        Wikitext source for hunterhouse.wikibase.cloud/wiki/Main_Page
└── README.md             This file
```

One page queries the Wikibase live (`browse.html`). The four narrative pages (`index`, `the-house`, `archive`, `richard-hunter`, `about`) are static prose, adapted from the Archive Overview and the CAA biographical record.

## Site architecture

The IA follows the Foundation site plan:

| Section | Purpose | Source content |
|---|---|---|
| Home | Orienting statement, primary navigation | Hunter epigraph + curated entry pathways |
| The House | Narrative introduction to the Hunter Residence | Archive Overview §1–5 |
| Archive | Public-facing introduction to the catalogue | Archive Overview + Technical Description |
| Browse | The archive proper — filter and search | Live Wikibase query |
| Richard Hunter | Biography, exhibitions, publications | CAA biographical record (F0076) |
| About | Foundation mandate, people, fellowship, contact | Custom |

## Visual language

Reference: Canadian Centre for Architecture ([cca.qc.ca](https://www.cca.qc.ca)) — spare, typographic, archive-forward.

Typography:
- Display: Iowan Old Style / Palatino / Georgia (serif)
- Body: Inter / system sans
- Mono: SF Mono / Menlo

Palette:
- Ink `#202020`, muted `#6a6a6a`, rule `#e2e2e2`
- Soft `#f7f5f0`, paper `#f4f0e6`, background `#fafaf7`
- Link `#2a4a8b` (blue), accent `#8b3a2a` (warm red — Hunter-period architectural)

Shared site header is inlined in every page (each file is self-contained — no shared CSS file). To change the nav globally, search-and-replace across the seven HTML files. The variable cost of inlining is the maintenance discipline; the value is that every page works in isolation.

## Deploy

1. Push to `main` on [github.com/bturep/HunterHouse](https://github.com/bturep/HunterHouse).
2. Repo settings → Pages: Source = "Deploy from a branch", Branch = `main` / `(root)`.
3. Live at `https://bturep.github.io/HunterHouse/` in ~30s.

When `hunterhousefoundation.com` is acquired and pointed at the GitHub Pages hosting, add a `CNAME` file to the repo root containing the bare domain.

## Wikibase Main_Page

`Main_Page.wiki` contains the wikitext for `https://hunterhouse.wikibase.cloud/wiki/Main_Page`. Apply by:
1. Visit Main_Page on the wiki
2. Edit (top right)
3. Replace existing content with `Main_Page.wiki` contents
4. Save

The Main Page on the wiki and the index page on this site address different audiences:
- **Wikibase Main_Page** addresses data consumers — researchers, scholars, federated Wikibase users — who landed on the data layer directly. Heavier on item-type structure, properties, and SPARQL.
- **GitHub Pages index** addresses general visitors who encountered the Foundation through its public site. Heavier on framing, the architect, the house.

Both reference each other. The data layer points outward to the public site; the public site exposes the underlying data layer to anyone who wants to query it.

## Things deliberately left out of v1

- **Image rendering.** Once Cloudflare image hosting is set up (OQ-204, OQ-205) and image-URL properties exist on the Wikibase, `formatValue()` in `item.html` and the gallery panels in `collection.html` extend to render them. The narrative pages can also feature curated images once a primary representation is selected per page.
- **Real "Start here" links on `the-house.html`.** The curated pathway is sketched as descriptions of forthcoming entry documents (the 1974 East Wing pre-design, the 1980s coloured legend, key letters, Fulker photographs, Gary Snyder letters). Each becomes a real link once the corresponding Wikibase Item is created.
- **Federation links to CAA per-Item.** The `Richard Hunter fonds` Institution Item carries the CAA finding aid URL; individual Archive Items will carry their own `CAA archive reference` once the property is populated.
- **Fellowship PDF.** Mentioned on `about.html` but not yet linked. To be circulated independently to academic programs and linked from the page when finalized.
- **Contact email.** Placeholder on `about.html`. Replace with the Foundation's contact address.
- **Real search (rather than client-side text filter).** The `browse.html` search is a simple in-page filter against loaded items. A proper search via the Notion API or a client-side index (Fuse.js) is a planned addition once item volume justifies it.
- **CNAME for `hunterhousefoundation.com`.** Added when the domain is in hand.

## Extending

**Add a page to the IA.** Create the HTML file using one of the reading pages (`the-house.html`, `archive.html`) as a template — same site header block, same CSS pattern. Add a nav link in the seven HTML files (search for `<nav class="site-nav">`).

**Update Wikibase URL.** Constants at the top of `index.html` aren't used (Home is static); update `WIKIBASE_URL` in `browse.html`, `item.html`, `collection.html`. Update wiki references in `archive.html` and `about.html`.

**Refine the Collection finding-aid sections.** The `AREAS` map at the top of `collection.html` maps property labels to ISAD(G)-style headings. Add labels as the Institution spec grows (`extent`, `scope and content`, `biographical history`, `conditions governing access`, `conditions governing reproduction`, `language of material`, `accruals` — see prior README revision for full list).

## Related

- Wikibase migration plan: `HH_Migration_RUNBOOK.md` (project specs)
- Item Type specs: `specs/HH_WikibaseSpec_*.md` (project specs)
- Archive Overview: `Hunter_House_Archive_Overview.rtf`
- Archive Technical Description: `Hunter_House_Archive_Technical_Description.rtf`
- Site architecture (Foundation site): `Hunter_House_Website_Architecture.rtf`
- CAA finding aid for Hunter fonds F0076: [searcharchives.ucalgary.ca/richard-hunter-accession](https://searcharchives.ucalgary.ca/richard-hunter-accession)
