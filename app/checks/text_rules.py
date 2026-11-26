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

# Do reguły family_new_number: kto pisze i co się "stało" z telefonem.
FAMILY = r"(mamo|tato|mama|tata|babciu|dziadku|synu|corko|kochanie)"
NEW_NUMBER = (r"(nowy numer|zmienil\w* numer|zepsul\w* (mi )?(sie )?telefon|telefon (mi )?(sie )?zepsul"
              r"|stary telefon|to moj nowy)")

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
       # "wygenerujesz mi BLIKa", "podeslesz BLIKa": czasownik w dowolnej formie przed "blik"
       r"|(podaj|podesl|wyslij|przeslij|wygeneruj|potrzebuj)\w*.{0,40}blik"
       # Prośba o "kod na 300 zl" bez słowa BLIK: kod z kwotą to właśnie kod BLIK.
       # (\w+ ){0,2} pozwala na 0-2 słowa pomiędzy: "podeslij mi szybko kod na 200 zl"
       rf"|(podaj|podesl|wyslij|przeslij|wygeneruj|daj)\w* (\w+ ){{0,2}}kod\w* na {AMOUNT})"),
    _r("family_new_number", 40,
       "Wiadomość od „bliskiej osoby z nowego numeru” to znane oszustwo. Zadzwoń na jej stary numer.",
       rf"{FAMILY}.{{0,120}}{NEW_NUMBER}"
       # Odwrotna kolejność: "mam nowy numer. Tato, ..." (tu tylko zwroty do kogoś: mamo, tato)
       rf"|{NEW_NUMBER}.{{0,80}}(mamo|tato|babciu|dziadku|synu|corko)"
       r"|(to moj nowy numer|pisze z nowego numeru|pisze z innego numeru)"),
    _r("money_request", 25,
       "Prośba o szybki przelew lub pożyczkę. Upewnij się telefonicznie, kto naprawdę pisze.",
       r"(pozycz\w*|przelej\w*|przelew\w*|wyslij\w*|potrzebuj\w*).{0,40}(\d+\s?(zl|pln)|pieniadz|kas[ey])"),
    _r("urgency", 15,
       "Wiadomość wywiera presję czasu. Prawdziwe firmy i urzędy nie wymagają reakcji w kilka godzin.",
       r"(natychmiast|pilne|pilnie|w ciagu (24|48|12) ?(h|godz)|do konca dnia|dzisiaj do"
       r"|ostatnie (ostrzezenie|wezwanie|przypomnienie)|ostateczne wezwanie|niezwlocznie"
       # "Zaplac teraz", "aby uniknac kary": popędzanie groźbą dodatkowych kosztów
       r"|(zaplac|oplac|ureguluj) (teraz|od razu)|uniknac (kary|dodatkow|odsetek|blokady)"
       r"|dodatkowe (koszty|oplaty))"),
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
       # "zainstal\w*" łapie każdą formę: zainstaluj, zainstalowac, zainstaluje
       r"(zainstal\w*|pobierz|instalacj\w*).{0,50}(aplikacj|apk|program|nowa wersj|anydesk|teamviewer|quicksupport)"),
    _r("utility_cutoff", 35,
       "Groźba odcięcia prądu lub gazu z linkiem do zapłaty to znane oszustwo.",
       r"(odlaczen\w*|odciec\w*|wstrzyman\w*|zaleglos\w*).{0,60}(prad|energi|gaz|dostaw)"),
    _r("investment", 45,
       "Obietnica łatwego zysku z inwestycji to bardzo częste oszustwo.",
       r"(inwest\w*|zarabiaj\w*|zarobek|zysk\w*|kryptowalut\w*|bitcoin).{0,80}"
       r"(dziennie|tygodniowo|gwarant|bez ryzyka|\d+ ?%|pasywn)"),
    _r("fine_or_debt", 25,
       "Mandat, dług albo opłata wysłana SMS-em z linkiem to oszustwo. Urzędy tak nie ściągają należności.",
       r"(mandat|grzywn|zadluzen|egzekuc|komornik|oplat\w* drogow|e-?toll|nieoplacon|niezaplacon"
       # parking i komunikacja miejska: "brak biletu", "wezwanie do zaplaty", "nieprawidlowe parkowanie"
       r"|brak\w* (waznego )?biletu|wezwani\w* do zaplaty|nieprawidlow\w* parkowan)"
       r"\w*.{0,80}(zaplac|oplac|uregul|link|kliknij|stron|skan)"),
    _r("qr_payment", 25,
       "Płatność przez kod QR z wiadomości albo naklejki może prowadzić na fałszywą stronę. "
       "Płać w oficjalnej aplikacji albo w parkomacie.",
       # kod QR + zapłata w dowolnej kolejności: "zeskanuj kod QR i oplac", "oplac, skanujac kod QR"
       r"(zeskanuj|skanuj|zeskanowa)\w*.{0,30}kod\w* qr.{0,80}(zaplac|oplac|platnos)"
       r"|(zaplac|oplac)\w*.{0,60}(zeskanuj|skanuj|zeskanowa)\w*.{0,20}kod\w* qr"),
    _r("security_alert", 30,
       "„Alarm bezpieczeństwa” z poleceniem kliknięcia to częsty pretekst. "
       "Sprawdź konto sam w oficjalnej aplikacji, a nie przez link czy numer z wiadomości.",
       # Zdarzenie: logowanie z nowego miejsca albo podejrzany przelew ...
       r"((zalogowa|logowani)\w*.{0,60}(nowego urzadzenia|nowym urzadzeniu|nieznanego urzadzenia"
       r"|innej lokalizacji|innego kraju)"
       r"|prob\w* (przelania|przelewu|wyplaty)|podejrzan\w* (transakcj|przelew|logowan)|nieautoryzowan\w*)"
       # ... a potem polecenie: kliknij/sprawdź/anuluj albo "zadzwoń pod numer z tej wiadomości".
       # Prawdziwy bank każe dzwonić na numer z karty albo sprawdzić w aplikacji.
       r".{0,100}(sprawdz|kliknij|anuluj|zweryfikuj|potwierdz|zabezpiecz"
       r"|zadzwon\w*.{0,40}numer\w* (z tej wiadomosci|z sms|ponizej))"),
    _r("personal_data_request", 25,
       "Prośba o PESEL, dane karty albo hasło. Nikt uczciwy nie prosi o to w wiadomości.",
       r"(podaj|wpisz|przeslij|potwierdz|uzupelnij).{0,40}"
       r"(pesel|numer\w* kart|cvv|cvc|dane kart|dane logowania|hasl|login|kod sms|numer dowodu)"),
    _r("click_link", 10,
       "Wiadomość każe kliknąć w link. Lepiej wejść na stronę samodzielnie, wpisując adres.",
       r"(kliknij|wejdz|odwiedz|przejdz)\w*.{0,30}(link|stron|adres|ponizej|tutaj|w link)"),
    _r("remote_access_call", 60,
       "„Konsultant banku” każący zainstalować program albo przelać pieniądze na „bezpieczne konto” to oszustwo.",
       # \w* po słowie łapie odmianę: "pracownika banku", "konsultantem z banku", "na konto techniczne"
       # (bez "bezpieczenstwo konta" i "kontakt techniczny", bo to zwykłe zwroty)
       r"(bezpieczn(e|ego|ym|y) (kont|rachun)|kont(o|a|em|u) techniczn|pracownik\w* (banku|policji|cert)"
       r"|konsultant\w* (z )?banku"
       # Programy do zdalnego pulpitu: w SMS-ie prawie zawsze oznaczają oszusta "z banku"
       r"|anydesk|teamviewer|quicksupport|rustdesk)"),
]


