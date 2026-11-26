"""Wyciąganie linków i domen z tekstu wiadomości.

Oszuści często piszą linki bez "https://" (np. "inpost-doplata.pl/abc"),
więc szukamy też gołych domen.
"""

import ipaddress
import re
from urllib.parse import urlsplit

import tldextract

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


def _make_extractor() -> tldextract.TLDExtract:
    """Tworzy tldextract działający w pełni offline.

    - suffix_list_urls=(): nie pobieraj Public Suffix List z internetu,
      użyj kopii wbudowanej w bibliotekę (aktualizuje się razem z wersją tldextract).
    - cache_dir=None: nie zapisuj nic na dysku.
    - include_psl_private_domains=True: domeny typu github.io, netlify.app czy blogspot.com
      traktujemy jak końcówki, bo każdy użytkownik dostaje tam własną stronę.
      "oszust.github.io" należy do oszusta, nie do GitHuba.
    """
    return tldextract.TLDExtract(
        suffix_list_urls=(),
        cache_dir=None,
        include_psl_private_domains=True,
    )


_EXTRACT = _make_extractor()


def registrable_domain(host: str) -> str:
    """Domena "właściwa", czyli ta, którą ktoś kupił i kontroluje.

    Przykłady: "konto.allegro.pl.xyz.com" -> "xyz.com", "sklep.x.com.pl" -> "x.com.pl",
    "user.github.io" -> "user.github.io". Korzysta z Public Suffix List (biblioteka tldextract).
    """
    if is_ip(host):
        return host
    parts = _EXTRACT(host)
    if parts.domain and parts.suffix:
        return f"{parts.domain}.{parts.suffix}"
    # Nieznana końcówka (np. "https://serwer.lokalny") albo sam sufiks (np. "gov.pl"):
    # zostajemy przy dwóch ostatnich członach, tak jak wcześniej.
    return ".".join(host.split(".")[-2:])
