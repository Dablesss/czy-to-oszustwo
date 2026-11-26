# Zadania dla agentów

Gotowe zlecenia dla agentów (subagentów Claude Code) na kolejne sesje. Każde zlecenie da się skopiować i przekazać agentowi bez dodatkowego kontekstu. Stan na 26.11.2026, po zmergowaniu PR #1–#9.

## Jak uruchamiać

- **Równolegle wolno puszczać tylko zadania z różnych grup plików** (kolumna „Pliki” w tabeli). Zadania z tej samej grupy uruchamiaj po kolei.
- Po zakończeniu agenta: przejrzyj diff, uruchom `python -m pytest -q` i `python -m tests.evaluate`, załóż PR z opisu, który zostawił agent.
- Zadania ze znacznikiem **[właściciel]** wymagają konta, klucza, telefonu albo decyzji właściciela. Agent ich nie zrobi.

| # | Zadanie | Gałąź | Pliki (wyłączne) | Zależy od |
|---|---|---|---|---|
| A1 | Reguły: pozostałe pomyłki zestawu realnego | `fix/rules-real-2` | `app/checks/text_rules.py`, `tests/examples*.py` | – |
| A2 | Domeny: Public Suffix List i dopasowanie marek | `fix/domains-psl` | `app/checks/links.py`, `app/checks/domain.py`, `requirements.txt` | – |
| A3 | Serwer: IP za proxy i logi dostępu | `fix/server-privacy` | `app/ratelimit.py`, `Dockerfile`, `static/prywatnosc.html` | – |
| A4 | Maskowanie adresów i imion przed AI | `feat/privacy-mask` | `app/privacy.py`, `tests/test_checks.py` (tylko nowe testy prywatności) | – |
| A5 | Pomiar AI na zestawach (bez klucza: atrapa) | `test/eval-ai` | `tests/eval_ai.py` (nowy) | – |
| A6 | Karta „oszustwo”: przyciski „Zgłoś na 8080” i „Skopiuj” | `feat/report-8080` | `static/*` | po A3 (sw.js) |
| A7 | Wiek domeny przez RDAP | `feat/domain-age` | `app/checks/domain_age.py` (nowy), `app/analyzer.py`, `app/config.py` | po A2 |
| A8 | Instrukcja wdrożenia i lista kontrolna | `docs/deploy` | `docs/wdrozenie.md` (nowy), `README.md` | – |
| A9 | Aktualizacja projektu w Figmie | – (tylko Figma) | plik Figma | po A6 |

Pierwsza fala (równolegle): **A1, A2, A3, A4, A5, A8**. Druga fala: **A6, A7, A9**.

---

## Wspólne zasady (dołącz do każdego zlecenia)

