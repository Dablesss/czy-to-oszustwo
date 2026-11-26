"""Testy maskowania adresów, kodów pocztowych, imion i nazwisk przed AI (app/privacy.py).

Imiona, nazwiska i adresy w przykładach są zmyślone.
"""

import pytest

from app.checks.links import extract_hosts
from app.checks.text_rules import check_text
from app.privacy import mask_personal_data
from tests.examples import LEGIT, SCAMS
from tests.examples_real import HARD_LEGIT, REAL_LEGIT, REAL_SCAMS


# --- co maskujemy ---

@pytest.mark.parametrize("text, hidden", [
    ("Odbior: ul. Marszalkowska 10/5", "Marszalkowska 10/5"),
    ("Zapraszamy na ul. Długą 7a", "Długą 7a"),
    ("Adres: al. Jana Pawła II 12 m. 4", "Pawła II 12"),
    ("Mieszkam na os. Tysiąclecia 3", "Tysiąclecia 3"),
    ("Spotkanie: pl. Grunwaldzki 2, potem ul. 3 Maja 15", "3 Maja 15"),
    ("Dostawa na ulica Polna 8 lok. 2", "Polna 8"),
])
def test_masks_street_address(text, hidden):
    masked = mask_personal_data(text)
    assert hidden not in masked
    assert "[ADRES]" in masked


def test_masks_postal_code_but_keeps_city():
    masked = mask_personal_data("Wyslemy na 00-950 Warszawa")
    assert "00-950" not in masked
    assert "[KOD POCZTOWY]" in masked
    assert "Warszawa" in masked


@pytest.mark.parametrize("text, hidden, tag", [
    ("Dzien dobry, tu Anna Kowalska z banku.", "Anna Kowalska", "[IMIĘ I NAZWISKO]"),
    ("Pozdrawiam, Łukasz Nowak-Wiśniewski", "Nowak-Wiśniewski", "[IMIĘ I NAZWISKO]"),
    ("Lukasz Zielinski, dzial bezpieczenstwa", "Zielinski", "[IMIĘ I NAZWISKO]"),  # bez ogonków
    ("Mamo, tu Kasia. Zgubilam telefon.", "Kasia", "[IMIĘ]"),
    ("Do zobaczenia w poniedzialek, Ola", "Ola", "[IMIĘ]"),
])
def test_masks_first_name_and_surname(text, hidden, tag):
    masked = mask_personal_data(text)
    assert hidden not in masked
    assert tag in masked


def test_masks_surname_after_pan_pani():
    masked = mask_personal_data("Pani Kowalska, Panie Nowak, pani Wiśniewska")
    assert "Kowalska" not in masked and "Nowak" not in masked and "Wiśniewska" not in masked
    assert masked.count("[NAZWISKO]") == 3
    assert masked.startswith("Pani ")  # sam zwrot zostaje, AI wie, że to zwrot do osoby


# --- czego NIE wolno zamaskować ---

@pytest.mark.parametrize("text", [
    "Nowy Sącz, Jelenia Góra, Zielona Góra, Kazimierz Dolny",
    "Santander Bank Polska: logowanie z nowego urzadzenia",
    "InPost: Paczka od Allegro czeka w Paczkomacie KRA05M",
    "Pani Prezes, prosze o kontakt",
    "Swieto 3 Maja, sklepy zamkniete",                     # "Maja" po liczbie to data
    "Zarabiaj 50-300 zl dziennie, 10-500 PLN tygodniowo",   # zakres kwot to nie kod pocztowy
    "Poczta Polska: przesylka czeka w placowce do 02.12.",   # "placowce" to nie "plac"
    "Wejdz na allegro.pl. Kliknij 5 razy",                 # "pl." z linku to nie "plac"
    "ul. Dluga. Zaplac 5 zl teraz",                        # sama nazwa bez numeru to nie adres
])
def test_does_not_mask_places_brands_amounts(text):
    assert mask_personal_data(text) == text


def test_keeps_links_with_names():
    text = "Kliknij https://kasia-paczka.top/Anna albo Kasia.pl"
    masked = mask_personal_data(text)
    assert "kasia-paczka.top/Anna" in masked
    assert "Kasia.pl" in masked


def _text(example):
    return example[0] if isinstance(example, tuple) else example


ALL_EXAMPLES = [_text(e) for s in (SCAMS, LEGIT, REAL_SCAMS, REAL_LEGIT, HARD_LEGIT) for e in s]


@pytest.mark.parametrize("text", ALL_EXAMPLES)
def test_masking_keeps_links_and_rule_keywords(text):
    """AI ma widzieć to samo co reguły: te same linki i te same słowa kluczowe.

    Reguły i tak działają na oryginalnym tekście, ale gdyby maskowanie zjadało
    np. "kod BLIK" albo domenę, AI oceniałoby inną wiadomość niż reguły.
    """
    masked = mask_personal_data(text)
    assert set(extract_hosts(masked)) == set(extract_hosts(text))
    assert {s.code for s in check_text(masked)} == {s.code for s in check_text(text)}
