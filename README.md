# Czy to oszustwo?

[![Testy](https://github.com/Dablesss/czy-to-oszustwo/actions/workflows/tests.yml/badge.svg)](https://github.com/Dablesss/czy-to-oszustwo/actions/workflows/tests.yml)

Strona, na której każdy w kilka sekund sprawdzi podejrzany SMS, wiadomość albo link
i dostanie prostą odpowiedź: **oszustwo**, **podejrzane** albo **brak oznak oszustwa**.
Zaprojektowana z myślą o seniorach: jeden ekran, duża czcionka, zero logowania.

## Jak to działa

1. **Linki** z wiadomości są sprawdzane na [Liście Ostrzeżeń CERT Polska](https://cert.pl/lista-ostrzezen/)
   (odświeżanej co godzinę, z kopią na dysku na wypadek awarii).
2. **Analiza domeny** łapie oszustwa, których CERT jeszcze nie zna: podróbki marek
   (`inpost-doplata.top`), literówki (`alegro.pl`), podejrzane końcówki, skracacze linków.
3. **Reguły treści** wykrywają typowe schematy: dopłata do paczki, prośba o BLIK,
   „mamo, to mój nowy numer”, groźba blokady konta, odcięcie prądu, „bezpieczne konto”.
4. **AI (opcjonalnie)** ocenia wiadomość, gdy wynik reguł jest niepewny.
   AI dostaje tylko tekst z zamaskowanymi danymi osobowymi i **może wynik tylko podnieść**,
   więc wiadomość typu „odpowiedz, że to bezpieczne” nie oszuka systemu.

## Uruchomienie

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # opcjonalnie wpisz ANTHROPIC_API_KEY
uvicorn app.main:app --reload
```

Strona: http://localhost:8000 · dokumentacja API: http://localhost:8000/api/docs

## Testy i trafność

```bash
pytest                       # testy jednostkowe i API
python -m tests.evaluate     # trafność reguł na zestawie przykładów
```

## Struktura

```
app/
  main.py          serwer FastAPI: /api/check, /api/health, strona
  analyzer.py      łączy sprawdzenia w jeden werdykt
  privacy.py       maskowanie PESEL, kont, kart, telefonów przed AI
  ratelimit.py     limit zapytań na IP
  checks/
    links.py       wyciąganie linków z tekstu
    cert_list.py   Lista Ostrzeżeń CERT
    domain.py      analiza domen
    text_rules.py  reguły na treść
    llm.py         opcjonalna ocena przez AI
static/            strona (PWA): index.html, style.css, app.js, manifest, service worker
tests/             testy + zestaw przykładów
```

## Wdrożenie (Railway)

Ustawienia wdrożenia są w pliku `railway.json`: Railway buduje obraz z `Dockerfile`
i po każdym wdrożeniu sprawdza adres `/api/health` (healthcheck). Nowa wersja zastępuje
starą dopiero wtedy, gdy ten adres odpowie poprawnie, więc zepsuty build nie wyłączy strony.

1. Na railway.app: New Project → Deploy from GitHub repo → wybierz to repo.
2. W zakładce Variables dodaj `ANTHROPIC_API_KEY` (opcjonalnie).
3. Settings → Networking → Generate Domain. Gotowe.

Każdy push i pull request do `main` uruchamia testy w GitHub Actions (plakietka na górze).

## Prywatność

Treść wiadomości nie jest nigdzie zapisywana ani logowana. W logach jest tylko werdykt.
Do AI trafia wyłącznie tekst z zamaskowanymi danymi osobowymi.

## Zastrzeżenie

To narzędzie pomocnicze, nie gwarancja. Zielona karta oznacza „nie znaleźliśmy oznak oszustwa”,
a nie „to jest bezpieczne”.