```
Projekt „Czy to oszustwo?”: FastAPI + reguły regex wykrywające polskie oszustwa SMS, strona PWA dla seniorów w static/.
Repo: C:\Users\kapiw\OneDrive\Pulpit\czy-to-oszustwo\czy-to-oszustwo (origin https://github.com/Dablesss/czy-to-oszustwo).
Windows, PowerShell + Git Bash, Python 3.11. Brak `gh`.

Izolacja (równolegle pracują inni agenci):
- NIE zmieniaj gałęzi w głównym katalogu. Utwórz własny worktree w KRÓTKIEJ ścieżce (Windows ma limit długości):
  git -C <repo> fetch origin
  git -C <repo> worktree add <scratchpad>\w-<krótka-nazwa> -b <gałąź> origin/main
  (jeśli `.git/config.lock` blokuje – odczekaj i powtórz).
- Python z istniejącego venv: <repo>\.venv\Scripts\python.exe, uruchamiany z katalogu worktree. Nie twórz venv w worktree.
- Serwer tylko na swoim porcie (podany w zadaniu), w tle; zatrzymaj na końcu.
- Zmieniaj tylko pliki wymienione w zadaniu.

Przeczytaj najpierw CLAUDE.md (zasady projektu) i docs/design-system.md (jeśli ruszasz static/).

Zasady kodu:
- Kod prosty, komentarze po polsku. Właściciel uczy się Pythona i musi rozumieć każdą linijkę.
- Wzorce regex małymi literami i bez polskich znaków (tekst jest normalizowany).
- Nie zmieniaj progów werdyktu, zasady „AI tylko podnosi wynik”, ukrywania punktów poza DEBUG ani CSP (żadnego inline JS/CSS).
- Repo jest publiczne: w przykładach żadnych prawdziwych numerów telefonów, PESEL-i, nazwisk, kont ani działających złośliwych adresów. Domeny oszustów zmyślaj.
- NIE wpisuj imienia właściciela do commitów, opisów PR ani plików. Pisz bezosobowo („Do sprawdzenia”).

Przed commitem: `python -m pytest -q` musi przechodzić. Przy zmianach reguł także `python -m tests.evaluate`:
fałszywe alarmy na LEGIT, REAL_LEGIT i HARD_LEGIT nie mogą wzrosnąć.

Commity po polsku (co było źle, co zmieniono, dlaczego), zakończone linią:
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Push: `git push -u origin <gałąź>`. Nigdy do main, bez merge'a, bez force-push.
Opis PR po polsku zapisz do <scratchpad>\PR-<gałąź>.md, na końcu linia:
🤖 Generated with [Claude Code](https://claude.com/claude-code)

Raport końcowy (krótko): commity, wynik pytest/evaluate przed i po, czego nie zrobiono i dlaczego, ścieżka do opisu PR.
```

---

## A1. Reguły: pozostałe pomyłki zestawu realnego

**Cel:** wykryć oszustwa z `REAL_SCAMS`, które dziś przechodzą, bez nowych fałszywych alarmów.

**Kontekst:** `python -m tests.evaluate` pokazuje 35/44 wykrytych w zestawie realnym, 1/21 alarmów w HARD_LEGIT. Nierozpoznane:
- zwrot paczki do nadawcy / Paczkomat („czekała za długo… anuluj zwrot”),
- OLX „Verify” (konto sprzedawcy wymaga weryfikacji, kupujący opłacił),
- Netflix: nieudana płatność / odnów subskrypcję (domena z literówką już jest łapana, brakuje reguły treści),
- inwestycja „zarabiać od 4000 zł miesięcznie”, „polecane przez ekspertów”,
- praca za lajki / Telegram, „X euro za godzinę”, „Y PLN dziennie”,
- niespodziewana pożyczka („wniosek zaakceptowany, potwierdź wypłatę”),
- „Czy to Państwo sprzedają?” + link oraz Profil Zaufany bez linku: tych **nie** łap na siłę regułą, to przypadki dla AI.
- HARD_LEGIT: „ING: Nie instaluj AnyDesk ani TeamViewer na prośbę osoby, która dzwoni jako konsultant banku” daje fałszywy alarm (ostrzeżenie dalej niż 40 znaków od frazy).

**Kroki:**
1. Przeczytaj `app/checks/text_rules.py` (zwłaszcza `_is_warning`, stałe `ASK_VERB`, `PAY`, `AMOUNT`), `tests/examples_real.py`, `tests/evaluate.py`.
2. Najpierw dopisz do `HARD_LEGIT` po 2 zwykłe wiadomości na każdy nowy schemat (prawdziwe oferty pracy, reklamy inwestycji banku, prawdziwe SMS-y Netflixa/OLX/InPostu o zwrocie), żeby było na czym mierzyć fałszywe alarmy. Osobny commit.
3. Jedna reguła (albo jedna zmiana) = jeden commit, z przykładem oszustwa i zwykłej wiadomości w `tests/examples.py`.
4. Nie zmieniaj `tests/examples_real.py` poza dopisywaniem do `HARD_LEGIT`.

