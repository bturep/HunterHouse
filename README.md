# Hunter House Foundation — public site

A **zero-build static site** for the Hunter House Foundation, served from GitHub Pages and live at **[hunterhouse.org](https://hunterhouse.org)**. It catalogues the architectural archive of Richard Morrow Hunter (1930–2023, 203 Goward Road, Saanich BC).

The catalogue browser reads its data at runtime from a public **Wikibase Cloud** instance ([hunterhouse.wikibase.cloud](https://hunterhouse.wikibase.cloud)) over SPARQL, and loads images from a public **Cloudflare R2** bucket. No framework, no bundler, no package manager.

> **For the full technical picture, read [`ARCHITECTURE.md`](ARCHITECTURE.md)** (reviewer-facing brief). This file is the short overview; `WIKIBASE.md` is the data-model reference.

## Project phase

**3-month pilot, researchers only.** Shared with a small group of trusted researchers, not yet the general public. Active work is on building out the archive and the researcher / curator tools; pilot feedback informs subsequent iterations before a broader release.

## Pages

```
HunterHouse/
├── index.html            Home — crawlable landing page (split-layout front door)
├── browse.html           The archive browser — single-file SPA (live SPARQL + R2 snapshot)
├── next.html             Staging copy of browse.html, a version line ahead (v1.09-test.NN)
├── richard-hunter.html   Biography (schema.org Person + sameAs Wikidata)
├── the-house.html        Narrative on the Hunter Residence and the drawing record
├── archive.html          How the catalogue is organised
├── about.html            Mandate, people, fellowship, contact, privacy note
├── gallery.html          Standalone visual house tour (PhotoSwipe lightbox)
├── archive/<ID>.html     Per-item static permalink pages (one per item; SEO + Wikidata P973 targets)
├── sw.js                 Service worker (PWA install + app-shell cache)
├── manifest.json         PWA manifest (+ manifest.next.json for staging)
├── robots.txt + sitemap.xml   Crawl directives + full URL set (generated)
├── assets/               light.css, dark.css, vendored PDF.js + PhotoSwipe, icons, placeholders
├── scripts/              Python tooling — ingest, preservation, snapshot/page builders (not shipped)
├── cloudflare/r2-browser/   Worker: researcher R2 file browser + cookieless analytics endpoints
└── ARCHITECTURE.md, WIKIBASE.md, SYNC-MAP.md, …   docs
```

`browse.html` is **the tool** (the app you *enter*); the rest is **the site** (editorial front-of-house). The two reading pages and `gallery.html` are static prose/images; only the SPA queries Wikibase.

## Live ↔ staging

`browse.html` is live; `next.html` is a parallel staging copy on its own version line, deployed alongside on the same Pages site (a duplicate *file*, not a branch — plain Pages serves only `main`). Develop in `next.html`; promote by copying it over `browse.html`, bumping `VERSION`, **swapping the manifest link to `manifest.json`**, re-applying any held-back feature gates, validating, and tagging. Full procedure in `ARCHITECTURE.md` §4.7.

## Deploy

1. Push to `main` on [github.com/bturep/HunterHouse](https://github.com/bturep/HunterHouse).
2. Repo Settings → Pages: Source = "Deploy from a branch", Branch = `main` / `(root)`. The `CNAME` file (`hunterhouse.org`) sets the custom domain; HTTPS is enforced.
3. Live in ~30 s. (Keep `.nojekyll` in place — this is a hand-built static site; Jekyll would choke on the `wikipedia/` markdown.)

`www.hunterhousefoundation.com` and the old `bturep.github.io/HunterHouse/` path both 301-redirect to `hunterhouse.org`.

## Wikibase Main Page

The wikitext for `hunterhouse.wikibase.cloud/wiki/Main_Page` is mirrored in **`WIKIBASE_MAINPAGE.md`** (apply edits in the wiki UI; keep the mirror in sync). The wiki Main Page addresses data consumers (item-type structure, properties, SPARQL); the site's `index.html` addresses general visitors (the architect, the house, the framing). Each links to the other.

## Visual language

Spare, typographic, archive-forward (reference: the [CCA](https://www.cca.qc.ca)). Type is **Inter Tight** (sans) + **JetBrains Mono** (mono); a warm paper/ink light surface (`light.css`) with a near-black dark surface (`dark.css`, used by the reading pages and the SPA's own inline dark mode). Default theme is dark. Design tokens live in `assets/light.css` / `assets/dark.css`.

## Related

- Architecture brief: [`ARCHITECTURE.md`](ARCHITECTURE.md)
- Wikibase property + QID reference: [`WIKIBASE.md`](WIKIBASE.md)
- Duplicated-fact drift map (what to update where): `SYNC-MAP.md` *(private repo, symlinked)*
- CAA finding aid for the Richard Hunter fonds (F0076): [searcharchives.ucalgary.ca](https://searcharchives.ucalgary.ca/richard-hunter-accession)
- Wikidata: [Richard Hunter Q139959908](https://www.wikidata.org/wiki/Q139959908) · [Richard Hunter fonds Q139960001](https://www.wikidata.org/wiki/Q139960001)
