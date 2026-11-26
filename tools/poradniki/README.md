# Generatory poradników

Narzędzia pomocnicze do działu `static/artykuly/`. Wynik to zwykłe pliki w `static/`, które można też poprawiać ręcznie, ale po ponownym uruchomieniu generatora ręczne zmiany w HTML znikną. Treść poprawiaj w `articles_content.py`.

| Plik | Co robi | Uruchomienie (z katalogu repo) |
|---|---|---|
| `articles_content.py` | treść poradników: tytuły, opisy, przykłady, FAQ, źródła, opisy obrazów (`IMG_ALT`) | – |
| `gen_articles.py` | strony `static/artykuly/*.html` (spis i poradniki) | `cd tools\poradniki; python gen_articles.py ..\..` |
| `gen_illustrations.py` | ilustracje SVG `static/img/artykuly/<slug>.svg` | `python tools\poradniki\gen_illustrations.py .` |
| `gen_og.py`, `render.py` | obrazy do podglądu linku 1200×630 `static/img/og/*.png` (przez Chrome bez okna) | `python tools\poradniki\gen_og.py .` |

`gen_og.py` potrzebuje Google Chrome i biblioteki `websocket-client` (`pip install websocket-client`), której nie ma w `requirements.txt`, bo serwer jej nie używa.

## Nowy poradnik

1. Dopisz słownik do `ARTICLES` i opis obrazu do `IMG_ALT` w `articles_content.py`.
2. Dopisz rysunek do `GLYPHS` w `gen_illustrations.py`.
3. Uruchom trzy generatory, dopisz adres do `static/sitemap.xml` (z `<image:image>`), podbij wersję cache w `static/sw.js`.
4. `python -m pytest -q`: testy sprawdzą SEO, opisy obrazów, linki i obraz do podglądu.