**Gotowe, gdy:** REAL_SCAMS ≥ 40/44 albo opisane, dlaczego nie da się więcej bez fałszywych alarmów; LEGIT, REAL_LEGIT i HARD_LEGIT bez wzrostu alarmów; pytest przechodzi.

---

## A2. Domeny: Public Suffix List i dopasowanie marek

**Cel:** poprawne wyznaczanie domeny właściwej i mniej fałszywych „podróbek marki”.

**Kontekst:**
- `links.registrable_domain` to uproszczenie z ręczną listą `_SECOND_LEVEL`. Domeny typu `x.com.pl`, `x.waw.pl`, `x.github.io`, `x.eu.cc` mogą być źle liczone.
- `domain._find_brand` szuka marki jako fragmentu adresu, więc `sklep-orange-juice.com` dostaje „podróbkę Orange”.

**Kroki:**
1. Dodaj `tldextract` do `requirements.txt` **w trybie offline**: wbudowana lista (`suffix_list_urls=()`), bez pobierania z sieci przy starcie ani w testach. Uzasadnij w commicie.
2. Podmień `registrable_domain` na tldextract, zachowując zachowanie dla IP. Testy dla: `konto.allegro.pl.xyz.com`, `inpost.pl`, `x.com.pl`, `x.waw.pl`, `user.github.io`, `a.b.eu.cc`.
3. Dopasowanie marki: marka musi być osobnym członem adresu (rozdzielonym `-` lub `.`) albo stać na początku domeny; zwykłe słowo obok innych słów w nazwie (`orange-juice`) nie wystarczy. Dodaj przykłady do `tests/examples.py` i testy w `tests/test_checks.py`.
4. Sprawdź, że wynik evaluate się nie pogorszył (szczególnie podróbki z REAL_SCAMS).

**Gotowe, gdy:** testy dla domen z listy przechodzą; evaluate bez pogorszenia; brak dostępu do sieci w testach (sprawdź z wyłączonym internetem albo przez patch).

---

## A3. Serwer: IP za proxy i logi dostępu

**Cel:** limit zapytań nie do obejścia i mniej danych osobowych w logach.

**Kontekst:**
- `app/ratelimit.py: client_ip` bierze **pierwszy** adres z `X-Forwarded-For`, który ustawia klient. Każdy może wpisać losowe IP przy każdym zapytaniu i ominąć limit.
- `Dockerfile` uruchamia uvicorna z `--proxy-headers --forwarded-allow-ips='*'` i z domyślnymi logami dostępu: adres IP, godzina i ścieżka trafiają do logów Railway.

**Kroki:**
1. Ustal i opisz w komentarzu, skąd brać prawdziwe IP za proxy Railway: ostatni adres dopisany przez zaufane proxy albo `request.client.host` po `--proxy-headers`. Napraw `client_ip` i dodaj test, który wysyła 20 zapytań z różnymi sfałszowanymi `X-Forwarded-For` i oczekuje 429 po przekroczeniu limitu.
2. W `Dockerfile` dodaj `--no-access-log` (logi aplikacji z werdyktem zostają) i ogranicz `--forwarded-allow-ips` do tego, co rozsądne dla Railway (opisz wybór).
3. Zaktualizuj sekcję „Adres IP” w `static/prywatnosc.html`: IP służy tylko do limitu w pamięci i nie jest zapisywane w logach. Podbij wersję cache w `static/sw.js`.

**Gotowe, gdy:** test obejścia limitu przechodzi (obejście nie działa); pytest przechodzi; polityka zgodna z kodem.

---

## A4. Maskowanie adresów i imion przed AI

**Cel:** mniej danych osobowych w tekście wysyłanym do Anthropic API.

**Kontekst:** `app/privacy.py: mask_personal_data` maskuje PESEL, konta, karty, telefony, e-maile i kody, ale nie adresy ani imiona i nazwiska. Polityka prywatności mówi o tym wprost.

