# System projektowy „Czy to oszustwo?”

Strona jest dla seniorów, więc najważniejsze są czytelność i pewność, że dotyk zadziałał. Wszystkie wartości są zmiennymi CSS w `static/style.css` (`:root`). W regułach CSS nie wpisujemy kolorów, odstępów ani rozmiarów czcionek na sztywno.

## Zasady

1. **Duże i czytelne.** Czcionka bazowa to 20 px, główny przycisk ma 64 px wysokości, a każdy inny cel dotyku co najmniej 48 px.
2. **Kontrast co najmniej 4.5:1** dla tekstu i 3:1 dla ramek pól, w obu motywach.
3. **Jedna kolumna, jedno główne działanie.** Na ekranie jest tylko jeden wyróżniony przycisk.
4. **Kolor nigdy nie jest jedyną informacją.** Werdykt ma też ikonę i tytuł.
5. **Bez inline JS i CSS** (CSP). Ikony są w jednym `<svg class="sprite">` i używane przez `<use href="#i-...">`.

## Tokeny

### Kolory

| Token | Jasny | Ciemny | Do czego |
|---|---|---|---|
| `--bg` | #f4f2ed | #0f1216 | tło strony |
| `--surface` | #ffffff | #181c22 | karty, pola, nagłówek |
| `--text` | #16191d | #eef0f3 | tekst |
| `--muted` | #4b5563 | #b4bcc8 | tekst pomocniczy |
| `--line` | #ddd8cd | #2e353f | linie i ramki kart |
| `--field-border` | #6b7280 | #8a94a3 | ramka pola i przycisku drugorzędnego |
| `--primary` | #1f4fa3 | #9cc0ff | kolor marki, główny przycisk, linki |
| `--primary-hover` / `--primary-active` | #183f84 / #12306a | #c2d8ff / #dbe8ff | stany głównego przycisku |
| `--on-primary` | #ffffff | #0b1626 | tekst na głównym przycisku |
| `--primary-soft` | #e8eef9 | #1c2a42 | tło przycisku „ghost” i wskazówki |
| `--focus` | #1f4fa3 | #c2d8ff | obwódka fokusu z klawiatury |
| `--link-visited` | #5b3a9e | #c9b2ff | odwiedzony link |

Kolory werdyktów nazywają się tak jak wartości `verdict` w API:

| Token | Jasny | Ciemny |
|---|---|---|
| `--scam` / `--scam-soft` | #b3261e / #fdf0ee | #ffb4ab / #2a1513 |
| `--suspicious` / `--suspicious-soft` | #8f5100 / #fff6e0 | #ffd27a / #2a2110 |
| `--no-signs` / `--no-signs-soft` | #1e7a3c / #ebf6ee | #8fdba6 / #12241a |
| `--on-verdict` | #ffffff | #16191d |

Karta werdyktu ustawia sobie `--tone` i `--tone-soft` z odpowiedniej pary, a pasek, tło i kropki przy radach biorą kolor z `--tone`.

### Odstępy

`--space-1` 4 px · `--space-2` 8 · `--space-3` 12 · `--space-4` 16 · `--space-5` 20 · `--space-6` 24 · `--space-7` 32 · `--space-8` 48

### Typografia

| Token | Wartość | Gdzie |
|---|---|---|
| `--text-sm` | 0.85rem (17 px) | stopka, pasek zaufania, licznik, przycisk „ghost” |
| `--text-base` | 1rem (20 px) | zwykły tekst, pole |
| `--text-md` | 1.15rem (23 px) | główny przycisk |
| `--text-lg` | 1.5rem (30 px) | tytuł werdyktu |
| `--text-xl` | 1.6–2.1rem | nagłówek strony |

Grubości: `--weight-semibold` 600, `--weight-bold` 700, `--weight-heavy` 800. Interlinia: `--leading` 1.5, `--leading-tight` 1.2.

### Pozostałe

`--radius` 16 px (karty) · `--radius-sm` 12 px (pola, przyciski) · `--shadow` (w ciemnym motywie brak) · `--duration-spin` 0.8 s · `--tap-min` 48 px · `--tap-comfortable` 56 px · `--tap-main` 64 px

## Komponenty

### Logo w nagłówku `a.brand`

Tarcza i napis „Czy to oszustwo?” w `.site-header` to link do strony głównej, taki sam na każdej stronie:

```html
<a class="brand" href="/" aria-label="Czy to oszustwo? – strona główna">
```

- Na stronie głównej ma dodatkowo `aria-current="page"` (czytnik ekranu powie, że to bieżąca strona).
- Wygląda jak napis, nie jak link: kolor `--text`, bez podkreślenia i bez koloru odwiedzonego linku.
- Wysokość `--tap-main` (64 px), klikalny jest tylko napis z tarczą, a nie cały pasek.
- Stany: hover podkreśla nazwę (2 px), focus to obwódka 3 px `--focus` z zaokrągleniem `--radius-sm`, rysowana w środku linku (`outline-offset: -3px`), bo na zewnątrz ucięłaby ją górna krawędź ekranu. Wewnętrzny odstęp `--space-2` z ujemnym marginesem trzyma logo w linii z treścią.
- `aria-label` zaczyna się od widocznego tekstu, więc sterowanie głosem („kliknij Czy to oszustwo”) działa.

### „Przejdź do treści” `.skip-link`

