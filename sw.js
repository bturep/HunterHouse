// Hunter House Foundation Archive — shell-caching service worker.
//
// Strategy:
//   • Precache the static shell on install (HTML, CSS, icons, manifest) so a
//     cold offline visit still paints.
//   • Stale-while-revalidate for HTML — cached copy paints instantly, fresh
//     copy is fetched in the background and overwrites the cache for the
//     next visit. A visitor on stale HTML is one visit behind a hotfix; the
//     savings on cold mobile loads outweighs the one-visit lag.
//   • Cache-first for /assets/* — CSS / icons / PDF.js bundle rarely change;
//     when they do, bumping CACHE_NAME below nukes the old cache wholesale.
//   • Network-only for everything off-origin (Wikibase Cloud SPARQL, R2
//     images). Those layers manage their own caching.
//
// Bump CACHE_NAME (the trailing -vN) to invalidate every cached asset on
// next activation. Do this any time the shell layout, asset list, or the
// caching policy itself changes.

const CACHE_NAME = 'hh-shell-v52';

const PRECACHE = [
  './',
  './browse.html',
  './next.html',
  './index.html',
  './manifest.json',
  './manifest.next.json',
  './manifest.baden.next.json',
  './assets/light.css',
  './assets/dark.css',
  './assets/hunter-mark.png',
  './assets/icon-180.png',
  './assets/icon-192.png',
  './assets/icon-512.png',
];

self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) =>
      // addAll is all-or-nothing; fall back to per-URL adds so one 404 in the
      // precache list never aborts the install.
      cache.addAll(PRECACHE).catch(() =>
        Promise.all(
          PRECACHE.map((url) => cache.add(url).catch(() => {}))
        )
      )
    )
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const req = event.request;
  const url = new URL(req.url);

  // Same-origin GETs only. Off-origin (Wikibase, R2) and non-GET (POST writes
  // via the edit proxy in dev) bypass the SW entirely.
  if (req.method !== 'GET') return;
  if (url.origin !== self.location.origin) return;

  // Range requests (PDF.js streams large PDFs with HTTP Range headers) must
  // hit the network — the Cache API can't satisfy partial-content requests.
  if (req.headers.get('range')) return;

  const isHTML =
    req.mode === 'navigate' ||
    req.destination === 'document' ||
    url.pathname.endsWith('.html') ||
    url.pathname.endsWith('/');

  event.respondWith(
    caches.open(CACHE_NAME).then(async (cache) => {
      const cached = await cache.match(req);

      if (isHTML) {
        // Stale-while-revalidate: return cache immediately if any, refresh
        // it in the background. No cache yet → wait on the network.
        const networkP = fetch(req)
          .then((res) => {
            if (res && res.ok) cache.put(req, res.clone());
            return res;
          })
          .catch(() => cached);
        return cached || networkP;
      }

      // Static assets — cache-first. Fall back to network and populate cache
      // on first request.
      if (cached) return cached;
      try {
        const res = await fetch(req);
        if (res && res.ok) cache.put(req, res.clone());
        return res;
      } catch (e) {
        // Offline + uncached: let the browser do its thing.
        return cached || Response.error();
      }
    })
  );
});