**Kroki:**
1. Maskuj adresy: `ul./al./os./pl. <Nazwa> <numer>[/<numer>]`, kody pocztowe `NN-NNN`.
2. Imiona: prosta, przewidywalna heurystyka, np. lista ~200 najpopularniejszych polskich imion (plik w `app/data/` albo stała), maskowanie imienia i następnego słowa z wielkiej litery. Nie używaj modeli ML ani nowych bibliotek. Uważaj na marki i miasta (np. „Nowy Sącz”, „Santander”).
3. Testy: co maskujemy i czego **nie** wolno zamaskować (marki, linki, kwoty, słowa kluczowe reguł). Reguły działają na oryginalnym tekście, więc maskowanie nie może zmienić werdyktu reguł; sprawdź to evaluate.
4. Jeśli zakres się udał, zaproponuj w opisie PR zmianę zdania w `static/prywatnosc.html` (samego pliku nie zmieniaj, bo należy do A3).

**Gotowe, gdy:** testy prywatności przechodzą; evaluate bez zmian.

---

## A5. Pomiar AI na zestawach

**Cel:** narzędzie, które pokaże, ile AI poprawia wynik, ile to kosztuje i jak długo trwa, gotowe na dzień, w którym będzie klucz API.

**Kroki:**
1. Nowy skrypt `tests/eval_ai.py` (`python -m tests.eval_ai`). Dla każdej wiadomości z SCAMS, REAL_SCAMS, LEGIT, REAL_LEGIT i HARD_LEGIT: wynik samych reguł, wynik z AI, czy AI w ogóle było pytane, czas, tokeny wejścia/wyjścia (z odpowiedzi API).
2. Bez `ANTHROPIC_API_KEY` skrypt działa na **atrapie** (stała odpowiedź) i wyraźnie to wypisuje. Nie wysyłaj nic do sieci w testach.
3. Opcja `--limit N` (domyślnie 20) i `--yes`: bez `--yes` skrypt pyta o potwierdzenie, zanim użyje prawdziwego klucza. Wypisz szacowany koszt przed startem.
4. Podsumowanie: trafność bez i z AI per zestaw, liczba zapytań do AI, średni czas, suma tokenów.
5. Nie zmieniaj `app/`. Jeśli trzeba czegoś z `llm.py` (np. liczby tokenów), opisz to w raporcie jako propozycję.

**Gotowe, gdy:** skrypt działa na atrapie i daje czytelne podsumowanie; pytest przechodzi.

**[właściciel]** Uruchomienie z prawdziwym kluczem i ustawienie miesięcznego limitu wydatków w konsoli Anthropic.

---

## A6. Karta „oszustwo”: zgłoś na 8080 i skopiuj

**Cel:** senior jednym dotknięciem otwiera SMS do CERT zamiast szukać numeru.

**Kroki:**
1. Na karcie werdyktu `scam` (i tylko tam) przycisk „Zgłoś na 8080”: link `sms:8080`. Treści wiadomości nie wstawiaj do linku (prywatność); poniżej krótka instrukcja „W aplikacji SMS przekaż podejrzaną wiadomość na numer 8080”.
2. Przycisk „Skopiuj treść wiadomości” (Clipboard API, z komunikatem „Skopiowano” przez `role="status"` i obsługą błędu).
3. Komponenty według `docs/design-system.md` (`.btn--secondary`, tokeny), cele dotyku min. 48 px, bez inline JS/CSS. Dopisz komponenty do `docs/design-system.md`.
4. Podbij cache w `static/sw.js`. Port do podglądu: 8011. Zrzuty (telefon 375 px, jasny i ciemny) zapisuj w scratchpadzie, nie w repo.

**Gotowe, gdy:** przyciski działają na karcie oszustwa, a na pozostałych kartach ich nie ma; `tests/test_guards.py` przechodzi.

---

## A7. Wiek domeny przez RDAP

**Cel:** świeżo zarejestrowana domena (np. < 30 dni) to mocny sygnał oszustwa.

