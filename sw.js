// Minimal service worker — satisfies PWA installability requirement.
// No caching: the archive relies on live Wikibase SPARQL data.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(clients.claim()));
