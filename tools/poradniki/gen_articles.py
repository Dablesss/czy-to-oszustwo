# Generator plików static/artykuly/*.html (narzędzie pomocnicze, nie trafia do repo).
# Wynik to zwykłe pliki HTML, które da się dalej edytować ręcznie.
import sys
from pathlib import Path

OUT = Path(sys.argv[1]) / "static" / "artykuly"
SITE = "https://domena.example"
DATE_TXT = "27.11.2026"
DATE_ISO = "2026-11-27"

SRC = {
    "gov-sms": ("https://www.gov.pl/web/baza-wiedzy/coraz-wiecej-prob-wyludzenia-przez-tzw-falszywe-sms-y-zachowaj-czujnosc",
                "gov.pl: Coraz więcej prób wyłudzenia przez fałszywe SMS-y"),
    "cert-lista": ("https://cert.pl/lista-ostrzezen/", "CERT Polska: Lista ostrzeżeń przed niebezpiecznymi stronami"),
    "cert-incydent": ("https://incydent.cert.pl/", "CERT Polska: formularz zgłaszania incydentów"),
    "mbank-blik": ("https://www.mbank.pl/artykuly/wyludzenie-kodu-blik/", "mBank: Wyłudzenie kodu BLIK"),
    "erste-blik": ("https://www.erste.pl/erste-education/odpal-cyberswiadomosc/oszustwo-na-blik",
                   "Erste Bank Polska: Oszustwo na BLIK-a"),
    "mbank-rodzina": ("https://www.mbank.pl/komunikaty/klienci-indywidualni/10349-uwazaj-na-oszustow-ktorzy-podszywaja-sie-pod-rodzine-lub-znajomych-na-portalach-spolecznosciowych/",
                      "mBank: Uważaj na oszustów, którzy podszywają się pod rodzinę lub znajomych"),
    "wroclaw-tato": ("https://www.wroclaw.pl/dla-mieszkanca/hej-tato-to-moj-nowy-numer-uwazaj-na-oszustow-sa-bezwzgledni",
                     "wroclaw.pl: „Hej tato, to mój nowy numer” – uważaj na oszustów"),
    "policja-tychy": ("https://tychy.policja.gov.pl/k27/prewencja/dla-internautow",
                      "Komenda Miejska Policji w Tychach: porady dla internautów"),
    "pko-pracownik": ("https://www.pkobp.pl/aktualnosci/bezpieczenstwo/oszusci-podszywaja-sie-pod-pracownikow-banku",
                      "PKO Bank Polski: Oszuści podszywają się pod pracowników banku"),
    "mbank-aplikacje": ("https://www.mbank.pl/komunikaty/klienci-indywidualni/9552-uwaga-oszusci-namawiaja-do-instalacji-aplikacji-mowia-ze-zwiekszy-ona-bezpieczenstwo-twoich-pieniedzy-na-koncie-lub-pomoze-w-inwestowaniu/",
                        "mBank: Oszuści namawiają do instalacji aplikacji"),
    "pko-zglos": ("https://www.pkobp.pl/klient-indywidualny/bankowosc-elektroniczna/bezpieczenstwo/jak-zglosic-oszustwo",
                  "PKO Bank Polski: Jak zgłosić oszustwo?"),
    "wroclaw-tauron": ("https://www.wroclaw.pl/dla-mieszkanca/tauron-odlaczenie-energii-elektrycznej-wylaczenie-pradu-falszywe-sms-e-maile",
                       "wroclaw.pl: Tauron – fałszywe SMS-y o odłączeniu prądu"),
    "erste-kupujacy": ("https://www.erste.pl/klient-indywidualny/bankowosc-internetowa/bezpieczne-bankowanie/komunikaty/komunikaty-lista/oszustwo-na-kupujacego",
                       "Erste Bank Polska: Oszustwo „na kupującego” – nie podawaj danych kart"),
    "mf-zwrot": ("https://www.podatki.gov.pl/aktualnosci/uwaga-na-falszywe-wiadomosci-o-zwrocie-podatku",
                 "podatki.gov.pl: Uwaga na fałszywe wiadomości o zwrocie podatku"),
    "mf-podszywanie": ("https://www.gov.pl/web/finanse/uwaga-oszusci-podszywaja-sie-pod-ministerstwo-finansow-i-urzad-skarbowy",
                       "gov.pl: Oszuści podszywają się pod Ministerstwo Finansów i urząd skarbowy"),
    "mobywatel-bws": ("https://info.mobywatel.gov.pl/uslugi/bezpiecznie-w-sieci",
                      "mObywatel: usługa „Bezpiecznie w sieci”"),
    "wroclaw-qr": ("https://www.wroclaw.pl/dla-mieszkanca/falszywe-kody-qr-na-parkomatach-we-wroclawiu",
                   "wroclaw.pl: Fałszywe kody QR na parkomatach we Wrocławiu"),
    "kas-wycieraczka": ("https://www.podatki.gov.pl/aktualnosci/uwaga-na-falszywe-wezwania-do-zaplaty",
                        "podatki.gov.pl: Uwaga na fałszywe wezwania do zapłaty"),
}

