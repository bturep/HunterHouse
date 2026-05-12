# Hunter House Archive

A static front-end for the Hunter House Stewardship Project's Wikibase, served from GitHub Pages.

Live data: [hunterhouse.wikibase.cloud](https://hunterhouse.wikibase.cloud)

## What this is

Two HTML files, no build step, no backend. Every page load queries the live Wikibase — SPARQL for the index, the MediaWiki action API for individual items, SPARQL again for reverse references. Edit anything in the Wikibase and it appears here on the next refresh.

```
HunterHouse/
├── index.html    Archive index — lists every Item, grouped by `instance of`
├── item.html     Single-item detail page — reads ?id=Q1 from the URL
└── README.md     This file
```

## Deploy

1. Push these files to the `main` branch of [github.com/bturep/HunterHouse](https://github.com/bturep/HunterHouse).
2. In repo settings → Pages: set **Source** to "Deploy from a branch", **Branch** to `main` / `(root)`.
3. Wait ~30s. The site appears at `https://bturep.github.io/HunterHouse/`.

That's the whole deployment. No Actions, no secrets, no environment variables. The Wikibase URL is hardcoded at the top of each HTML file — adjust there if the instance ever moves.

## Architecture

**Index page.** Two-phase query. First finds the property whose label is "instance of"; if found, items are grouped by their type values. If not (the property hasn't been created yet), items are listed ungrouped. Defensive against the early-migration state where the Wikibase has Items but few properties.

**Item page.** Fetches the entity via `wbgetentities`, collects all property and entity IDs referenced in the statements + qualifiers, batch-resolves their labels (50 per API call), groups statements into named sections (Identity, People, Locative, Temporal, Phase/Work, Source, Identifiers, Other) using a property-label heuristic defined in the script, then runs a SPARQL aggregation query for reverse references.

**Section grouping.** The `SECTIONS` array at the top of `item.html` controls which property labels fall under which heading. Refine this as the property vocabulary stabilizes — particularly when the gap between current spec drafts and instantiated properties closes.

## Things deliberately left out of v1

- **Image thumbnails.** The mockup shows a primary representation and a gallery; both are blocked on the Cloudflare scan-to-bucket pipeline (OQ-204, OQ-205). Once images have stable URLs accessible via a Wikibase property (e.g. `image URL`), the renderer extends in `formatValue()`.
- **Federation links.** The mockup's "View CAA holdings →" link to the Canadian Architecture Archive will become real once `CAA archive reference` is populated. The plumbing is already in place — values of property type "external identifier" render as `<a class="external">` links.
- **Faceted filtering.** The index page has type filtering + text search. Per-property facets (Project Set, Drawing Type, House Area for Archive Items) come once those properties exist and the volume of Items justifies the UI weight.
- **Caching.** Every page load queries live. Once the Wikibase is stable, a build step that pre-generates static JSON snapshots becomes worth the complexity. Not yet.

## Extending

**Add a new section to the item page:**
```js
// In item.html, near the top:
const SECTIONS = [
  // ... existing
  { name: "Film", keys: ["depicted in film", "filmed by", "filmed on"] },
];
```

**Customize the index display:**
The `render()` function in `index.html` produces the grouped card grid. Replace its template strings with whatever layout you want — table view, timeline, map. The data structure (`itemsByType[typeName] → [{qid, label, description}, ...]`) is stable.

**Point at a different Wikibase:**
Change `WIKIBASE_URL` at the top of both HTML files. The rest is derived from it.

## Related

- Wikibase migration plan: `HH_Migration_RUNBOOK.md` (in project specs)
- Item Type specs: `specs/HH_WikibaseSpec_*.md` (in project specs)
- Original mockup: `HH_Wikibase_ItemPage_Mockup_2026-05-11_v2.html`