# Ostrzeżenia zamiast próśb: "pracownik banku NIGDY NIE poprosi o kod BLIK",
# "nigdy nie przelewaj na bezpieczne konto", "nie instaluj AnyDesk".
# Same słowa "nie"/"uwaga" nie wystarczą ("podeślij BLIKa, nie mam kasy" to dalej prośba),
# dlatego "nie" liczy się tylko z czasownikiem, który ostrzega.
WARNING_WORDS = (r"(\bnigdy\b|\bnie (poprosi|prosi|prosimy|podawaj|przekazuj|udostepniaj"
                 r"|przelewaj|wysylaj|instaluj|klikaj)"
                 # "uwaga na falszywe SMS-y z prosba o doplate": opis cudzego oszustwa
                 r"|falszyw\w* (sms|wiadomos|mail))")
# Ostrzeżenie stoi tuż PRZED dopasowaniem (do 40 znaków): "nigdy nie podawaj nikomu kodu BLIK"
WARNING_BEFORE = re.compile(WARNING_WORDS)
# ... albo zaraz ZA nim: "pracownik banku nigdy nie poprosi", "kodu BLIK nie podawaj"
WARNING_AFTER = re.compile(r"[\s,]*" + WARNING_WORDS)


def _is_warning(normalized: str, match: re.Match[str]) -> bool:
    """Czy to dopasowanie jest częścią ostrzeżenia ("nigdy nie..."), a nie prośbą oszusta."""
    before = normalized[max(0, match.start() - 40):match.start()]
    after = normalized[match.end():]
    return bool(WARNING_BEFORE.search(before) or WARNING_AFTER.match(after))


def _rule_matches(rule: Rule, normalized: str) -> bool:
    """Reguła pasuje, jeśli choć jedno jej dopasowanie NIE jest ostrzeżeniem."""
    return any(not _is_warning(normalized, m) for m in rule.pattern.finditer(normalized))


def check_text(text: str) -> list[Signal]:
    normalized = normalize_text(text)
    return [
        Signal(code=rule.code, points=rule.points, reason=rule.reason, source="text")
        for rule in RULES
        if _rule_matches(rule, normalized)
    ]