# ---------------------------------------------------------------- wspólne fragmenty

def head(title, desc, path, og_type, og_img, og_alt):
    url = f"{SITE}{path}"
    extra = ""
    if og_type == "article":
        extra = (f'\n  <meta property="article:published_time" content="{DATE_ISO}">'
                 f'\n  <meta property="article:modified_time" content="{DATE_ISO}">')
    return f"""<!DOCTYPE html>
<html lang="pl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <!-- Adres bazowy https://domena.example podmień na prawdziwą domenę (patrz SITE_URL w tests/test_guards.py). -->
  <link rel="canonical" href="{url}">
  <!-- Podgląd linku w komunikatorach i serwisach społecznościowych (Open Graph) -->
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="Czy to oszustwo?">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{SITE}{og_img}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="{og_alt}">
  <meta property="og:locale" content="pl_PL">{extra}
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#ffffff" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#181c22" media="(prefers-color-scheme: dark)">
  <link rel="manifest" href="/manifest.json">
  <link rel="icon" href="/icons/icon.svg" type="image/svg+xml">
  <link rel="apple-touch-icon" href="/icons/icon-192.png">
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <a class="skip-link" href="#tresc">Przejdź do treści</a>
  <svg class="sprite" aria-hidden="true" focusable="false">
    <symbol id="i-logo" viewBox="0 0 32 32">
      <path d="M16 3 27 7v8.5c0 6.6-4.6 11.6-11 13.5C9.6 27.1 5 22.1 5 15.5V7Z" fill="currentColor"/>
      <path class="logo-check" d="m11 16 3.5 3.5L21.5 12" fill="none" stroke="#fff" stroke-width="2.8" stroke-linecap="round" stroke-linejoin="round"/>
    </symbol>
  </svg>

  <header class="site-header">
    <div class="wrap header-bar">
      <a class="brand" href="/" aria-label="Czy to oszustwo? – strona główna">
        <svg class="brand-logo" aria-hidden="true"><use href="#i-logo"/></svg>
        <span class="brand-name">Czy to oszustwo?</span>
      </a>
      <nav aria-label="Główne menu">
        <a class="nav-link" href="/artykuly/" aria-current="page">Poradniki</a>
      </nav>
    </div>
  </header>
"""


def footer(current_index=False):
    cur = ' aria-current="page"' if current_index else ""
    return f"""
  <footer class="site-footer">
    <div class="wrap">
      <p class="report">
        Podejrzany SMS zgłoś do CERT Polska: przekaż go na numer <strong>8080</strong>.
      </p>
      <p>To narzędzie pomocnicze, nie gwarancja. W razie wątpliwości zadzwoń do firmy na numer, który znasz.</p>
      <ul class="footer-links">
        <li><a href="/artykuly/"{cur}>Poradniki</a></li>
        <li><a href="/prywatnosc.html">Prywatność</a></li>
        <li><a href="/regulamin.html">Regulamin</a></li>
        <li><a href="https://github.com/Dablesss/czy-to-oszustwo">Kod źródłowy na GitHubie</a></li>
      </ul>
    </div>
  </footer>
</body>
</html>
"""


