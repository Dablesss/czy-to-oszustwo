"""Strażnicy zasad projektu.

Te testy nie sprawdzają, czy aplikacja dobrze rozpoznaje oszustwa.
Pilnują zasad bezpieczeństwa i prywatności, które łatwo złamać przy zmianach
(np. przy nowym wyglądzie strony): CSP bez kodu inline, brak cache'owania /api/,
brak treści wiadomości w logach, ukryte punkty, ostrożny tekst zielonej karty.
Wszystko działa bez sieci i bez AI.
"""

import json
import logging
import os
from html.parser import HTMLParser
from pathlib import Path

# Tak samo jak w test_api.py: bez pobierania listy CERT i bez klucza AI.
# Musi być PRZED importem aplikacji, bo app/config.py czyta te zmienne przy imporcie.
os.environ["CERT_AUTO_REFRESH"] = "false"
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["RATE_LIMIT_PER_MINUTE"] = "1000"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app import config  # noqa: E402
from app.main import app, cert  # noqa: E402

STATIC = Path(__file__).resolve().parent.parent / "static"
# rglob szuka także w podkatalogach (np. static/artykuly/), więc nowe poradniki
# automatycznie przechodzą przez wszystkie testy HTML poniżej.
HTML_FILES = sorted(STATIC.rglob("*.html"))


def html_id(path):
    """Nazwa testu, np. "artykuly/index.html" (same "index.html" powtarzałoby się)."""
    return path.relative_to(STATIC).as_posix()


@pytest.fixture()
def client(monkeypatch):
    # Na wszelki wypadek wyłączamy AI i DEBUG także tutaj (gdyby ktoś miał je w .env).
    monkeypatch.setattr(config, "LLM_ENABLED", False)
    monkeypatch.setattr(config, "DEBUG", False)
    with TestClient(app) as c:
        cert.domains = set()  # pusta lista CERT – nic nie pobieramy z internetu
        yield c


# ---------------------------------------------------------------- 1. HTML bez inline


class InlineFinder(HTMLParser):
    """Czyta HTML znacznik po znaczniku i zapisuje każde złamanie zasady CSP."""

    def __init__(self):
        super().__init__()
        self.problems = []
        self.inside = None  # "script" albo "style", gdy jesteśmy w środku takiego znacznika

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style"):
            self.inside = tag
        for name, value in attrs:
            if name == "style":
                self.problems.append(f"<{tag}> ma atrybut style=")
            if name.startswith("on"):
                self.problems.append(f"<{tag}> ma atrybut {name}= (kod JS w HTML)")
            if value and value.strip().lower().startswith("javascript:"):
                self.problems.append(f"<{tag}> ma {name}=\"javascript:...\"")

    def handle_endtag(self, tag):
        if tag == self.inside:
            self.inside = None

    def handle_data(self, data):
        # Tekst wewnątrz <script> lub <style> to kod inline – CSP go zablokuje.
        if self.inside and data.strip():
            self.problems.append(f"<{self.inside}> ma treść w środku (kod inline)")


def test_there_are_html_files():
    """Zabezpieczenie testu poniżej: gdyby glob nic nie znalazł, tamten test nic by nie sprawdzał."""
    assert HTML_FILES, "Nie znaleziono żadnego pliku HTML w static/"


@pytest.mark.parametrize("path", HTML_FILES, ids=html_id)
def test_html_has_no_inline_code(path):
    """Zasada: CSP bez inline. Nagłówek CSP (script-src 'self', style-src 'self')
    blokuje w przeglądarce kod wpisany prosto w HTML. Gdyby ktoś dodał np. onclick=
    albo <script>...</script>, strona po cichu przestałaby działać, a kusiłoby
    „naprawienie” tego przez osłabienie CSP. Dozwolone jest tylko <script src="...">."""
    finder = InlineFinder()
    finder.feed(path.read_text(encoding="utf-8"))
    assert finder.problems == []


# ---------------------------------------------------------------- 2. Nagłówki bezpieczeństwa


