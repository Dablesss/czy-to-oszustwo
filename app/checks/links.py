"""Wyciąganie linków i domen z tekstu wiadomości.

Oszuści często piszą linki bez "https://" (np. "inpost-doplata.pl/abc"),
więc szukamy też gołych domen.
"""

import ipaddress
import re
from urllib.parse import urlsplit

# Link z protokołem albo goła domena z końcówką z liter (min. 2), opcjonalnie ze ścieżką.
# (?<![@\w.-]) pomija adresy e-mail i fragmenty innych słów.
_URL_RE = re.compile(
    r"(?<![@\w.-])"
    r"((?:https?://)?"
    r"(?:(?:[a-z0-9 -￿](?:[a-z0-9 -￿-]{0,61}[a-z0-9 -￿])?\.)+"
    r"(?:[a-z -￿]{2,63}|xn--[a-z0-9-]{2,59})"
    r"|(?:https?://)\d{1,3}(?:\.\d{1,3}){3})"
    r"(?::\d{2,5})?"
    r"(?:/[^\s<>\"']*)?)",
    re.IGNORECASE,
)

# Goła domena (bez "https://") musi mieć znaną końcówkę. Bez tego "Witaj.Twoja paczka"
# zostałoby uznane za domenę "witaj.twoja". Link z "https://" przyjmujemy z każdą końcówką.
_KNOWN_TLDS = {
    "pl", "com", "net", "org", "eu", "info", "biz", "io", "app", "me", "co", "cc", "tv", "online",
    "site", "shop", "store", "xyz", "top", "icu", "sbs", "click", "live", "cfd", "buzz", "rest",
    "monster", "vip", "link", "website", "space", "fun", "life", "pro", "cloud", "today", "best",
    "lol", "cyou", "bond", "quest", "ru", "de", "uk", "cz", "sk", "ua", "lt", "fr", "it", "es",
    "nl", "us", "ly", "gd", "at", "be", "ch", "dev", "page", "work", "world", "win", "help",
}


def normalize_host(host: str) -> str:
    """Małe litery, bez "www.", bez kropki na końcu, w zapisie punycode (xn--)."""
    host = host.strip().strip(".").lower()
    if host.startswith("www."):
        host = host[4:]
    try:
        host = host.encode("idna").decode("ascii")
    except UnicodeError:
        pass
    return host


def extract_hosts(text: str) -> list[str]:
    """Zwraca listę unikalnych hostów znalezionych w tekście (w kolejności wystąpienia)."""
    hosts: list[str] = []
    for match in _URL_RE.finditer(text):
        raw = match.group(1).rstrip(".,;:!?)]}")
        url = raw if "://" in raw else f"http://{raw}"
        host = urlsplit(url).hostname
        if not host:
            continue
        host = normalize_host(host)
        tld = host.rsplit(".", 1)[-1]
        has_scheme = "://" in raw
        if not has_scheme and tld not in _KNOWN_TLDS and not tld.startswith("xn--"):
            continue
        if host not in hosts:
            hosts.append(host)
    return hosts


def is_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return False


# Domeny drugiego poziomu, pod którymi rejestruje się domeny (np. firma.com.pl).
_SECOND_LEVEL = {
    "com.pl", "net.pl", "org.pl", "gov.pl", "edu.pl", "info.pl", "biz.pl", "waw.pl",
    "co.uk", "org.uk", "com.ua", "com.br", "co.in",
}


def registrable_domain(host: str) -> str:
    """Domena "właściwa", np. dla "konto.allegro.pl.xyz.com" zwraca "xyz.com".

    Uproszczenie bez pełnej Public Suffix List. Po MVP można podmienić na bibliotekę tldextract.
    """
    if is_ip(host):
        return host
    parts = host.split(".")
    if len(parts) >= 3 and ".".join(parts[-2:]) in _SECOND_LEVEL:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])