**Kroki:**
1. `app/checks/domain_age.py`: zapytanie RDAP (`https://rdap.org/domain/<domena>`) z krótkim timeoutem (np. 2 s), cache w pamięci (np. 24 h), pomijanie domen oficjalnych i z listy CERT.
2. Włączane flagą `DOMAIN_AGE_ENABLED` w `app/config.py` (domyślnie wyłączone). Sygnał np. „domena ma X dni” z punktami tylko poniżej progu. Uzasadnij wartości.
3. Błąd lub timeout RDAP nigdy nie psuje sprawdzenia: brak sygnału i log tylko z kodem błędu, bez domeny użytkownika w logach.
4. Testy z podstawioną odpowiedzią (bez sieci). Zaktualizuj politykę prywatności: domena z linku trafia do zewnętrznej usługi RDAP. Tego pliku nie zmieniaj, opisz zmianę w PR.

**Gotowe, gdy:** testy przechodzą bez sieci; przy wyłączonej fladze zachowanie aplikacji jest identyczne jak dziś.

---

## A8. Instrukcja wdrożenia i lista kontrolna

**Cel:** właściciel wdraża na Railway sam, krok po kroku, bez zgadywania.

**Kroki:**
1. `docs/wdrozenie.md`: Railway (New Project z GitHub, zmienne `ANTHROPIC_API_KEY`, `DEBUG=false`, `LLM_ENABLED`), generowanie domeny, sprawdzenie `/api/health` (`cert_domains` > 0), healthcheck z `railway.json`, rollback, gdzie oglądać logi, jak ustawić limit wydatków u Anthropic.
2. Lista kontrolna przed publicznym startem: pola `[DO UZUPEŁNIENIA]` w `static/prywatnosc.html` i `static/regulamin.html`, `DEBUG=false`, test na telefonie (Android: dodanie do ekranu, „Udostępnij” z SMS, TalkBack), sprawdzenie nagłówków CSP na produkcji.
3. W `README.md` dopisz link do `docs/wdrozenie.md` (jedna linia w sekcji „Uruchomienie”).
4. Nie zmieniaj kodu. Sprawdź tylko, że `Dockerfile` buduje się lokalnie, jeśli Docker jest dostępny. Jeśli nie, napisz to w raporcie.

**Gotowe, gdy:** instrukcja jest kompletna i zgodna z `railway.json` i `Dockerfile`.

**[właściciel]** Logowanie do Railway, wpisanie klucza API, wygenerowanie domeny.

---

## A9. Aktualizacja projektu w Figmie

**Cel:** plik Figma „Czy to oszustwo? – projekt strony” zgodny z kodem.

**Kontekst:** plik powstał przed poprawkami dostępności i stronami prawnymi. Ma zmienne (dwie kolekcje kolorów: jasne i ciemne, bo darmowy plan pozwala na jeden tryb), komponenty i 7 ekranów. Czcionka Roboto.

**Kroki:** dodaj ekrany „Prywatność” i „Regulamin” (telefon), licznik znaków pod polem, przycisk „Zgłoś na 8080” z A6, linki w stopce. Użyj istniejących komponentów i zmiennych, nie wpisuj kolorów na sztywno. Wymaga połączonego MCP Figmy (skill `figma-use` i `figma-generate-design`).

---

## Zadania właściciela (agent ich nie zrobi)

- [ ] Uzupełnić pola `[DO UZUPEŁNIENIA]` w `static/prywatnosc.html` i `static/regulamin.html`.
- [ ] Klucz API Anthropic i miesięczny limit wydatków, potem `python -m tests.eval_ai --yes` (po A5).
- [ ] Wdrożenie na Railway według `docs/wdrozenie.md` (po A8).
- [ ] Test na Androidzie: dodanie do ekranu, „Udostępnij” z aplikacji SMS, TalkBack.
- [ ] Test na 3–5 starszych osobach bez podpowiadania i spisanie, co ich zmyliło.
- [ ] Przegląd i merge PR-ów z zadań A1–A8.