def test_security_headers_on_homepage(client):
    """Zasada: CSP bez inline. Sprawdzamy nagłówki ustawiane w app/main.py.
    'unsafe-inline' / 'unsafe-eval' w CSP otworzyłyby drogę atakom XSS,
    a pozostałe nagłówki chronią przed zgadywaniem typu pliku, osadzaniem
    strony w ramce (clickjacking) i wysyłaniem adresu strony do innych serwisów."""
    headers = client.get("/").headers
    csp = headers["Content-Security-Policy"]
    assert "script-src 'self'" in csp
    assert "unsafe-inline" not in csp
    assert "unsafe-eval" not in csp
    assert headers["X-Content-Type-Options"] == "nosniff"
    assert headers["X-Frame-Options"] == "DENY"
    assert "Referrer-Policy" in headers


# ---------------------------------------------------------------- 3. Service worker


def test_service_worker_skips_api():
    """Zasada: nie zapisujemy treści wiadomości. Service worker nie może
    cache'ować odpowiedzi z /api/, bo wynik sprawdzenia zostałby w pamięci telefonu.

    Ograniczenie: to tylko sprawdzenie tekstu pliku, nie uruchamiamy JavaScriptu.
    Test widzi, że warunek z "/api/" stoi przed respondWith, ale nie sprawdzi,
    czy ten warunek naprawdę kończy funkcję (np. czy jest w nim `return`)."""
    sw = (STATIC / "sw.js").read_text(encoding="utf-8")
    handler = sw[sw.index('addEventListener("fetch"'):]  # tylko obsługa fetch
    assert '"/api/"' in handler
    assert "respondWith" in handler
    assert handler.index('"/api/"') < handler.index("respondWith")


def test_shared_text_never_goes_to_network():
    """Zasada: nie logujemy treści wiadomości. "Udostępnij" z aplikacji SMS otwiera
    /?text=<treść>, a serwer i hosting zapisują adresy stron w logach. Service worker
    musi obsłużyć taki adres sam (strona z pamięci), zanim zapyta sieć.

    Ograniczenie: sprawdzamy tekst pliku, bez uruchamiania JavaScriptu."""
    sw = (STATIC / "sw.js").read_text(encoding="utf-8")
    handler = sw[sw.index('addEventListener("fetch"'):]
    assert '"text"' in handler and "searchParams" in handler
    share_check = handler.index("searchParams")
    assert share_check < handler.index("fetch(event.request)")  # przed zapytaniem do sieci
    assert 'caches.match("/")' in handler[share_check:]


def test_server_has_no_access_log():
    """Zasada: nie logujemy treści wiadomości ani zbędnych danych. Logi dostępu
    uvicorna zapisywałyby adres IP i pełny adres strony (z ?text=... przy udostępnianiu)."""
    dockerfile = (STATIC.parent / "Dockerfile").read_text(encoding="utf-8")
    assert "--no-access-log" in dockerfile


# ---------------------------------------------------------------- 4. Prywatność logów


def test_message_text_is_not_logged(client, caplog):
    """Zasada: treść wiadomości nie trafia do logów (w logach tylko werdykt).
    Wysyłamy wiadomość z unikalnym znacznikiem i szukamy go we wszystkich logach."""
    marker = "ZNACZNIK-TESTOWY-1234"
    caplog.set_level(logging.DEBUG)  # łapiemy logi każdego poziomu
    response = client.post(
        "/api/check", json={"text": f"{marker} dopłata 1,99 zł inpost-doplata.top"}
    )
    assert response.status_code == 200
    assert caplog.records, "Nie złapano żadnego logu – test nic by nie sprawdził"
    for record in caplog.records:
        assert marker not in record.getMessage()


# ---------------------------------------------------------------- 5. Ukryte punkty


def test_score_and_signals_hidden_without_debug(client):
    """Zasada: punkty i sygnały ukryte poza DEBUG. Gdyby oszust widział punkty,
    mógłby poprawiać swój SMS tak długo, aż przejdzie. (test_api.py sprawdza
    tylko brak "score"; tu dodatkowo "signals" i wymuszone DEBUG=false.)"""
    data = client.post("/api/check", json={"text": "Dopłać 1,99 zł: inpost-doplata.top"}).json()
    assert "score" not in data
    assert "signals" not in data


# ---------------------------------------------------------------- 6. Zielona karta


