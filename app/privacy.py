"""Maskowanie danych osobowych, zanim tekst trafi do modelu AI.

Ludzie wkleją prawdziwe wiadomości z PESEL-ami, numerami kont i telefonów,
adresami, imionami i nazwiskami. Do AI wysyłamy tylko wersję zamaskowaną,
a treści nigdzie nie zapisujemy.

Reguły (text_rules, domain) działają na ORYGINALNYM tekście, więc maskowanie
nie zmienia ich werdyktu. Zmienia tylko to, co widzi AI.
"""

import re

from .checks.text_rules import normalize_text
from .data_imiona import IMIONA

_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    # Numer konta (IBAN PL albo 26 cyfr, także ze spacjami co 4)
    (re.compile(r"\b(?:PL\s?)?\d{2}(?:[ ]?\d{4}){6}\b", re.IGNORECASE), "[NUMER KONTA]"),
    # Numer karty: 4 grupy po 4 cyfry
    (re.compile(r"\b\d{4}(?:[ -]?\d{4}){3}\b"), "[NUMER KARTY]"),
    # PESEL: dokładnie 11 cyfr
    (re.compile(r"\b\d{11}\b"), "[PESEL]"),
    # E-mail
    (re.compile(r"\b[\w.+-]+@[\w-]+(?:\.[\w-]+)+\b"), "[EMAIL]"),
    # Telefon: +48 / 0048 i 9 cyfr, z odstępami albo bez
    (re.compile(r"(?:\+|00)48[ -]?\d{3}[ -]?\d{3}[ -]?\d{3}\b"), "[TELEFON]"),
    (re.compile(r"\b\d{3}[ -]\d{3}[ -]\d{3}\b"), "[TELEFON]"),
    (re.compile(r"\b\d{9}\b"), "[TELEFON]"),
    # Kod BLIK lub SMS (6 cyfr), gdy stoi obok słowa "kod"
    (re.compile(r"(kod\w*\D{0,15})\b\d{6}\b", re.IGNORECASE), r"\1[KOD]"),
    # Kod pocztowy NN-NNN. Nie ruszamy zakresów kwot typu "50-300 zł".
    (re.compile(r"\b\d{2}-\d{3}\b(?!\s*(?:zł|zl|pln|eur|euro|€|%|tys))", re.IGNORECASE),
     "[KOD POCZTOWY]"),
]

# Wielka litera i małe litery: jedno słowo pisane jak imię albo nazwisko ("Anna", "Łukasz").
_CAP = r"[A-ZĄĆĘŁŃÓŚŹŻ]"
_LOW = r"[a-ząćęłńóśźż]"
_CAP_WORD = rf"{_CAP}{_LOW}+"

# Adres: ul./al./os./pl. (albo pełne słowo) + nazwa (1–4 słowa) + numer domu[/mieszkania].
# - (?<![\w./]) – przed "pl." nie może stać kropka ani litera, żeby nie złapać
#   końcówki linku "allegro.pl. Kliknij…".
# - Słowo nazwy bez kropki na końcu (kropka kończy zdanie), wyjątek: krótkie skróty
#   do 4 liter, np. "gen.", "św.". Każde słowo nazwy kończy się odstępem, więc
#   "ul. Długa. Zapłać 5 zł" nie zostanie wzięte za adres.
_ADDRESS = re.compile(
    r"(?<![\w./])(?i:ul\.|al\.|os\.|pl\.|(?:ulica|ulicy|aleja|alei|osiedle|osiedlu|plac|placu)\b)\s*"
    r"(?:\d{1,2}\s+)?"                              # np. "3" w "ul. 3 Maja"
    r"(?:(?:[^\W\d_]{1,4}\.|[^\W\d_][\w-]*)\s+){1,4}"  # nazwa ulicy
    r"\d+[a-zA-Z]?(?:\s*/\s*\d+[a-zA-Z]?)?"         # numer domu i mieszkania: 12, 12a, 12/5
    r"(?:\s*(?:m\.?|lok\.?)\s*\d+)?\b(?!\.\d)"       # "m. 4", "lok. 2"; "02.12" to data
)

# Słowo z wielkiej litery i (w lookahead) ewentualne następne słowo z wielkiej litery.
# Lookahead nic nie "zjada", więc pętla w _mask_names sama decyduje, ile zamaskować.
# - (?<!\d\s) – nie maskujemy "Maja" w "3 Maja",
# - (?<![\w./@-]) i (?!\.\w) – nie ruszamy kawałków linków i e-maili ("Kasia.pl").
_NAME = re.compile(
    rf"(?<!\d\s)(?<![\w./@-])({_CAP_WORD})\b(?!\.\w)(?=(\s+{_CAP_WORD}(?:-{_CAP_WORD})?\b(?!\.\w))?)"
)

# Zwrot grzecznościowy + nazwisko: "Pani Kowalska", "Panie Nowak".
_HONORIFIC = re.compile(rf"\b((?i:pan|pani|panie|pana|panu|panią|panem))\s+({_CAP_WORD})\b(?!\.\w)")

# Słowa, które stoją z wielkiej litery po imieniu albo "Pani", ale nie są nazwiskami:
# nazwy firm i urzędów, które AI musi zobaczyć, żeby ocenić wiadomość.
_NOT_SURNAMES = {
    "bank", "banku", "polska", "polski", "poczta", "urzad", "policja", "kurier",
    "allegro", "olx", "vinted", "inpost", "paczkomat", "orange", "play", "plus",
    "santander", "pekao", "mbank", "millennium", "alior", "netflix", "blik",
    "prezes", "prezesie", "doktor", "doktorze", "dyrektor", "dyrektorze",
}

# Miejscowości, które zaczynają się od imienia: nie maskujemy ich wcale.
_PLACES = {"kazimierz dolny", "kazimierza dolnego"}


def _mask_names(text: str) -> str:
    """Zamienia imię z listy IMIONA (i ewentualne nazwisko za nim) na znacznik."""
    out: list[str] = []
    pos = 0  # do tego miejsca tekst jest już przepisany do out
    for match in _NAME.finditer(text):
        if match.start() < pos:
            continue  # to słowo zostało już zamaskowane jako nazwisko
        if normalize_text(match.group(1)) not in IMIONA:
            continue
        surname = match.group(2) or ""
        if normalize_text(match.group(1) + surname) in _PLACES:
            continue
        if surname and normalize_text(surname.strip()) in _NOT_SURNAMES:
            surname = ""
        out.append(text[pos:match.start()])
        out.append("[IMIĘ I NAZWISKO]" if surname else "[IMIĘ]")
        pos = match.end() + len(surname)
    out.append(text[pos:])
    return "".join(out)


def _mask_honorific(match: re.Match[str]) -> str:
    """'Pani Kowalska' -> 'Pani [NAZWISKO]', ale 'Pani Prezes' zostaje."""
    if normalize_text(match.group(2)) in _NOT_SURNAMES:
        return match.group(0)
    return f"{match.group(1)} [NAZWISKO]"


def mask_personal_data(text: str) -> str:
    """Zwraca tekst z zamaskowanymi danymi osobowymi."""
    masked = text
    for pattern, replacement in _PATTERNS:
        masked = pattern.sub(replacement, masked)
    # Adres przed imionami: "ul. Jana Pawła II 12" to adres, a nie osoba.
    masked = _ADDRESS.sub("[ADRES]", masked)
    masked = _mask_names(masked)
    masked = _HONORIFIC.sub(_mask_honorific, masked)
    return masked
