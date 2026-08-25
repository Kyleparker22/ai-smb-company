/* yourco service worker — deliberately conservative.
 *
 * This app shows live business data behind a login. A cache that serves stale pipeline
 * numbers, or that keeps one person's view around for the next person to sign in, would be
 * worse than no offline support at all. So:
 *
 *   - ONLY the static shell is cached: the stylesheet, icon and manifest.
 *   - Every navigation and every /api/ call goes to the network, always. No stale data,
 *     and no cached page surviving a sign-out.
 *   - Offline gets an honest message, not a hollow shell pretending to be the app.
 */
const CACHE = 'yourco-shell-v1';
const SHELL = ['/app.css', '/icon.svg', '/manifest.webmanifest'];

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;                       // never cache a write
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;        // never touch third parties

  // Static shell: cache-first, it changes only on deploy.
  if (SHELL.includes(url.pathname)) {
    e.respondWith(caches.match(req).then(hit => hit || fetch(req)));
    return;
  }

  // Everything else — pages and APIs — is network-only. If the network is gone, say so.
  e.respondWith(fetch(req).catch(() =>
    new Response(
      '<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' +
      '<link rel="stylesheet" href="/app.css"><body class="is-auth"><main class="auth">' +
      '<div class="mark">yourco<span>.</span></div>' +
      '<p class="sub">You are offline</p>' +
      '<p class="fine">This app shows live data, so it does not keep an offline copy — ' +
      'a stale pipeline number is worse than none. Reconnect and reload.</p>' +
      '</main>',
      { status: 503, headers: { 'Content-Type': 'text/html; charset=utf-8' } }
    )
  ));
});