def ul(items):
    return "<ul>\n" + "\n".join(f"        <li>{i}</li>" for i in items) + "\n      </ul>"


def ol(items):
    return "<ol>\n" + "\n".join(f"        <li>{i}</li>" for i in items) + "\n      </ol>"


def crumbs(current=None):
    items = '<li><a href="/">Strona główna</a></li>'
    if current:
        items += '<li><a href="/artykuly/">Poradniki</a></li>'
    else:
        items += '<li><span aria-current="page">Poradniki</span></li>'
    return f'    <nav class="breadcrumbs" aria-label="Jesteś tutaj"><ol>{items}</ol></nav>\n'


def card(a, lazy=True):
    load = 'loading="lazy" decoding="async"' if lazy else 'decoding="async"'
    return f"""        <li>
          <a class="card" href="/artykuly/{a['slug']}.html">
            <img src="/img/artykuly/{a['slug']}.svg" alt="{a['img_alt']}" width="1200" height="630" {load}>
            <span class="card-body">
              <span class="card-title">{a['h1']}</span>
              <span class="card-desc">{a['card']}</span>
              <span class="card-meta">Czytaj · {minutes(a)} min</span>
            </span>
          </a>
        </li>
"""


def minutes(a):
    """Czas czytania: liczba słów całego poradnika / 180 słów na minutę (spokojne tempo)."""
    texts = [a['lead'], a['example_intro']] + a['short'] + [m[1] for m in a['examples']]
    texts += a.get('how_it_works', []) + a['signs'] + a['todo'] + a['clicked']
    texts += [q + ' ' + x for q, x in a['faq']]
    return max(2, round(len(' '.join(texts).split()) / 180))


CTA = """    <aside class="article-cta" aria-labelledby="cta-title">
      <h2 id="cta-title">Masz podobną wiadomość?</h2>
      <p>Wklej ją na stronie głównej. W kilka sekund zobaczysz, czy ma oznaki oszustwa. Nie zapisujemy treści.</p>
      <a class="btn btn--primary" href="/">Sprawdź swoją wiadomość</a>
    </aside>
"""


def article(a, all_articles):
    path = f"/artykuly/{a['slug']}.html"
    parts = [head(a["title"], a["desc"], path, "article", f"/img/og/{a['slug']}.png", a["img_alt"])]
    parts.append(f"""
  <main id="tresc" class="wrap prose article">
{crumbs(a['h1'])}
    <h1>{a['h1']}</h1>
    <p class="lead">{a['lead']}</p>
    <p class="article-meta">Czas czytania: {minutes(a)} min · Opublikowano <time datetime="{DATE_ISO}">{DATE_TXT}</time> · Zaktualizowano <time datetime="{DATE_ISO}">{DATE_TXT}</time></p>

    <figure class="article-hero">
      <img src="/img/artykuly/{a['slug']}.svg" alt="{a['img_alt']}" width="1200" height="630" fetchpriority="high" decoding="async">
    </figure>

    <section class="summary" aria-labelledby="skrot">
      <h2 id="skrot">W skrócie</h2>
      {ul(a['short'])}
    </section>

    <h2>Jak wygląda taka wiadomość</h2>
    <p>{a['example_intro']}</p>
""")
    for msg in a["examples"]:
        parts.append(f"""    <figure class="example-msg">
      <figcaption>{msg[0]}</figcaption>
      <blockquote><p>{msg[1]}</p></blockquote>
    </figure>
""")
    parts.append("""    <p class="example-note">Przykłady są zmyślone na potrzeby poradnika. Adresy stron w nich nie działają, a mimo to nie wpisuj ich w przeglądarkę.</p>
""")
    if a.get("how_it_works"):
        parts.append(f"""
    <h2>Na czym polega ta sztuczka</h2>
""" + "".join(f"    <p>{p}</p>\n" for p in a["how_it_works"]))
    parts.append(f"""
    <h2>Po czym poznać oszustwo</h2>
      {ul(a['signs'])}

    <h2>Co zrobić, gdy dostaniesz taką wiadomość</h2>
      {ul(a['todo'])}

    <h2>Co zrobić, jeśli już kliknąłem albo podałem dane</h2>
      <p>Nie wstydź się i działaj od razu. Liczy się czas, a oszuści oszukują także ostrożnych ludzi.</p>
      {ol(a['clicked'])}

{CTA}
    <h2>Najczęstsze pytania</h2>
""")
    for q, ans in a["faq"]:
        parts.append(f"    <h3>{q}</h3>\n    <p>{ans}</p>\n")
    parts.append("""
    <h2>Przeczytaj też</h2>
      <ul class="card-grid">
""")
    by_slug = {x["slug"]: x for x in all_articles}
    for s in a["related"]:
        parts.append(card(by_slug[s]))
    parts.append("""      </ul>

    <h2>Źródła</h2>
      <p>Poradnik napisaliśmy własnymi słowami na podstawie ostrzeżeń instytucji i banków:</p>
      <ul class="article-sources">
""")
    for key in a["sources"]:
        url, name = SRC[key]
        parts.append(f'        <li><a href="{url}">{name}</a></li>\n')
    parts.append("""      </ul>

    <a class="back-link" href="/artykuly/"><span aria-hidden="true">←</span> Wszystkie poradniki</a>
  </main>
""")
    parts.append(footer())
    return "".join(parts)


