# CLAUDE.md — kontekst projektu „Czy to oszustwo?”

Ten plik czyta Claude Code na starcie każdej sesji. Trzymaj go aktualnym: po każdym większym kroku popraw sekcję „Stan projektu”.

## O projekcie

Strona (PWA), na której każdy w kilka sekund sprawdzi podejrzany SMS, wiadomość albo link i dostanie prostą odpowiedź: **oszustwo** (czerwona karta), **podejrzane** (żółta) albo **brak oznak oszustwa** (zielona). Główni użytkownicy to seniorzy i osoby mniej obeznane z technologią, a pośrednio ich dzieci i wnuki, które wysyłają im link.

- Repo: https://github.com/Dablesss/czy-to-oszustwo (publiczne, projekt do portfolio)
- Plan projektu (dokument): https://claude.ai/artifact/SUDbzvhH4D6nkrcttQMXQx

## Właściciel i sposób pracy

- Właściciel: student 2. semestru informatyki inżynierskiej, uczy się Pythona i celuje w pracę przy AI. Projekt ma być w portfolio, więc **właściciel musi rozumieć każdą linijkę**.
- Komunikacja po polsku, krótko i bezpośrednio, bez zbędnych potwierdzeń.
- Pracuje na Windowsie (PowerShell, VS Code). Komendy podawaj w wersji dla PowerShella.
- Zadania oznaczone niżej jako **[właściciel]** robi właściciel sam (albo wymagają jego konta, klucza lub telefonu). Możesz tłumaczyć, podpowiadać i robić code review, ale nie pisz za niego rozwiązania, chyba że wprost o to poprosi.
- **Nie wpisuj imienia właściciela do commitów, opisów PR, komentarzy na GitHubie ani plików w repo.** Pisz bezosobowo.
- Zadania oznaczone **[Claude]** możesz robić samodzielnie, także przez subagentów, równolegle.

## Zasady pracy z repo

- **Nigdy nie pushuj do `main`.** Każda zmiana: osobna gałąź (`ci/...`, `data/...`, `ux/...`, `feat/...`, `fix/...`, `docs/...`, `test/...`) i Pull Request do akceptacji właściciela. Nie merguj sam, chyba że właściciel wprost o to poprosi.
- Brak `gh` na komputerze właściciela: PR-y zakłada się przez przeglądarkę (link `.../compare/main...<gałąź>?expand=1`), opis PR agent zapisuje do pliku.
- Przed commitem: `python -m pytest -q` musi przechodzić. Przy zmianach w regułach uruchom też `python -m tests.evaluate` i wpisz wynik do opisu PR.
- Commity, opisy PR, komentarze w kodzie, teksty na stronie: po polsku.
- Nie commituj `.env`, `.venv`, `data/cert_domains.txt`, zrzutów ekranu.
- Agenci równolegle: każdy we własnym `git worktree` w krótkiej ścieżce (Windows ma limit długości), z Pythonem z `.venv` głównego katalogu. Gotowe zlecenia: `docs/zadania-agentow.md`.
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
static/            index.html, prywatnosc.html, regulamin.html, style.css, app.js, manifest.json (share_target), sw.js, icons/
docs/
  design-system.md   tokeny (kolory, odstępy, czcionki), komponenty, stany, dostępność
  zadania-agentow.md gotowe zlecenia dla agentów
tests/
  examples.py      zestaw podstawowy (SCAMS, LEGIT) używany przez pytest i evaluate
  examples_real.py REAL_SCAMS, REAL_LEGIT (realne kampanie), HARD_LEGIT (trudne zwykłe SMS-y); tylko evaluate
  evaluate.py      pomiar trafności reguł na trzech zestawach
  test_guards.py   pilnuje zasad: CSP bez inline, SW bez /api/, brak treści w logach, ukryte punkty
  test_*.py        testy jednostkowe, API, bezpieczeństwo AI
