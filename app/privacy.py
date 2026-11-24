"""Maskowanie danych osobowych, zanim tekst trafi do modelu AI.

Ludzie wkleją prawdziwe wiadomości z PESEL-ami, numerami kont i telefonów.
Do AI wysyłamy tylko wersję zamaskowaną, a treści nigdzie nie zapisujemy.
"""

import re

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
]


def mask_personal_data(text: str) -> str:
    """Zwraca tekst z zamaskowanymi danymi osobowymi."""
    masked = text
    for pattern, replacement in _PATTERNS:
        masked = pattern.sub(replacement, masked)
    return masked
