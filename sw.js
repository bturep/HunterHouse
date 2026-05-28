// Hunter House Foundation Archive — KILL-SWITCH service worker.
//
// Replaces the prior shell-caching SW after v2/v3 deployments left iOS
// PWA installs in a broken state (white-screen on launch). This SW does
// the following on install/activate:
//   • Clears every cache this origin holds (any CACHE_NAME, past or present).
//   • Unregisters itself so subsequent fetches go directly to the network.
//   • Force-reloads every currently-open client window — so a stuck PWA
//     tab recovers in-place once the new SW activates.
// It has NO fetch handler — without one, the browser fetches directly
// from the network as if there were no SW. That's the safe default while
// the site stabilises.
//
// The inline `navigator.serviceWorker.register(...)` calls in
// browse.html / next.html have been commented out alongside this push
// so we don't re-register on next load. Once we've confirmed the site
// is healthy, a future commit can reintroduce caching with a fresh
// SW under a different filename (e.g. sw-v2.js) and a fresh registration.

self.addEventListener('install', () => self.skipWaiting());

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    try {
      const keys = await caches.keys();
      await Promise.all(keys.map((k) => caches.delete(k)));
    } catch (e) { /* ignore */ }
    try {
      await self.registration.unregister();
    } catch (e) { /* ignore */ }
    try {
      const clients = await self.clients.matchAll({ type: 'window' });
      clients.forEach((client) => {
        try { client.navigate(client.url); } catch (e) { /* ignore */ }
      });
    } catch (e) { /* ignore */ }
  })());
});

// No fetch handler — browser handles network directly.