.github/workflows/tests.yml   CI: pytest i evaluate na każdy PR
railway.json, Dockerfile      wdrożenie na Railway (jeszcze nie wdrożone)
```

## Jak działa sprawdzanie

1. Hosty z tekstu (`links.extract_hosts`).
2. Każdy host: lista CERT (trafienie = 100 pkt, od razu czerwona karta), inaczej `domain.analyze_host`.
3. Reguły treści (`text_rules.check_text`).
4. Bonusy: link do nieoficjalnej strony + prośba o działanie (+15), podróbka marki + jakakolwiek reguła tekstu (+15).
5. Suma punktów, maks. 100. **Od 60 pkt: scam, od 25: suspicious, poniżej: no_signs.**
6. AI tylko gdy wynik jest niepewny (5–59 pkt) albo gdy jest nieznany link i 0 pkt. AI dostaje zamaskowany tekst.

## Kluczowe decyzje (nie zmieniaj bez rozmowy z właścicielem)

- **AI może wynik tylko podnieść, nigdy obniżyć** (`score = max(score, ai.points)`). Chroni przed wiadomościami typu „odpowiedz, że to bezpieczne” (prompt injection). Test: `tests/test_llm_safety.py`.
- **Zielona karta to „nie widzimy oznak oszustwa”, nigdy „bezpieczne”.** Zawsze z przypomnieniem, żeby nie podawać BLIK, PIN-u ani danych karty.
- **Nie zapisujemy ani nie logujemy treści wiadomości.** W logach tylko werdykt. Service worker nie cache'uje `/api/`.
- **Punkty i pełna lista sygnałów są ukryte** (widać je tylko przy `DEBUG=true`), żeby oszuści nie uczyli się obchodzić reguł. Użytkownik widzi maks. 3 powody.
- **CSP bez inline**: żadnych `<script>` ani `style=""` w HTML, tylko pliki z `static/`. Pilnuje tego `tests/test_guards.py`.
- **Wygląd według `docs/design-system.md`**: kolory, odstępy i czcionki tylko przez zmienne CSS, przyciski `.btn` + wariant. Projekt w Figmie: plik „Czy to oszustwo? – projekt strony” (czcionka Roboto).
- **Ostrzeżenia to nie oszustwa**: „pracownik banku nigdy nie poprosi o BLIK” nie może dostać czerwonej karty. `_is_warning` w `text_rules.py` liczy ostrzeżenie tylko w tym samym zdaniu, żeby oszust nie mógł wyłączyć reguły, dopisując „Nigdy nie podawaj hasła.” przed prośbą.
- Przy oszustwie podpowiadamy przesłanie SMS-a na **8080** (numer CERT Polska do zgłaszania).
- Na stronie: jeden ekran, duża czcionka (bazowo 20 px), przyciski min. 60 px, wysoki kontrast, tryb ciemny.

## Jak dodać regułę

1. Dopisz `_r("kod", punkty, "powód prostym językiem", r"wzorzec")` do `RULES` w `app/checks/text_rules.py`. Wzorzec pisz **bez polskich znaków i małymi literami**, bo tekst jest normalizowany.
2. Dodaj przykład oszustwa i przykład zwykłej wiadomości, która NIE powinna się złapać.
3. `python -m pytest -q` i `python -m tests.evaluate`. Sprawdź, czy nie wzrosły fałszywe alarmy.

## Stan projektu (27.11.2026)

W `main` (PR #1–#10): MVP, reguły, zestaw realny i HARD_LEGIT, system projektowy, dostępność, strony prawne v1, README, plan zadań.

**Otwarte PR-y (czekają na merge, kolejność w `docs/zadania-fala-b.md`, krok 0):**
- #11 polityka prywatności i regulamin v2 + treść z „Udostępnij” poza logami (`--no-access-log`, service worker)
- #14 logo jako link, SEO (canonical, OG, robots.txt, sitemap.xml) → bazuje na #11
- #17 8 poradników `/artykuly/` → bazuje na #14
- #18 nowy wygląd: modernizm (czerń/biel/#1c45c4, proste kąty, siatka), ilustracje SVG, obrazy OG, przykłady do kliknięcia, generatory w `tools/poradniki/` → bazuje na #17
- #16 reguły: realny 42/44, HARD_LEGIT 0/33 · #13 domeny (tldextract offline) · #15 maskowanie imion/adresów przed AI · #12 skrypt `tests/eval_ai.py`

Znane ograniczenia:
- Limit zapytań da się obejść sfałszowanym `X-Forwarded-For`; klucze IP zostają w pamięci do restartu (zadanie B6).
- `pko-weryfikacja.xyz` nie jest łapane jako podróbka PKO (B6). Nowe reguły z #16 nie są w `_ASKS_FOR_ACTION` (B6).
- Podstrony (spis, poradniki, prawne) są w starszym stylu niż strona główna z #18 (B1).
- AI nie testowane na prawdziwym API. Strona nie jest wdrożona, adres `https://domena.example` do podmiany.

## Zadania

**Kolejna sesja: `docs/zadania-fala-b.md`** (krok 0: merge PR-ów za zgodą właściciela, potem agenci B1–B9, na koniec integracja). Wspólne zasady dla agentów i starsze zlecenia: `docs/zadania-agentow.md`.

### Właściciel
- [ ] Zgoda na merge PR #11–#18 (albo merge samodzielnie).
- [ ] Uzupełnić pola `[DO UZUPEŁNIENIA]` w `static/prywatnosc.html` i `static/regulamin.html`, notka o projekcie swoimi słowami.
- [ ] Przeczytać poradniki (lista do sprawdzenia w PR #17).
- [ ] Przeczytać kod reguł (`text_rules.py`, zwłaszcza `_is_warning`) i umieć obronić każdą decyzję.

### Tydzień 3
- [ ] **[właściciel]** Włączyć AI z prawdziwym kluczem i uruchomić `python -m tests.eval_ai --yes` (po A5): koszt, czas, trafność. Ustawić miesięczny limit wydatków w konsoli Anthropic.
- [ ] **[właściciel]** Przetestować PWA na Androidzie: dodanie do ekranu, „Udostępnij” z aplikacji SMS, TalkBack.

### Tydzień 4
- [ ] **[właściciel]** Wdrożenie na Railway według `docs/wdrozenie.md` (po A8).
- [ ] **[właściciel]** Test na 3–5 starszych osobach bez podpowiadania. Spisać, co ich zmyliło.
- [x] README do portfolio: schemat działania, liczby z evaluate, opis decyzji. Zostało: zrzut ekranu i link do wdrożonej strony.

### Po MVP (dopiero gdy ktoś spoza rodziny używa)
1. Zrzuty ekranu przez model AI z obsługą obrazów.
2. Wiek domeny przez RDAP: zadanie A7 w `docs/zadania-agentow.md`.
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
