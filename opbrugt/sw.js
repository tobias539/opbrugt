/* Service worker: gør, at Android (Chrome og Samsung Internet) kan installere Mad app som en rigtig app.
   Den henter altid den nyeste udgave fra nettet først, så opdateringer kommer med det samme. Kun når der
   ikke er net (fx nede i supermarkedet), bruges den sidst hentede udgave. Andre adresser (Claude, Google
   Script) røres ikke. Lageret gemmer hver fil under adressen uden "?v=…", så der kun ligger én udgave. */
const LAGER = "mad-app";

self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => e.waitUntil(self.clients.claim()));

self.addEventListener("fetch", e => {
  const r = e.request;
  if (r.method !== "GET" || new URL(r.url).origin !== location.origin || r.url.includes("version.json")) return;
  const noegle = r.url.split("?")[0];
  e.respondWith(
    fetch(r).then(svar => {
      if (svar.ok) {
        const kopi = svar.clone();
        caches.open(LAGER).then(c => c.put(noegle, kopi));
      }
      return svar;
    }).catch(() => caches.match(noegle).then(gemt => gemt || Response.error()))
  );
});