Pierwszy element w `<body>` każdej strony: `<a class="skip-link" href="#tresc">`, a `<main>` ma `id="tresc"`. Jest schowany nad ekranem i wysuwa się w lewym górnym rogu dopiero po naciśnięciu Tab (tło `--primary`, tekst `--on-primary`, min. 48 px). Osoba z klawiaturą lub czytnikiem ekranu pomija nim nagłówek.

### Przycisk `.btn`

| Wariant | Kiedy | Wysokość |
|---|---|---|
| `.btn--primary` | jedno główne działanie na ekranie („Sprawdź wiadomość”) | 64 px |
| `.btn--secondary` | działanie poboczne („Sprawdź inną wiadomość”) | 56 px |
| `.btn--ghost` | małe działanie pomocnicze obok pola („Wklej ze schowka”) | 48 px |
| `.btn--full` | dodatkowo: na całą szerokość | — |

| Stan | Wygląd |
|---|---|
| hover | ciemniejsze tło (primary) albo niebieska ramka (secondary) |
| active | przesunięcie o 1 px i ciemniejsze tło: widać, że dotyk zadziałał |
| focus | obwódka 3 px `--focus` |
| ładowanie | `aria-disabled="true"`, klasa `.is-busy`, kręcące się kółko i napis „Sprawdzam…” |

Nie używamy `disabled`, bo przycisk traciłby fokus z klawiatury.

### Pole tekstowe

Etykieta jest zawsze widoczna. Bez `maxlength`: zamiast cicho ucinać tekst, od 2500 znaków pokazujemy licznik `2650 / 3000 znaków`, powyżej 3000 licznik robi się czerwony, a przy próbie sprawdzenia pojawia się komunikat. Stany: hover, focus i błąd (`aria-invalid`, czerwona ramka, komunikat w `role="alert"`).

### Karta werdyktu `.verdict`

Klasa `scam`, `suspicious` albo `no_signs` (z API). Na górze kolorowy pasek z ikoną, napisem „Wynik sprawdzenia” i tytułem (`h2`, dostaje fokus po sprawdzeniu). Pod spodem lista rad `.steps` z kolorowymi kropkami. Zielona karta nigdy nie mówi „bezpieczne”.

### „Dlaczego tak uważamy?” `.reasons`

Natywne `<details>`, plus i minus zamiast trójkąta, cały pasek klikalny (56 px). Maksymalnie 3 powody.

### Pozostałe

- `.trust`: trzy krótkie zdania z ikoną. Na telefonie są w jednej kolumnie, od 720 px w trzech.
- `.hint`: wskazówka „dodaj do ekranu głównego”, tylko iOS Safari.
- `.site-footer`: numer 8080, zastrzeżenie i `.footer-links` (Poradniki, Prywatność, Regulamin, kod na GitHubie). Linki łamią się do nowej linii na wąskim ekranie, każdy ma min. 48 px wysokości, a link do bieżącej strony ma `aria-current="page"` (pogrubiony, bez podkreślenia).

### Strony z tekstem `.prose`

`prywatnosc.html` i `regulamin.html` mają ten sam nagłówek i stopkę co strona główna, a treść w `<main class="wrap prose">`. Nie potrzebują JS.

- `h2` w rozmiarze `--text-md`, akapity i listy maks. 34em szerokości, krótkie zdania.
- `.back-link` „← Wróć do sprawdzania” na górze i na dole: pogrubiony link, min. 48 px wysokości.
- `mark` oznacza pola `[DO UZUPEŁNIENIA: …]` (tło `--suspicious-soft`, obwódka `--suspicious`), żeby nie przeoczyć ich przed startem.
- `.updated`: data ostatniej zmiany, mały szary tekst.

## Dostępność

- `role="status"` ogłasza „Sprawdzam…” i „Wynik jest gotowy”, a `aria-busy` jest na formularzu podczas sprawdzania.
- Ikony mają `aria-hidden="true"`, a znaczenie niesie tekst obok.
- Przy `prefers-reduced-motion` kółko się nie kręci, a przyciski się nie przesuwają.
- Strona działa bez poziomego przewijania przy 375 px, przy zoomie 200% i przy tekście 200%.

## Nowa podstrona: obowiązkowy `<head>`

Każdy plik HTML w `static/` musi mieć (pilnuje tego `tests/test_guards.py`):

- `<html lang="pl">`, unikalny `<title>` (do 60 znaków) i `<meta name="description">` (do 160 znaków),
- `<link rel="canonical">` z pełnym adresem na `https://domena.example` (adres bazowy do podmiany po kupnie domeny),
- Open Graph: `og:type`, `og:title`, `og:description`, `og:url` (taki sam jak canonical), `og:image` (ikona 512 px), `og:locale` = `pl_PL`, oraz `twitter:card` = `summary`,
- skip link, nagłówek z `a.brand` i stopkę jak na pozostałych stronach,
- wpis w `static/sitemap.xml`.

## Jak dodać nowy element

1. Użyj istniejących tokenów. Jeśli czegoś brakuje, dodaj token w `:root` w obu motywach, zamiast wpisywać wartość na sztywno.
2. Sprawdź kontrast nowych kolorów (min. 4.5:1).
3. Zdefiniuj stany: hover, active, focus, a jeśli trzeba, ładowanie i błąd.
4. Dopisz element do tego dokumentu.
