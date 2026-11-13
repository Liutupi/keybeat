// KEYBEAT offline cache. The page itself is fetched from the network first so updates show up;
// word lists, icons and fonts are served from cache and refreshed in the background.
const CACHE = "keybeat-v4";
const SHELL = ["./", "index.html", "manifest.webmanifest", "icons/icon-192.png"];
self.addEventListener("install", e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())); });
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const req = e.request, url = new URL(req.url);
  if (req.method !== "GET") return;
  const fonts = url.hostname === "fonts.googleapis.com" || url.hostname === "fonts.gstatic.com";
  if (url.origin !== location.origin && !fonts) return;            // e.g. dictionary audio: leave to the network
  const page = req.mode === "navigate" || url.pathname.endsWith("/") || url.pathname.endsWith("index.html");
  e.respondWith(caches.open(CACHE).then(async c => {
    const hit = await c.match(req, {ignoreSearch: page});
    const net = fetch(req).then(r => { if (r && (r.ok || r.type === "opaque")) c.put(req, r.clone()); return r; });
    if (page) return net.catch(() => hit || c.match("index.html"));
    if (hit) { net.catch(() => {}); return hit; }
    return net;
  }));
});
