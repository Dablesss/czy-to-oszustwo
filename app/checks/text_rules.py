"""Reguły na treść wiadomości: typowe schematy polskich oszustw.

Tekst jest sprowadzany do małych liter i pozbawiany polskich znaków,
więc "dopłata", "doplata" i "DOPŁATA" pasują do tej samej reguły.

Jak dodać regułę: dopisz Rule(...) do RULES i przykład do tests/examples.py.
Potem uruchom `python -m tests.evaluate` i sprawdź, czy nie rośnie liczba fałszywych alarmów.
"""

import re
import unicodedata
from dataclasses import dataclass

from ..models import Signal


def normalize_text(text: str) -> str:
    """Małe litery, bez polskich znaków ("ł" -> "l"), pojedyncze spacje."""
    text = text.lower().replace("ł", "l")
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", text)


@dataclass(frozen=True)
class Rule:
    code: str
    points: int
    reason: str
    pattern: re.Pattern[str]


def _r(code: str, points: int, reason: str, pattern: str) -> Rule:
    return Rule(code, points, reason, re.compile(pattern))


AMOUNT = r"\d{1,3}(?:[.,]\d{1,2})?\s?(?:zl|pln)"

RULES: list[Rule] = [
    _r("small_payment", 30,
       "Prośba o małą dopłatę to najczęstsza sztuczka: chodzi o dane Twojej karty, nie o kwotę.",
       rf"(doplat|oplat\w* (celn|dodatk)|uisc|uregul|naleznosc|brakuj\w* (kwot|oplat)).{{0,80}}{AMOUNT}"
       rf"|{AMOUNT}.{{0,60}}(doplat|oplat|uisc|uregul)"),
    _r("parcel_problem", 15,
       "Wiadomość o problemie z paczką to częsty pretekst oszustów.",
       r"(paczk|przesylk|kurier|inpost|dpd|dhl|poczta polska)\w*.{0,80}"
       r"(wstrzyman|zatrzyman|nie moze zostac|niedostarcz|adres\w* (nieprawidl|niepeln)|potwierdz|aktualizuj|oczekuj\w* na (oplat|doplat))"),
    _r("blik_request", 60,
       "Nigdy nie podawaj nikomu kodu BLIK. Oszuści podszywają się pod znajomych i proszą o kod.",
       r"(kod\w* blik|blik\w*.{0,40}(podaj|wyslij|przeslij|daj|potrzebuj|pozycz)"
       r"|(podaj|wyslij|przeslij|potrzebuj\w*).{0,40}blik)"),
    _r("family_new_number", 40,
       "Wiadomość od „bliskiej osoby z nowego numeru” to znane oszustwo. Zadzwoń na jej stary numer.",
       r"(mamo|tato|mama|tata|babciu|dziadku|synu|corko|kochanie).{0,120}"
       r"(nowy numer|zmienil\w* numer|zepsul\w* (mi )?(sie )?telefon|stary telefon|to moj nowy)"
       r"|(to moj nowy numer|pisze z nowego numeru|pisze z innego numeru)"),
    _r("money_request", 25,
       "Prośba o szybki przelew lub pożyczkę. Upewnij się telefonicznie, kto naprawdę pisze.",
       r"(pozycz\w*|przelej\w*|przelew\w*|wyslij\w*|potrzebuj\w*).{0,40}(\d+\s?(zl|pln)|pieniadz|kas[ey])"),
    _r("urgency", 15,
       "Wiadomość wywiera presję czasu. Prawdziwe firmy i urzędy nie wymagają reakcji w kilka godzin.",
       r"(natychmiast|pilne|pilnie|w ciagu (24|48|12) ?(h|godz)|do konca dnia|dzisiaj do"
       r"|ostatnie (ostrzezenie|wezwanie|przypomnienie)|ostateczne wezwanie|niezwlocznie)"),
    _r("account_blocked", 25,
       "Groźba blokady konta i prośba o „potwierdzenie danych” to typowe wyłudzenie.",
       # Bez "wygasa": "karta wygasa 12/2026" to zwykła informacja banku, a nie groźba
       r"(konto|rachunek|karta|dostep|aplikacj\w*|profil)\w*.{0,60}"
       r"(zablokowan|zawieszon|wylaczon|ograniczon)"
       r"|(potwierdz|zaktualizuj|zweryfikuj|uzupelnij)\w* (swoje )?(dane|tozsamos|konto)"),
    _r("prize_or_refund", 30,
       "Nieoczekiwana wygrana, zwrot lub „wypłata” to przynęta, żeby wyłudzić dane.",
       r"(wygral\w*|wygrana|nagrod\w*|nalezy ci sie"
       r"|dostepne wyplaty|odbierz (swoj|nagrod|zwrot|bon)|odebra\w* (pieniadz|srodk|wyplat|platnos)|otrzymac (srodki|pieniadze|platnosc)|darmow\w* (bon|kupon|voucher)|bon o wartosci"
       # Sam "zwrot podatku/środków" to zwykła informacja (sklep, urząd).
       # Podejrzany jest zwrot, po który trzeba coś zrobić: wybrać bank, podać dane, kliknąć.
       r"|(otrzymac|odebrac) zwrot\w*.{0,40}(wybierz|podaj|potwierdz|kliknij|wejdz)"
       # "odbierz 250 zl", "odbierz 10 euro na start": darmowe pieniądze za nic
       r"|odbierz \d+(?:[.,]\d{1,2})? ?(zl|pln|euro|eur)\b)"),
    _r("install_app", 30,
       "Prośba o zainstalowanie aplikacji z linku. Aplikacje instaluj tylko ze Sklepu Play lub App Store.",
       r"(zainstaluj|pobierz|instalacj\w*).{0,50}(aplikacj|apk|program|nowa wersj|anydesk|teamviewer|quicksupport)"),
    _r("utility_cutoff", 35,
       "Groźba odcięcia prądu lub gazu z linkiem do zapłaty to znane oszustwo.",
       r"(odlaczen\w*|odciec\w*|wstrzyman\w*|zaleglos\w*).{0,60}(prad|energi|gaz|dostaw)"),
    _r("investment", 45,
       "Obietnica łatwego zysku z inwestycji to bardzo częste oszustwo.",
       r"(inwest\w*|zarabiaj\w*|zarobek|zysk\w*|kryptowalut\w*|bitcoin).{0,80}"
       r"(dziennie|tygodniowo|gwarant|bez ryzyka|\d+ ?%|pasywn)"),
    _r("fine_or_debt", 25,
       "Mandat, dług albo opłata wysłana SMS-em z linkiem to oszustwo. Urzędy tak nie ściągają należności.",
       r"(mandat|grzywn|zadluzen|egzekuc|komornik|oplat\w* drogow|e-?toll|nieoplacon)"
       r"\w*.{0,80}(zaplac|oplac|uregul|link|kliknij|stron)"),
    _r("personal_data_request", 25,
       "Prośba o PESEL, dane karty albo hasło. Nikt uczciwy nie prosi o to w wiadomości.",
       r"(podaj|wpisz|przeslij|potwierdz|uzupelnij).{0,40}"
       r"(pesel|numer\w* kart|cvv|cvc|dane kart|dane logowania|hasl|login|kod sms|numer dowodu)"),
    _r("click_link", 10,
       "Wiadomość każe kliknąć w link. Lepiej wejść na stronę samodzielnie, wpisując adres.",
       r"(kliknij|wejdz|odwiedz|przejdz)\w*.{0,30}(link|stron|adres|ponizej|tutaj|w link)"),
    _r("remote_access_call", 60,
       "„Konsultant banku” każący zainstalować program albo przelać pieniądze na „bezpieczne konto” to oszustwo.",
       r"(bezpieczne konto|konto techniczne|pracownik (banku|policji|cert)|konsultant\w* banku)"),
]


def check_text(text: str) -> list[Signal]:
    normalized = normalize_text(text)
    return [
        Signal(code=rule.code, points=rule.points, reason=rule.reason, source="text")
        for rule in RULES
        if rule.pattern.search(normalized)
    ]
