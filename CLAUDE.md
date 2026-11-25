# CLAUDE.md — kontekst projektu „Czy to oszustwo?”

Ten plik czyta Claude Code na starcie każdej sesji. Trzymaj go aktualnym: po każdym większym kroku popraw sekcję „Stan projektu”.

## O projekcie

Strona (PWA), na której każdy w kilka sekund sprawdzi podejrzany SMS, wiadomość albo link i dostanie prostą odpowiedź: **oszustwo** (czerwona karta), **podejrzane** (żółta) albo **brak oznak oszustwa** (zielona). Główni użytkownicy to seniorzy i osoby mniej obeznane z technologią, a pośrednio ich dzieci i wnuki, które wysyłają im link.

- Repo: https://github.com/Dablesss/czy-to-oszustwo (publiczne, projekt do portfolio)
- Plan projektu (dokument): https://claude.ai/artifact/SUDbzvhH4D6nkrcttQMXQx

## Właściciel i sposób pracy

- Właściciel: Kacper, student 2. semestru informatyki inżynierskiej, uczy się Pythona i celuje w pracę przy AI. Projekt ma być w portfolio, więc **Kacper musi rozumieć każdą linijkę**.
- Komunikacja po polsku, krótko i bezpośrednio, bez zbędnych potwierdzeń.
- Pracuje na Windowsie (PowerShell, VS Code). Komendy podawaj w wersji dla PowerShella.
- Zadania oznaczone niżej jako **[Kacper]** robi Kacper sam, bo to na nich się uczy. Możesz tłumaczyć, podpowiadać i robić code review, ale nie pisz za niego rozwiązania, chyba że wprost o to poprosi.
- Zadania oznaczone **[Claude]** możesz robić samodzielnie, także przez subagentów, równolegle.

## Zasady pracy z repo

- **Nigdy nie pushuj do `main`.** Każda zmiana: osobna gałąź (`ci/...`, `data/...`, `ux/...`, `feat/...`, `fix/...`, `docs/...`) i Pull Request do akceptacji Kacpra. Nie merguj sam.
- Przed commitem: `python -m pytest -q` musi przechodzić. Przy zmianach w regułach uruchom też `python -m tests.evaluate` i wpisz wynik do opisu PR.
- Commity, opisy PR, komentarze w kodzie, teksty na stronie: po polsku.
- Nie commituj `.env`, `.venv`, `data/cert_domains.txt`, zrzutów ekranu.
- Repo jest publiczne: w przykładach testowych żadnych prawdziwych numerów telefonów, PESEL-i, nazwisk ani działających złośliwych adresów. Domeny oszustów zmyślaj w tym samym stylu.

## Uruchomienie (Windows, PowerShell)

```
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
copy .env.example .env          # opcjonalnie wpisz ANTHROPIC_API_KEY
python -m uvicorn app.main:app --reload
```

- Strona: http://localhost:8000 · API docs: http://localhost:8000/api/docs · stan: http://localhost:8000/api/health
- Testy: `python -m pytest -q` · trafność reguł: `python -m tests.evaluate`
- Jeśli `.venv\Scripts\activate` zwraca błąd o skryptach: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## Stack i struktura

Jeden serwer FastAPI serwuje API i stronę (jedno wdrożenie). Frontend bez frameworka.

```
app/
  main.py          FastAPI: POST /api/check, GET /api/health, strona z static/, nagłówki bezpieczeństwa (CSP)
  config.py        ustawienia z .env, progi werdyktu
  models.py        schematy Pydantic: Verdict, Signal, CheckRequest, CheckResponse
  analyzer.py      łączy sprawdzenia w jeden werdykt
  privacy.py       maskowanie PESEL, kont, kart, telefonów, e-maili, kodów przed wysłaniem do AI
  ratelimit.py     limit zapytań na IP (w pamięci, okno 60 s)
  checks/
    links.py       wyciąganie hostów z tekstu (także gołe domeny bez https://), registrable_domain
    cert_list.py   Lista Ostrzeżeń CERT Polska: pobieranie co godzinę, kopia na dysku, dopasowanie subdomen
    domain.py      oficjalne domeny marek, podróbki marek, literówki, punycode, IP, końcówki, skracacze
    text_rules.py  reguły regex na typowe polskie oszustwa (tekst normalizowany: małe litery, bez ogonków)
    llm.py         opcjonalna ocena przez Claude (API Anthropic), model z LLM_MODEL
static/            index.html, style.css, app.js, manifest.json (share_target), sw.js, icons/
tests/
  examples.py      zestaw podstawowy (SCAMS, LEGIT) używany przez pytest i evaluate
  evaluate.py      pomiar trafności reguł
  test_*.py        testy jednostkowe, API, bezpieczeństwo AI
.github/workflows/tests.yml   CI (po zmergowaniu PR #1)
railway.json, Dockerfile      wdrożenie na Railway (po zmergowaniu PR #1)
```

