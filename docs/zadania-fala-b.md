# Fala B: zadania na kolejną sesję

Plan na jedną dużą sesję: najpierw porządek z otwartymi PR-ami, potem 7 agentów w dwóch rzutach, na koniec integracja. Każdy agent dostaje: sekcję „Wspólne zasady” z `docs/zadania-agentow.md` + swoje zlecenie stąd.

Stan na 27.11.2026: zadania A1, A2, A4, A5 i C1, C2 z fali A są zrobione (PR #13–#17), wygląd strony głównej jest w PR #18. Zostały z fali A: A3 (częściowo), A6, A7, A8, A9. Weszły one do fali B poniżej.

## Krok 0 (Claude, na początku sesji): otwarte PR-y

Fala B buduje na wyglądzie z PR #18, więc najpierw trzeba wciągnąć otwarte PR-y do `main`. **Merge tylko za zgodą właściciela** (zapytaj na starcie sesji). Kolejność:

1. **#11** strony prawne → **#14** logo i SEO → **#17** poradniki → **#18** wygląd (to stos: każdy bazuje na poprzednim; po merge'u bazy GitHub przestawia następny na `main`, ewentualnie zrób to ręcznie przyciskiem „Edit” przy bazie).
2. **#16** reguły, **#13** domeny, **#15** maskowanie, **#12** pomiar AI: dowolnie. Przed każdym sprawdź CI, a po wszystkich: `git pull`, `python -m pytest -q`, `python -m tests.evaluate`.
3. Po merge'u #11 i #15: w `static/prywatnosc.html` (punkt 5, Anthropic) zamień zdanie „Imiona, nazwiska i adresy nie są zakrywane” na zdanie z opisu PR #15.

Jeśli właściciel nie zgodzi się na merge: agenci frontu (B1–B5) startują z `origin/ux/modern`, a backendu (B6, B7) z `origin/main` + opisują zależności w PR.

## Rzut 1 (równolegle, różne pliki)

| # | Zadanie | Gałąź | Pliki (wyłączne) | Port |
|---|---|---|---|---|
| **B1** | Podstrony w nowym stylu (spis, 8 poradników, prywatność, regulamin) | `ux/subpages` | `tools/poradniki/gen_articles.py`, `static/artykuly/*`, `static/prywatnosc.html`, `static/regulamin.html`, `static/style.css` (TYLKO bloki `.prose`, `.article*`, `.card*`, `.breadcrumbs`, `.page-hero`) | 8041 |
| **B2** | Pomoc przy wyniku: „Już kliknąłem”, „Zapytaj bliską osobę”, „Zgłoś na 8080”, „Przeczytaj na głos”, podświetlony link | `feat/result-actions` | `static/index.html` (sekcja `#result`), `static/app.js`, nowy `static/juz-kliknalem.html`, `static/style.css` (TYLKO nowy blok na końcu pliku `/* ===== Pomoc przy wyniku */`) | 8042 |
| **B3** | Quiz „Czy rozpoznasz oszustwo?” | `feat/quiz` | nowe: `static/quiz.html`, `static/quiz.js`, `static/quiz.css` | 8043 |
| **B4** | Ulotka do druku A4 „5 zasad” i strona „Jak używać na telefonie” | `feat/print-and-howto` | nowe: `static/ulotka.html`, `static/print.css`, `static/jak-uzywac.html`, `static/img/jak-uzywac/*` | 8044 |
| **B6** | Backend: obejście limitu (IP), sprzątanie licznika, poprawki AI, marka PKO, nowe reguły w bonusie | `fix/backend-b` | `app/ratelimit.py`, `app/checks/llm.py`, `app/analyzer.py`, `app/checks/domain.py`, `tests/test_backend_b.py` (nowy) | – |
| **B8** | Instrukcja wdrożenia na Railway | `docs/deploy` | `docs/wdrozenie.md` (nowy), `README.md` (1 linia) | – |

## Rzut 2 (po zakończeniu wskazanych zadań)

| # | Zadanie | Po | Gałąź | Pliki |
|---|---|---|---|---|
| **B7** | Wiek domeny przez RDAP (zadanie A7) | B6 | `feat/domain-age` | nowy `app/checks/domain_age.py`, `app/analyzer.py`, `app/config.py`, `tests/test_domain_age.py` |
| **B5** | „Teraz krążą”: aktualne kampanie na stronie głównej | B1, B2 | `feat/now-circulating` | nowy `static/teraz.json`, `static/index.html` (nowa sekcja), `static/app.js` (nowa funkcja), `static/style.css` (nowy blok) |
| **B9** | Figma: zaktualizować projekt do wyglądu z PR #18 i nowych stron | B1, B2 | – | plik Figma „Czy to oszustwo? – projekt strony” |

## Krok końcowy (Claude): integracja

1. Linki do nowych stron: w nagłówku „Poradniki” + menu na telefonie, w stopce: Quiz, Ulotka, Jak używać, Już kliknąłem. W `static/sitemap.xml` nowe adresy. W `static/sw.js` podbić wersję (nowych stron NIE dodawać do SHELL, poza `juz-kliknalem.html`, która ma działać offline).
2. `tests/test_guards.py` sam obejmie nowe pliki HTML (SEO, obrazy, linki) – poprawić to, co nie przejdzie.
3. Zrzuty wszystkich stron (telefon jasny/ciemny, desktop) i krótki przegląd dostępności nowych elementów.
4. Zaktualizować `CLAUDE.md` (stan projektu) i oznaczyć zrobione zadania tutaj.
5. PR-y przez Chrome (bez `gh`), opis bez imienia właściciela, bez merge'a.

---

## B1. Podstrony w nowym stylu

**Cel:** spis poradników, 8 artykułów, prywatność i regulamin wyglądają jak nowa strona główna (PR #18): czerń, biel, jeden kolor `--primary`, proste kąty, grube linie `--rule`, plakatowe nagłówki, etykiety sekcji (`.block`, `.block-label`).

**Kroki:**
1. Przeczytaj `static/index.html`, `static/style.css` (sekcja „Strona główna (modernizm)”), `docs/design-system.md`, `tools/poradniki/README.md`.
2. Spis (`/artykuly/`): tytuł plakatowy, krótki wstęp, lista poradników w stylu `.guide-list` z małą ilustracją po lewej (SVG z `static/img/artykuly/`, `width`/`height`, `loading="lazy"`) zamiast pastelowych kart. Na górze filtr „Najczęstsze / Pieniądze i bank / Paczki i zakupy / Urzędy” jako zwykłe kotwice (bez JS).
3. Artykuł: okruszki, tytuł plakatowy, „W skrócie” jako czarna ramka 2 px, przykłady wiadomości jako ramki jak `.example-btn` (bez przycisku), „Co zrobić” jako numerowana lista z dużymi cyframi jak `.how-list`, CTA jako czarny blok z białym tekstem i przyciskiem, „Przeczytaj też” jak `.guide-list`. Spis treści (kotwice do H2) na górze artykułów dłuższych niż 3 min.
4. Prywatność i regulamin: ten sam styl tekstu, spis treści na górze, pola `[DO UZUPEŁNIENIA]` dalej wyróżnione.
5. Zmiany w HTML poradników rób w `gen_articles.py` i uruchom generator (nie edytuj wygenerowanych plików ręcznie). Usuń z CSS klasy, których żadna strona już nie używa (np. `.eyebrow`, `.trust`) – sprawdź grepem po `static/`, zanim usuniesz. `.hint` zostaje (wskazówka dla iPhone'a).
6. Testy (`pytest`), zrzuty: spis, 2 artykuły, prywatność; telefon jasny/ciemny, desktop; tekst 200%.

**Gotowe, gdy:** wszystkie podstrony w jednym stylu ze stroną główną, testy przechodzą, brak poziomego przewijania, kontrast min. 4,5:1 (policz i wpisz do PR).

## B2. Pomoc przy wyniku

**Cel:** w chwili, gdy ktoś dostał podejrzaną wiadomość albo już kliknął, strona prowadzi go do konkretnego działania.

**Kroki:**
1. Nowa strona `static/juz-kliknalem.html` „Kliknąłem albo podałem dane – co teraz?”: kroki od najpilniejszego (zablokuj kartę w aplikacji banku lub telefonicznie, zadzwoń do banku na numer z karty, zmień hasło, zastrzeż PESEL w mObywatelu, zgłoś na policji/112, przekaż SMS na 8080). Duże przyciski `tel:` tylko dla numerów, które sprawdzisz w oficjalnych źródłach (gov.pl, CERT, banki) i podasz źródło w PR. Jeśli numeru nie da się potwierdzić, nie wpisuj go. Strona ma działać offline (dodaj do SHELL w `sw.js`).
2. Przy wyniku (karta werdyktu) przyciski:
   - **„Już kliknąłem w link”** → `/juz-kliknalem.html` (na czerwonej i żółtej karcie),
   - **„Zgłoś na 8080”** → `sms:8080` (tylko czerwona karta; treści SMS-a NIE wstawiaj do linku), pod spodem jedno zdanie „W aplikacji SMS przekaż podejrzaną wiadomość na numer 8080”,
   - **„Zapytaj bliską osobę”** → Web Share API (`navigator.share`) z tekstem „Sprawdziłem wiadomość na Czy to oszustwo?. Wynik: <tytuł werdyktu>. Możesz zerknąć?” i adresem strony; bez treści wiadomości; gdy `navigator.share` niedostępne – link `sms:?body=...` z tym samym tekstem,
   - **„Przeczytaj na głos”** → `speechSynthesis` (język `pl-PL`), czyta tytuł i rady; przycisk zmienia się na „Zatrzymaj”; ukryty, gdy przeglądarka nie obsługuje.
3. **Podświetlony link:** API już zwraca `links` (host + status). W wyniku pokaż „Podejrzany adres: <host>” przekreślony czerwonym przy statusie innym niż `official` (tekst przez `textContent`, nigdy `innerHTML`).
4. Style tylko w nowym bloku na końcu `style.css`, cele dotyku min. 48 px, `aria-live` nie może czytać dwa razy tego samego.
5. Testy: rozszerz `tests/test_guards.py` tylko jeśli potrzeba; test API, że `links` jest w odpowiedzi.

**Gotowe, gdy:** przyciski działają na trzech werdyktach (sprawdź przykładami ze strony głównej), strona „Już kliknąłem” działa offline, testy przechodzą.

## B3. Quiz „Czy rozpoznasz oszustwo?”

**Cel:** 8 wiadomości (5 oszustw, 3 zwykłe) z prostym pytaniem „Oszustwo czy nie?”, po odpowiedzi wyjaśnienie i link do poradnika. Uczy bez straszenia, dobre do udostępniania.

**Kroki:** `static/quiz.html` (ten sam nagłówek/stopka i SEO co inne strony, własny obraz OG wygenerowany jak w `tools/poradniki/gen_og.py`), `static/quiz.js` (bez bibliotek, stan w pamięci, wynik „6/8” na końcu i przycisk „Spróbuj jeszcze raz”), `static/quiz.css`. Treści zmyślone w stylu `tests/examples_real.py`. Dostępność: przyciski min. 64 px, fokus na wyjaśnieniu po odpowiedzi, `aria-live`. Bez zapisywania wyników gdziekolwiek.

## B4. Ulotka do druku i „Jak używać na telefonie”

1. `static/ulotka.html` + `static/print.css` (`@media print`): jedna strona A4, „5 zasad, które chronią przed oszustwami”, numer 8080, adres strony, kod QR do strony **wygenerowany lokalnie jako SVG** (prosty generator w Pythonie w `tools/`, bez zewnętrznych usług; adres `https://domena.example` do podmiany). Przycisk „Drukuj” (`window.print()` w pliku JS, nie inline).
2. `static/jak-uzywac.html`: obrazkowa instrukcja „Jak sprawdzić SMS bez kopiowania” – Android: dodanie do ekranu głównego i „Udostępnij → Czy to oszustwo?”; iPhone: kopiowanie i wklejanie. Ilustracje SVG w stylu `tools/poradniki/gen_illustrations.py` (telefon + strzałki/kroki), `alt` dla każdej.

## B6. Backend

1. **IP za proxy:** `client_ip` bierze pierwszy adres z `X-Forwarded-For` (do sfałszowania). Ustal poprawne źródło za Railway (ostatni adres dopisany przez proxy albo `request.client.host` po `--proxy-headers`), test: 20 zapytań ze zmiennym sfałszowanym nagłówkiem → 429.
2. **Licznik limitu:** usuwaj klucze IP z pustą kolejką (dziś zostają w pamięci do restartu); zaktualizuj zdanie o IP w `prywatnosc.html` tylko jeśli B1 jeszcze nie ruszał tego pliku – inaczej opisz zmianę w PR.
3. **`llm.py`** (propozycje z PR #12): sprawdzanie `stop_reason` (`refusal`, `max_tokens` → `None` + log samego powodu), `max_tokens` z zapasem, logowanie tokenów i czasu bez treści. Zanim zmienisz parametry API, sprawdź aktualną dokumentację (skill `claude-api`).
4. **`_ASKS_FOR_ACTION`** w `analyzer.py`: dopisz reguły z PR #16 (`loan_approved`, `parcel_return_cancel`, `seller_verification`, `payment_failed`, `qr_payment`?), evaluate przed/po, fałszywe alarmy nie mogą wzrosnąć.
5. **Marka PKO:** `pko-weryfikacja.xyz` nie jest dziś łapane (w `BRANDS` jest `pkobp`, `ipko`). Dodaj krótkie `pko` jako całe słowo z testami na fałszywe alarmy.

## B7. Wiek domeny (RDAP)

Zlecenie A7 z `docs/zadania-agentow.md`, bez zmian. Domyślnie wyłączone flagą; zaktualizuj opis w PR o polityce prywatności (domena z linku trafia do usługi RDAP).

## B8. Instrukcja wdrożenia

Zlecenie A8 z `docs/zadania-agentow.md` + uwzględnij: `--no-access-log` (już w `Dockerfile`), podmiana `https://domena.example` (polecenie z PR #14), region serwera w UE (do polityki prywatności), limit wydatków Anthropic, `python -m tests.eval_ai` przed włączeniem AI.

## B5. „Teraz krążą”

Sekcja na stronie głównej z 3 aktualnymi kampaniami oszustw. Dane w `static/teraz.json` (tytuł, 1 zdanie, data, link do poradnika lub źródła). Treści na podstawie ostrzeżeń CERT Polska/banków z ostatnich tygodni (źródła w PR, przykłady zmyślone). JSON wczytywany przez `fetch` w `app.js`, a bez JS / offline sekcja się nie pokazuje. Dopisz w `tools/poradniki/README.md`, jak aktualizować plik.

## B9. Figma

Zaktualizuj plik „Czy to oszustwo? – projekt strony” do wyglądu z PR #18 (czerń/biel/`#1c45c4`, proste kąty, grube linie) i dodaj ekrany: spis poradników, artykuł, „Już kliknąłem”, quiz. Użyj istniejących zmiennych (podmień wartości kolorów i zaokrągleń), skill `figma-use` + `figma-generate-design`.

---

## Zadania właściciela (fala B)

- [ ] Zgoda na merge PR #11–#18 na początku sesji (albo merge samodzielnie).
- [ ] Pola `[DO UZUPEŁNIENIA]` w prywatności i regulaminie, notka o projekcie swoimi słowami.
- [ ] Przeczytać 8 poradników i odhaczyć listę z PR #17.
- [ ] Klucz API i limit wydatków, potem `python -m tests.eval_ai --yes`.
- [ ] Wdrożenie według `docs/wdrozenie.md` (po B8), test na telefonie i na 3–5 starszych osobach.
