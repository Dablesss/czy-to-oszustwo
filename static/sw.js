// Service worker: zapamiętuje wygląd strony, żeby otwierała się szybko.
// Zapytania do /api/ NIGDY nie są zapisywane (prywatność i aktualność wyników).

// Zmień numer przy każdej zmianie w static/, żeby telefony pobrały nową wersję.
// Poradników (static/artykuly/) celowo NIE ma w SHELL: nie zapychamy pamięci telefonu.
const CACHE = "czy-to-oszustwo-v12";
const SHELL = ["/", "/style.css", "/app.js", "/manifest.json", "/icons/icon.svg",
               "/prywatnosc.html", "/regulamin.html"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(SHELL)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  if (event.request.method !== "GET" || url.pathname.startsWith("/api/")) return;

  // "Udostępnij" z aplikacji SMS otwiera adres /?text=<treść wiadomości>. Taki adres NIE może
  // trafić do sieci, bo serwer i hosting zapisują adresy stron w logach. Dlatego odpowiadamy
  // stroną z pamięci telefonu (albo pobieramy "/" bez treści w adresie), a app.js odczyta
  // treść z adresu lokalnie i wyśle ją do /api/check w treści zapytania, której nie logujemy.
  const isShare = ["title", "text", "url"].some((name) => url.searchParams.has(name));
  if (event.request.mode === "navigate" && isShare) {
    event.respondWith(caches.match("/").then((cached) => cached || fetch("/")));
    return;
  }

  // Najpierw sieć (świeża wersja), a bez internetu kopia z pamięci.
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        const copy = response.clone();
        caches.open(CACHE).then((cache) => cache.put(url.pathname === "/" ? "/" : event.request, copy));
        return response;
      })
      .catch(() => caches.match(url.pathname === "/" ? "/" : event.request))
  );
});
