/* Property OS service worker.
   The shell is cached so the app opens instantly and still renders on a bad
   connection — which is when a resident is most likely to be filing a request.
   API calls are always network-first: a stale maintenance board is worse than
   no board, so nothing under /api/ is ever served from cache. */
const SHELL = 'pos-shell-v5';   // bumped: app.js gained the dataset-notice banner
const FILES = ['/', '/index.html', '/tenant.html', '/staff.html', '/owner.html',
               '/shared.css', '/app.js', '/icon.svg', '/manifest.webmanifest'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(SHELL).then(c => c.addAll(FILES)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(caches.keys()
    .then(ks => Promise.all(ks.filter(k => k !== SHELL).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener('fetch', e => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin) return;
  if (url.pathname.startsWith('/api/')) return;          // never cache live data
  e.respondWith(
    fetch(e.request)
      .then(r => {
        const copy = r.clone();
        caches.open(SHELL).then(c => c.put(e.request, copy));
        return r;
      })
      .catch(() => caches.match(e.request).then(r => r || caches.match('/index.html')))
  );
});