def test_green_card_never_says_safe(client):
    """Zasada: zielona karta nigdy nie mówi „bezpieczne”. Brak oznak oszustwa
    to nie gwarancja, więc tytuł nie może tego obiecywać, a rady muszą
    przypominać, żeby nie podawać kodu BLIK ani PIN-u."""
    data = client.post("/api/check", json={"text": "Cześć, będę o 18, kupić chleb?"}).json()
    assert data["verdict"] == "no_signs"
    assert "bezpieczn" not in data["title"].lower()
    advice = " ".join(data["advice"])
    assert "BLIK" in advice
    assert "PIN" in advice


# ---------------------------------------------------------------- 7. Manifest PWA


def test_manifest_is_valid():
    """Zasada: strona działa jako aplikacja na telefonie (PWA). Zepsuty manifest
    oznacza brak instalacji i brak opcji „Udostępnij → Czy to oszustwo?”
    (share_target), a brakująca ikona psuje instalację."""
    manifest = json.loads((STATIC / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["share_target"]["action"] == "/"
    assert manifest["icons"], "Manifest nie ma ikon"
    for icon in manifest["icons"]:
        # "/icons/icon-192.png" -> static/icons/icon-192.png
        assert (STATIC / icon["src"].lstrip("/")).is_file(), f"Brak pliku {icon['src']}"


# ---------------------------------------------------------------- 8. SEO i nawigacja

# Adres bazowy strony. To JEDYNE miejsce w Pythonie, gdzie jest zapisany.
# Po kupnie domeny podmień go tutaj i w plikach static/ (canonical, og:url, og:image,
# robots.txt, sitemap.xml) – testy niżej pilnują, żeby wszędzie był ten sam.
SITE_URL = "https://domena.example"


class HeadReader(HTMLParser):
    """Zbiera z HTML to, co czytają wyszukiwarki: język, tytuł, opis, adres
    kanoniczny, znaczniki Open Graph i adres linku z logo (a class="brand")."""

    def __init__(self):
        super().__init__()
        self.lang = None
        self.title = ""
        self.in_title = False
        self.meta = {}  # name albo property -> content
        self.canonical = None
        self.brand_href = None
        self.skip_link = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "html":
            self.lang = a.get("lang")
        elif tag == "title":
            self.in_title = True
        elif tag == "meta" and ("name" in a or "property" in a):
            self.meta[a.get("name") or a.get("property")] = a.get("content", "")
        elif tag == "link" and a.get("rel") == "canonical":
            self.canonical = a.get("href")
        elif tag == "a" and "brand" in (a.get("class") or "").split():
            self.brand_href = a.get("href")
        elif tag == "a" and "skip-link" in (a.get("class") or "").split():
            self.skip_link = a.get("href")

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data


def read_head(path):
    reader = HeadReader()
    reader.feed(path.read_text(encoding="utf-8"))
    return reader


@pytest.mark.parametrize("path", HTML_FILES, ids=html_id)
def test_html_has_seo_basics(path):
    """Każda strona ma to, czego potrzebuje wyszukiwarka: język polski, tytuł
    (do 60 znaków, dłuższy Google utnie), opis (do 160 znaków), adres kanoniczny
    na naszej domenie i podgląd linku (Open Graph) z polską wersją językową."""
    head = read_head(path)
    assert head.lang == "pl"
    assert 0 < len(head.title.strip()) <= 60, f"Tytuł: {head.title!r}"
    assert 0 < len(head.meta.get("description", "")) <= 160
    assert head.canonical and head.canonical.startswith(SITE_URL + "/")
    assert head.meta.get("og:url") == head.canonical
    assert head.meta.get("og:image", "").startswith(SITE_URL + "/")
    assert head.meta.get("og:locale") == "pl_PL"
    for key in ("og:title", "og:description", "og:type", "twitter:card"):
        assert head.meta.get(key), f"Brak {key}"


@pytest.mark.parametrize("path", HTML_FILES, ids=html_id)
def test_logo_links_home_and_skip_link_works(path):
    """Logo w nagłówku prowadzi na stronę główną z każdej podstrony, a link
    „Przejdź do treści” wskazuje element, który naprawdę istnieje."""
    head = read_head(path)
    assert head.brand_href == "/"
    assert head.skip_link and head.skip_link.startswith("#")
    assert f'id="{head.skip_link[1:]}"' in path.read_text(encoding="utf-8")


def test_titles_are_unique():
    """Dwie strony z tym samym tytułem wyglądają w wynikach wyszukiwania jak duplikat."""
    titles = [read_head(p).title.strip() for p in HTML_FILES]
    assert len(titles) == len(set(titles))


def test_robots_and_sitemap(client):
    """robots.txt i sitemap.xml są dostępne pod adresami, których szukają wyszukiwarki,
    z właściwym typem, a mapa strony zawiera adres kanoniczny każdej strony HTML."""
    robots = client.get("/robots.txt")
    assert robots.status_code == 200
    assert robots.headers["content-type"].startswith("text/plain")
    assert f"Sitemap: {SITE_URL}/sitemap.xml" in robots.text

    sitemap = client.get("/sitemap.xml")
    assert sitemap.status_code == 200
    assert "xml" in sitemap.headers["content-type"]
    for path in HTML_FILES:
        assert f"<loc>{read_head(path).canonical}</loc>" in sitemap.text


class LinkReader(HTMLParser):
    """Zbiera adresy linków wewnętrznych (href zaczynający się od "/")."""

    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        href = dict(attrs).get("href")
        # "//" na początku to adres innej strony bez https:, więc go pomijamy
        if tag in ("a", "link") and href and href.startswith("/") and not href.startswith("//"):
            self.links.append(href)


def static_file_for(href):
    """Zamienia adres strony na plik w static/, tak jak robi to serwer:
    "/artykuly/" -> static/artykuly/index.html, "/style.css" -> static/style.css."""
    path = href.split("#")[0].split("?")[0]
    if path.endswith("/"):
        path += "index.html"
    return STATIC / path.lstrip("/")


@pytest.mark.parametrize("path", HTML_FILES, ids=html_id)
def test_internal_links_exist(path):
    """Każdy link wewnętrzny prowadzi do istniejącego pliku. Literówka w adresie
    poradnika dałaby błąd 404, a senior nie wiedziałby, co dalej."""
    reader = LinkReader()
    reader.feed(path.read_text(encoding="utf-8"))
    broken = [href for href in reader.links if not static_file_for(href).is_file()]
    assert broken == [], f"Linki do nieistniejących plików: {broken}"


# ---------------------------------------------------------------- 9. Obrazy i SEO obrazów


class ImageReader(HTMLParser):
    """Zbiera atrybuty każdego znacznika <img>."""

    def __init__(self):
        super().__init__()
        self.images = []

    def handle_starttag(self, tag, attrs):
        if tag == "img":
            self.images.append(dict(attrs))


@pytest.mark.parametrize("path", HTML_FILES, ids=html_id)
def test_images_are_accessible_and_seo_friendly(path):
    """Każdy obrazek ma opis (alt) dla czytnika ekranu i wyszukiwarki grafiki,
    wymiary (width, height), żeby strona nie "skakała" przy wczytywaniu,
    i istniejący plik w static/."""
    reader = ImageReader()
    reader.feed(path.read_text(encoding="utf-8"))
    for img in reader.images:
        src = img.get("src", "")
        assert len(img.get("alt", "").strip()) >= 10, f"{src}: brak opisu alt (min. 10 znaków)"
        assert img.get("width") and img.get("height"), f"{src}: brak width/height"
        assert static_file_for(src).is_file(), f"{src}: nie ma takiego pliku"


@pytest.mark.parametrize("path", sorted((STATIC / "artykuly").glob("*.html")), ids=html_id)
def test_article_has_own_share_image(path):
    """Każdy poradnik ma własny obraz 1200x630 do podglądu linku (Open Graph)
    i duży podgląd na Twitterze/X. Plik obrazu musi istnieć."""
    head = read_head(path)
    image = head.meta.get("og:image", "")
    assert image.startswith(SITE_URL + "/img/og/") and image.endswith(".png"), image
    assert static_file_for(image[len(SITE_URL):]).is_file(), f"brak pliku {image}"
    assert head.meta.get("og:image:width") == "1200" and head.meta.get("og:image:height") == "630"
    assert head.meta.get("twitter:card") == "summary_large_image"