## Jak działa sprawdzanie

1. Hosty z tekstu (`links.extract_hosts`).
2. Każdy host: lista CERT (trafienie = 100 pkt, od razu czerwona karta), inaczej `domain.analyze_host`.
3. Reguły treści (`text_rules.check_text`).
4. Bonusy: link do nieoficjalnej strony + prośba o działanie (+15), podróbka marki + jakakolwiek reguła tekstu (+15).
5. Suma punktów, maks. 100. **Od 60 pkt: scam, od 25: suspicious, poniżej: no_signs.**
6. AI tylko gdy wynik jest niepewny (5–59 pkt) albo gdy jest nieznany link i 0 pkt. AI dostaje zamaskowany tekst.

## Kluczowe decyzje (nie zmieniaj bez rozmowy z Kacprem)

- **AI może wynik tylko podnieść, nigdy obniżyć** (`score = max(score, ai.points)`). Chroni przed wiadomościami typu „odpowiedz, że to bezpieczne” (prompt injection). Test: `tests/test_llm_safety.py`.
- **Zielona karta to „nie widzimy oznak oszustwa”, nigdy „bezpieczne”.** Zawsze z przypomnieniem, żeby nie podawać BLIK, PIN-u ani danych karty.
- **Nie zapisujemy ani nie logujemy treści wiadomości.** W logach tylko werdykt. Service worker nie cache'uje `/api/`.
- **Punkty i pełna lista sygnałów są ukryte** (widać je tylko przy `DEBUG=true`), żeby oszuści nie uczyli się obchodzić reguł. Użytkownik widzi maks. 3 powody.
- **CSP bez inline**: żadnych `<script>` ani `style=""` w HTML, tylko pliki z `static/`.
- Przy oszustwie podpowiadamy przesłanie SMS-a na **8080** (numer CERT Polska do zgłaszania).
- Na stronie: jeden ekran, duża czcionka (bazowo 20 px), przyciski min. 60 px, wysoki kontrast, tryb ciemny.

## Jak dodać regułę

1. Dopisz `_r("kod", punkty, "powód prostym językiem", r"wzorzec")` do `RULES` w `app/checks/text_rules.py`. Wzorzec pisz **bez polskich znaków i małymi literami**, bo tekst jest normalizowany.
2. Dodaj przykład oszustwa i przykład zwykłej wiadomości, która NIE powinna się złapać.
3. `python -m pytest -q` i `python -m tests.evaluate`. Sprawdź, czy nie wzrosły fałszywe alarmy.

## Stan projektu (25.11.2026)

Zrobione:
- Działający szkielet MVP: API, reguły, analiza domen, lista CERT, opcjonalne AI, strona PWA z „Udostępnij” na Androidzie, 47 testów.
- Repo na GitHubie, commit „Szkielet projektu Czy to oszustwo?”.
- PR #1 (`ci/github-actions`): GitHub Actions z testami, plakietka w README, `railway.json`. Testy w CI przeszły. **Czeka na merge Kacpra.**

Znane ograniczenia:
- Zestaw przykładów pisał autor reguł, więc wynik 16/16 i 0 fałszywych alarmów jest przeuczony. Prawdziwy obraz da zestaw realny (zadanie niżej).
- Pobieranie listy CERT sprawdzone tylko lokalnie u Kacpra (jeśli `/api/health` pokazuje `cert_domains: 0`, zbadaj logi).
- AI nie było testowane na prawdziwym API, tylko na podstawionej odpowiedzi.
- `registrable_domain` to uproszczenie bez Public Suffix List (kandydat: biblioteka `tldextract`).
- Rate limit w pamięci: działa na jednej instancji.
- Brak obsługi zrzutów ekranu, brak wieku domeny.

## Zadania

### Teraz (tydzień 1–2)

