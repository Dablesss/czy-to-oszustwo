"""Testy jednostkowe pojedynczych sprawdzeń. Uruchom: pytest"""

from pathlib import Path

from app.checks.cert_list import CertList
from app.checks.domain import analyze_host
from app.checks.links import extract_hosts, registrable_domain
from app.checks.text_rules import check_text, normalize_text
from app.privacy import mask_personal_data


# --- linki ---

def test_extracts_links_with_and_without_scheme():
    text = "Zaplac tu: https://Inpost-Doplata.top/x oraz www.allegro.pl i bit.ly/abc"
    assert extract_hosts(text) == ["inpost-doplata.top", "allegro.pl", "bit.ly"]


def test_ignores_emails_amounts_and_glued_sentences():
    text = "Napisz na jan@firma.pl. Kwota 1,50 zl. Witaj.Twoja paczka jest gotowa."
    assert extract_hosts(text) == []


def test_registrable_domain():
    assert registrable_domain("konto.allegro.pl.evil.com") == "evil.com"
    assert registrable_domain("mojapaczka.dpd.com.pl") == "dpd.com.pl"


# --- domeny ---

def test_official_domain_is_trusted():
    assert analyze_host("allegro.pl") == ("official", [])
    assert analyze_host("login.ipko.pl")[0] == "official"
    assert analyze_host("www.gitd.gov.pl")[0] == "official"
    assert analyze_host("www.t-mobile.pl")[0] == "official"


def test_brand_in_foreign_domain():
    status, signals = analyze_host("inpost-doplata.top")
    codes = {s.code for s in signals}
    assert status == "suspicious"
    assert {"brand_in_foreign_domain", "suspicious_tld"} <= codes


def test_brand_typo_and_leetspeak():
    assert "brand_typo" in {s.code for s in analyze_host("alegro.pl")[1]}
    assert "brand_in_foreign_domain" in {s.code for s in analyze_host("a11egro-oferta.com")[1]}
    assert "brand_in_foreign_domain" in {s.code for s in analyze_host("t-mobile-oplata.top")[1]}


def test_short_brand_needs_separate_token():
    # "gov" wewnątrz słowa "governance" nie jest podróbką gov.pl
    assert analyze_host("governance.com") == ("unknown", [])
    assert "brand_in_foreign_domain" in {s.code for s in analyze_host("gov-pl.info")[1]}


# --- lista CERT ---

def test_cert_list_matches_subdomains(tmp_path: Path):
    cache = tmp_path / "cert.txt"
    cache.write_text("zla-domena.pl\ninna.xyz\n", encoding="utf-8")
    cert = CertList("", cache)
    cert.load_cache()
    assert cert.is_listed("zla-domena.pl")
    assert cert.is_listed("a.b.zla-domena.pl")
    assert not cert.is_listed("dobra-domena.pl")
    assert not cert.is_listed("pl")


# --- treść ---

def test_normalize_text_removes_polish_letters():
    assert normalize_text("DOPŁATA  Żółć") == "doplata zolc"


def test_text_rules_find_typical_scams():
    assert "small_payment" in {s.code for s in check_text("Dokonaj dopłaty 1,99 zł do przesyłki")}
    assert "blik_request" in {s.code for s in check_text("Podeślesz mi kod BLIK?")}
    assert "family_new_number" in {s.code for s in check_text("Mamo, to mój nowy numer")}


def test_text_rules_quiet_on_normal_messages():
    assert check_text("Będę za 10 minut, kupić chleb?") == []
    assert check_text("Kod odbioru paczki: 123456") == []


def test_text_rules_ignore_warnings():
    # Ostrzeżenie banku to nie prośba oszusta ...
    assert check_text("Pracownik banku nigdy nie poprosi Cię o kod BLIK.") == []
    assert check_text("Nigdy nie przelewaj pieniędzy na tzw. bezpieczne konto.") == []
    # ... ale samo "nie" przy prośbie niczego nie zmienia
    assert "blik_request" in {s.code for s in check_text("Podeślij mi kod BLIK, nie mam kasy")}


def test_warning_from_another_sentence_does_not_hide_scam():
    # Oszust dopisuje ostrzeżenie w osobnym zdaniu, żeby wyłączyć regułę: to nie może działać
    codes = lambda t: {s.code for s in check_text(t)}
    assert "blik_request" in codes("Nigdy nie podawaj hasła. Podaj mi teraz kod BLIK, pilne!")
    assert "remote_access_call" in codes("Pamiętaj, nigdy nie klikaj w linki. Zainstaluj AnyDesk, konsultant banku pomoże.")
    assert "remote_access_call" in codes("Nigdy nie podawaj PIN-u, przelej środki na bezpieczne konto.")
    # "nigdy" za dopasowaniem, ale po przecinku i bez czasownika ostrzeżenia
    assert "remote_access_call" in codes("Przelej pieniądze na bezpieczne konto, nigdy nie mów o tym nikomu.")


# --- prywatność ---

def test_masks_personal_data():
    text = "PESEL 90010112345, konto PL61 1090 1014 0000 0712 1981 2874, tel. +48 600 100 200"
    masked = mask_personal_data(text)
    assert "90010112345" not in masked
    assert "1981" not in masked
    assert "600 100 200" not in masked
    assert "[PESEL]" in masked and "[NUMER KONTA]" in masked and "[TELEFON]" in masked