def index(all_articles):
    parts = [head("Poradniki: jak rozpoznać oszustwo · Czy to oszustwo?",
                  "Proste poradniki o najczęstszych oszustwach: SMS o dopłacie do paczki, BLIK od znajomego, "
                  "telefon z banku, fałszywy mandat. Jak rozpoznać i co zrobić.",
                  "/artykuly/", "website", "/img/og/poradniki.png",
                  "Ilustracje poradników: telefon z podejrzanym SMS-em, paczka, kod BLIK i bank")]
    parts.append(f"""
  <main id="tresc">
   <div class="wrap wrap--wide">
{crumbs()}
    <section class="page-hero">
      <h1>Poradniki: jak rozpoznać oszustwo</h1>
      <p class="lead">Krótko i prostym językiem o oszustwach, które najczęściej trafiają do skrzynek SMS i komunikatorów. Każdy poradnik mówi, po czym poznać sztuczkę i co zrobić.</p>
      <p class="article-meta">Zaktualizowano <time datetime="{DATE_ISO}">{DATE_TXT}</time></p>
    </section>

    <h2 class="visually-hidden">Lista poradników</h2>
    <ul class="card-grid">
""")
    for i, a in enumerate(all_articles):
        parts.append(card(a, lazy=i >= 3))
    parts.append("""    </ul>
   </div>
   <div class="wrap prose article">

    <section class="summary" aria-labelledby="zasady">
      <h2 id="zasady">Trzy zasady, które chronią przed większością oszustw</h2>
      <ul>
        <li>Nikomu nie podawaj kodu BLIK, PIN-u, hasła do banku ani danych karty. Bank i policja nigdy o nie nie proszą.</li>
        <li>Nie klikaj linków w nieoczekiwanych SMS-ach. Sprawę sprawdź w aplikacji albo na stronie wpisanej samodzielnie.</li>
        <li>Gdy ktoś Cię pogania, zatrzymaj się. Zadzwoń do firmy albo bliskiej osoby na numer, który znasz.</li>
      </ul>
    </section>
""" + CTA + """   </div>
  </main>
""")
    parts.append(footer(current_index=True))
    return "".join(parts)


from articles_content import ARTICLES  # noqa: E402

OUT.mkdir(parents=True, exist_ok=True)
for a in ARTICLES:
    assert len(a["title"]) <= 60, a["title"]
    assert len(a["desc"]) <= 160, (len(a["desc"]), a["desc"])
    (OUT / f"{a['slug']}.html").write_text(article(a, ARTICLES), encoding="utf-8", newline="\n")
(OUT / "index.html").write_text(index(ARTICLES), encoding="utf-8", newline="\n")
print("OK", len(ARTICLES))
