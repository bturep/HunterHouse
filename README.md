# Hunter House Archive

A static front-end for the Hunter House Stewardship Project's Wikibase, served from GitHub Pages.

Live data: [hunterhouse.wikibase.cloud](https://hunterhouse.wikibase.cloud)

## What this is

Three HTML files, no build step, no backend. Every page load queries the live Wikibase — SPARQL for the index and the holdings counts, the MediaWiki action API for individual items, SPARQL again for reverse references and exports. Edit anything in the Wikibase and it appears here on the next refresh.

```
HunterHouse/
├── index.html         Archive index — every Item, grouped by `instance of`
├── item.html          Single-item detail — raw statements, ?id=Q1
├── collection.html    Finding-aid view — for `archive` / `archival collection` items
└── README.md          This file
```

## Page routing

The index inspects each Item's `instance of` values:
- Items typed `archive` or `archival collection` → `collection.html`
- Everything else → `item.html`

`item.html` also offers a "View as finding aid →" link when the entity is one of the archival-collection types. The two views are interchangeable for the same Q-ID; they show different cuts of the same data.

## Deploy

1. Push these files to the `main` branch of [github.com/bturep/HunterHouse](https://github.com/bturep/HunterHouse).
2. In repo settings → Pages: set **Source** to "Deploy from a branch", **Branch** to `main` / `(root)`.
3. Wait ~30s. Site appears at `https://bturep.github.io/HunterHouse/`.

No Actions, no secrets, no environment variables. The Wikibase URL is hardcoded at the top of each HTML file — adjust there if the instance ever moves.

## Architecture

**Index page.** Two-phase query. First finds the property whose label is "instance of"; if present, items group by their type values. If absent (no `instance of` property yet), items list ungrouped. Defensive against the early-migration state.

**Item page.** Fetches the entity via `wbgetentities`, batch-resolves property and entity labels (50 per API call, paginated), groups statements into sections (Identity, People, Locative, Temporal, Phase/Work, Source, Identifiers, Other) using a property-label heuristic. Reverse references queried separately via SPARQL aggregation.

**Collection page (finding aid).** Same entity fetch as the item page, but renders the statements into ISAD(G)-aligned areas — *Identity*, *Context*, *Content and Structure*, *Conditions of Access and Use*. Then queries SPARQL twice for holdings: first by items linked via a property labeled "source collection"; failing that, by *any* incoming reference. Results are grouped by `instance of` value to produce numerical holdings counts (e.g. "344 architectural drawings, 62 photographs"). The full list is exportable as CSV or JSON, generated client-side.

## Property additions worth folding into the Institution spec

The collection page renders whatever statements exist, but the finding-aid view fills out properly only if the following properties are present on archival-collection Items. Most aren't in `HH_WikibaseSpec_Institution.md` yet. Recommended additions, modeled on ISAD(G) and Canadian RAD (which the CAA finding aids follow):

| Property | Datatype | Purpose | ISAD(G) area |
|---|---|---|---|
| `extent` | string (or quantity + unit) | "344 drawings, 0.22 linear meters textual" | Identity |
| `level of description` | Item (controlled: fonds / series / sub-series / file / item) | Distinguishes a fonds from a sub-collection | Identity |
| `name of creator` | Item (Person) | Already covered by `founder` for institutions; archival collections may need an explicit creator distinct from custodian | Context |
| `biographical history` | string (prose) | The "Hunter was born in Phoenix..." paragraph | Context |
| `scope and content` | string (prose) | What the collection actually contains, beyond `description` | Content and Structure |
| `immediate source of acquisition` | string (prose) | "Donated by Richard Hunter in 2019 and 2021." | Context |
| `acquisition date` | date | When acquired | Context |
| `conditions governing access` | Item (Open / Restricted / Closed) | Access control summary | Conditions |
| `conditions governing reproduction` | string (prose) | Copyright statement, license terms | Conditions |
| `copyright holder` | Item or string | Who holds rights | Conditions |
| `language of material` | Item (English / French / etc.) | Multi-valued | Conditions |
| `accruals` | string (prose) | "Further accruals expected" | Content and Structure |

Wikibase doesn't have a native long-text datatype, but `string` handles prose adequately; long prose is also reasonable to leave on the corresponding wiki page rather than as an Item statement. Decide per property based on whether other Items will reference the value or whether it's purely descriptive.

The page's `AREAS` map at the top of `collection.html` already anticipates most of these labels. Add the property in Wikibase using one of those exact labels and it lands in the right finding-aid area automatically.

## Holdings: how counts are derived

The page tries two queries in order:

1. **Named** — items linked via a property whose label is `source collection`. This is the canonical path once that property exists.
2. **Any incoming** — items linked via any incoming property. Used as fallback during migration when the property hasn't been created. May overcount, but won't be empty.

The numerical breakdown ("X drawings, Y photographs") emerges from grouping by each held item's `instance of` value. To match the CAA's specific phrasing ("344 architectural drawings: 245 original drawings, 55 reprographic copies, ..."), you'd need a more granular `item type` or `drawing type` property on Archive Items — already anticipated in the Archive Item spec.

## Export

The CSV and JSON export buttons run the holdings query (capped at 5000 items) and serialize results in the browser. Columns: `qid`, `label`, `type_qid`, `type_label`, `wikibase_url`. To export more fields (creation dates, drawing types, source page references), extend the SPARQL query in `fetchHoldings()` and add the fields to `exportCSV` / `exportJSON`.

The export is not the canonical archival manifest — that lives in the CAA's own catalogue for the Hunter fonds, in the Hunter House Collection's internal records, etc. The export is a *snapshot* of what the Wikibase currently models about a collection's holdings, useful for sharing, version control, and reconciliation.

## Things deliberately left out of v1

- **Image thumbnails.** The mockup shows primary representations and galleries; both wait on the Cloudflare scan pipeline (OQ-204, OQ-205). Once images have stable URLs via a Wikibase property, `formatValue()` extends to render them.
- **Federation links to CAA.** The collection page renders `finding aid URL` and `accession policy URL` as external links once those properties carry values. Direct links into CAA's catalogue for individual Items follow once the `CAA archive reference` property is populated on Archive Items.
- **Series / sub-series hierarchy.** The CAA fonds is structured as Fonds → Series → Sub-subseries → File → Item. The current Institution spec collapses this to Institution + (separately) Phases for the Hunter Residence. If you want a full hierarchical finding-aid tree, that's a structural decision for the Institution and Phase specs, not a frontend gap.
- **Per-property facets and faceted holdings filters.** Once Archive Items have rich properties (Project Set, Drawing Type, House Area), the collection page extends with filters. Holding off until those properties exist.

## Extending

**Add a property to a finding-aid area:**
```js
// In collection.html, near the top:
const AREAS = {
  "identity-fields": [
    /* ... */
    "extent and medium",         // ← add labels here
    "level of description",
  ],
  /* ... */
};
```

**Customize the holdings export columns:**
Edit `fetchHoldings()` to retrieve more fields, then add them to `exportCSV()` and `exportJSON()`.

**Point at a different Wikibase:**
Change `WIKIBASE_URL` at the top of all three HTML files. Everything is derived from it.

## Related

- Wikibase migration plan: `HH_Migration_RUNBOOK.md` (project specs)
- Item Type specs: `specs/HH_WikibaseSpec_*.md` (project specs)
- Original mockup: `HH_Wikibase_ItemPage_Mockup_2026-05-11_v2.html`
- CAA finding aid for Hunter fonds: [searcharchives.ucalgary.ca/richard-hunter-accession](https://searcharchives.ucalgary.ca/richard-hunter-accession) (F0076 — primary external referent for the `Richard Hunter fonds` Institution Item)