- [ ] **[Kacper]** Zmergować PR #1 i zrobić `git pull`.
- [ ] **[Kacper]** Sprawdzić `/api/health` (czy `cert_domains` > 0) i `pytest`.
- [ ] **[Kacper]** Przeczytać kod w kolejności: `main.py` → `analyzer.py` → `checks/text_rules.py` → `checks/domain.py` → `checks/links.py` → `static/app.js`. Pytania zapisać i omówić z Claude.
- [ ] **[Claude]** Zestaw realnych przykładów (gałąź `data/real-examples`):
  - Zbadaj prawdziwe kampanie: telegraf.cert.pl, miesięczne podsumowania CERT Polska, ostrzeżenia banków, policji, mObywatela (2025–2026). Różnorodność: paczki, prąd/gaz, BLIK „na znajomego”, „mamo nowy numer”, e-TOLL/mandaty, zwrot podatku, mObywatel/PESEL, fałszywe banki i aplikacje, OLX/Vinted „odbierz płatność”, inwestycje/krypto, praca za lajki, WhatsApp, „bezpieczne konto”, kody QR.
  - Nowy plik `tests/examples_real.py`: `REAL_SCAMS` (~35, krotki `(tekst, "scam"|"suspicious")` z komentarzem źródła) i `REAL_LEGIT` (~25 zwykłych wiadomości). Treści przeformułowane, domeny zmyślone, bez prawdziwych danych.
  - `tests/evaluate.py`: osobne wyniki dla zestawu podstawowego i realnego + lista pomyłek realnego.
  - **Nie zmieniaj reguł** i nie dodawaj zestawu realnego do pytest. W opisie PR: źródła z linkami, wynik evaluate, tabela pomyłek jako lista zadań dla Kacpra.
- [ ] **[Claude]** Audyt dostępności i UX (gałąź `ux/accessibility`):
  - Zrzuty ekranu telefon 375×812 i desktop, jasny i ciemny motyw, stan pusty i trzy werdykty.
  - Kontrast WCAG AA (z wartościami przed/po), fokus, kolejność tabulacji, `aria-live`/`aria-busy`, emoji ukryte przed czytnikiem, cele dotyku ≥ 48 px, powiększenie 200%, czytelny komunikat offline, wskazówka „dodaj do ekranu” tylko na iOS Safari (z zamknięciem zapamiętanym w localStorage w try/catch).
  - Bez bibliotek i zewnętrznych czcionek, bez zmian w `app/`. Podbij wersję cache w `sw.js`.
- [ ] **[Kacper]** Na podstawie pomyłek z zestawu realnego poprawić 1–2 reguły na raz (z code review od Claude).
- [ ] **[Kacper]** Dodać 20 własnych zwykłych SMS-ów (po usunięciu danych) do `REAL_LEGIT`.

### Tydzień 3
- [ ] Włączyć AI z prawdziwym kluczem, przetestować na 20 wiadomościach, sprawdzić koszty i czas odpowiedzi. Ustawić miesięczny limit wydatków w konsoli Anthropic.
- [ ] Przetestować PWA na Androidzie: dodanie do ekranu, „Udostępnij” z aplikacji SMS.

### Tydzień 4
- [ ] Wdrożenie na Railway (Variables: `ANTHROPIC_API_KEY`, `DEBUG=false`), wygenerować domenę.
- [ ] Test na 3–5 starszych osobach bez podpowiadania. Spisać, co ich zmyliło.
- [ ] README do portfolio: zrzut ekranu, schemat działania, liczby z evaluate, opis decyzji (AI tylko podnosi, prywatność, koszty).

### Po MVP (dopiero gdy ktoś spoza rodziny używa)
1. Zrzuty ekranu przez model AI z obsługą obrazów.
2. Wiek domeny przez RDAP (świeża domena = mocny sygnał).
3. Tryb opiekuna: powiadomienie dla bliskiej osoby przy czerwonej karcie.
4. Ogłoszenia OLX/Otodom: skradzione zdjęcia, podejrzana cena.
5. Bot Telegram/WhatsApp na tym samym API.
6. Natywna aplikacja (Expo), jeśli dużo użytkowników iPhone'a.

## Ryzyka do pilnowania

| Ryzyko | Zabezpieczenie |
| --- | --- |
| Przepuszczone oszustwo (nowa domena spoza listy CERT) | nigdy „bezpieczne”; zielona karta zawsze przypomina o BLIK/karcie; reguły domen i treści |
| Fałszywe alarmy na prawdziwe SMS-y | zestaw realnych zwykłych wiadomości; oficjalne domeny w `domain.BRANDS` |
| Odpowiedzialność prawna | stopka „narzędzie pomocnicze, nie gwarancja”; przed publicznym startem prosty regulamin i polityka prywatności |
| Dane osobowe (RODO) | maskowanie przed AI, brak zapisu treści, logi tylko z werdyktem |
| Koszty AI i spam | rate limit na IP, limit długości 3000 znaków, AI tylko przy niepewnym wyniku, limit wydatków u dostawcy |
| Prompt injection | AI tylko podnosi wynik; treść w tagach `<wiadomosc>` jako dane |
| Oszuści uczą się obchodzić reguły | punkty i sygnały ukryte poza DEBUG |
| CERT niedostępny lub zmieni format | kopia na dysku; odrzucenie listy krótszej niż 100 domen |
| Seniorzy nie ogarną strony | jeden ekran, duże elementy, test na ludziach w tygodniu 4 |
| Brak czasu przy studiach | twardy zakres MVP; reszta tylko na liście „Po MVP” |
