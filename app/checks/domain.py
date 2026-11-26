"""Analiza domeny: podróbki znanych marek, podejrzane końcówki, skracacze linków.

Ta warstwa łapie oszustwa, których CERT jeszcze nie zdążył dodać do listy.
"""

import re

from ..models import Signal
from .links import is_ip, registrable_domain

# Oficjalne domeny popularnych marek, na które podszywają się oszuści.
# Klucz = słowo, którego szukamy w podejrzanych domenach; wartość = prawdziwe domeny.
BRANDS: dict[str, set[str]] = {
    "inpost": {"inpost.pl", "inpost.eu"},
    "allegro": {"allegro.pl", "allegro.cz", "allegrolokalnie.pl"},
    "olx": {"olx.pl"},
    "vinted": {"vinted.pl", "vinted.com"},
    "pocztapolska": {"poczta-polska.pl", "pocztex.pl", "envelo.pl"},
    "pocztex": {"pocztex.pl"},
    "dpd": {"dpd.com", "dpd.pl", "dpd.com.pl"},
    "dhl": {"dhl.com", "dhl.pl"},
    "pkobp": {"pkobp.pl", "ipko.pl"},
    "ipko": {"ipko.pl"},
    "mbank": {"mbank.pl"},
    "santander": {"santander.pl"},
    "pekao": {"pekao.com.pl", "pekaobiznes24.pl"},
    "millennium": {"bankmillennium.pl"},
    "ingbank": {"ing.pl", "ingbank.pl"},
    "revolut": {"revolut.com"},
    "blik": {"blik.com"},
    "mobywatel": {"gov.pl", "mobywatel.gov.pl"},
    "gov": {"gov.pl"},
    "epuap": {"gov.pl"},
    "zus": {"zus.pl"},
    "podatki": {"podatki.gov.pl", "gov.pl"},
    # Inspekcja Transportu Drogowego: oszuści wysyłają fałszywe mandaty "z GITD".
    # "gitd" jest krótkie (4 litery), więc łapie się tylko jako osobny człon: gitd-mandaty.online
    "gitd": {"gitd.gov.pl", "gov.pl"},
    # Operatorzy komórkowi. Bez "play" i "plus": to zwykłe słowa (np. "playlista", "plusy"),
    # więc dawałyby fałszywe alarmy na zwykłych adresach.
    "orange": {"orange.pl", "orange.com"},
    "tmobile": {"t-mobile.pl", "t-mobile.com"},
    # Firmy energetyczne mają osobne domeny dla operatora sieci (dystrybucji),
    # który wysyła np. SMS-y o planowanych przerwach w dostawie prądu.
    "pge": {"gkpge.pl", "pgeobrot.pl", "pge.pl", "pgedystrybucja.pl"},
    "tauron": {"tauron.pl", "tauron-dystrybucja.pl"},
    "enea": {"enea.pl"},
    "energa": {"energa.pl", "energa-operator.pl"},
    "orlen": {"orlen.pl"},
    "netflix": {"netflix.com"},
    "facebook": {"facebook.com", "fb.com"},
    "whatsapp": {"whatsapp.com"},
}

ALL_OFFICIAL: set[str] = set().union(*BRANDS.values())

SUSPICIOUS_TLDS = {
    "top", "xyz", "icu", "sbs", "click", "shop", "online", "site", "live", "cfd", "buzz", "rest",
    "monster", "vip", "cyou", "bond", "quest", "lol", "fun", "space", "website", "link", "store",
    "help",
}

SHORTENERS = {
    "bit.ly", "tinyurl.com", "t.ly", "is.gd", "cutt.ly", "shorturl.at", "rb.gy", "tiny.pl",
    "t.co", "goo.su", "ow.ly", "v.gd", "s.id", "qrco.de",
}


def is_official(host: str) -> bool:
    return registrable_domain(host) in ALL_OFFICIAL or host in ALL_OFFICIAL


def _edit_distance(a: str, b: str) -> int:
    """Ile zmian dzieli dwa słowa (wstawienie, usunięcie, podmiana, zamiana sąsiednich liter).

    "inpots" -> "inpost" = 1 (zamienione dwie litery), "alegro" -> "allegro" = 1.
    """
    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        d[i][0] = i
    for j in range(len(b) + 1):
        d[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = a[i - 1] != b[j - 1]
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + cost)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
    return d[len(a)][len(b)]


def _find_brand(host: str) -> str | None:
    """Szuka nazwy marki w hoście. Krótkie nazwy (dpd, gov) tylko jako osobny człon adresu."""
    tokens = re.split(r"[-.]", host)
    tokens += [t.translate(_LEET) for t in tokens]
    flat = host.replace("-", "").replace(".", "")
    flats = {flat, flat.translate(_LEET)}
    for brand in BRANDS:
        if len(brand) >= 5:
            if any(brand in f for f in flats):
                return brand
        elif brand in tokens:
            return brand
    return None


# Zamiana cyfr/znaków udających litery: a11egro -> allegro, pk0bp -> pkobp
_LEET = str.maketrans({"0": "o", "1": "l", "3": "e", "4": "a", "5": "s", "7": "t", "@": "a"})


def analyze_host(host: str) -> tuple[str, list[Signal]]:
    """Zwraca status hosta ("official" / "suspicious" / "unknown") i listę sygnałów."""
    if is_official(host):
        return "official", []

    signals: list[Signal] = []
    domain = registrable_domain(host)
    label = domain.split(".")[0]                    # np. "inpost-doplata"

    # 1. Nazwa marki w domenie, która do tej marki nie należy
    brand_hit = _find_brand(host)
    if brand_hit:
        signals.append(Signal(
            code="brand_in_foreign_domain", points=45, source="domain",
            reason=f"Adres {host} udaje markę „{brand_hit}”, ale do niej nie należy.",
        ))
    else:
        # 2. Literówka w nazwie marki (inpots.pl, alegro.pl)
        typo = next(
            (brand for part in re.split(r"[-.]", host)
             for brand in BRANDS
             if len(brand) >= 5 and len(part) >= 5 and _edit_distance(part, brand) == 1),
            None,
        )
        if typo:
            signals.append(Signal(
                code="brand_typo", points=40, source="domain",
                reason=f"Adres {host} wygląda jak literówka w nazwie „{typo}”.",
            ))

    # 3. Adres IP zamiast nazwy
    if is_ip(host):
        signals.append(Signal(
            code="ip_address", points=30, source="domain",
            reason="Link prowadzi na goły adres IP. Prawdziwe firmy tak nie robią.",
        ))

    # 4. Punycode: znaki udające polskie litery albo łacińskie (np. cyrylica)
    if "xn--" in host:
        signals.append(Signal(
            code="punycode", points=25, source="domain",
            reason="Adres zawiera nietypowe znaki, które mogą udawać zwykłe litery.",
        ))

    # 5. Podejrzana końcówka domeny
    tld = host.rsplit(".", 1)[-1]
    if tld in SUSPICIOUS_TLDS:
        signals.append(Signal(
            code="suspicious_tld", points=15, source="domain",
            reason=f"Końcówka .{tld} jest często używana przez oszustów.",
        ))

    # 6. Skracacz linków ukrywa prawdziwy adres
    if domain in SHORTENERS or host in SHORTENERS:
        signals.append(Signal(
            code="shortener", points=15, source="domain",
            reason="Link jest skrócony, więc nie widać, dokąd naprawdę prowadzi.",
        ))

    # 7. Dużo myślników, np. "poczta-polska-doplata-paczka.com"
    if label.count("-") >= 2:
        signals.append(Signal(
            code="many_hyphens", points=10, source="domain",
            reason="Adres ma nietypowo długą nazwę z wieloma myślnikami.",
        ))

    return ("suspicious" if signals else "unknown"), signals
