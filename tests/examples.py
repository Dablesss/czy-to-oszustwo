"""Zestaw przykładów do mierzenia trafności (tests/evaluate.py) i testów (test_api.py).

Oszustwa są wzorowane na typowych kampaniach opisywanych przez CERT Polska (telegraf.cert.pl).
Domeny w przykładach są zmyślone.

TYDZIEŃ 2: rozbuduj do ~50 + 50 prawdziwych przykładów. Zwykłe wiadomości są równie ważne
jak oszustwa, bo pokazują fałszywe alarmy.
"""

# (tekst, oczekiwany minimalny werdykt) — "scam" albo "suspicious"
SCAMS: list[tuple[str, str]] = [
    ("InPost: Twoja paczka zostala wstrzymana. Dokonaj doplaty 1,99 zl: https://inpost-doplata.top/pl", "scam"),
    ("Poczta Polska: przesylka oczekuje na oplate celna 2,49 PLN. Ureguluj naleznosc: pocztapolska-cło.xyz/a1", "scam"),
    ("PGE: Z powodu zaleglosci dzis o 21:00 nastapi odlaczenie pradu. Ureguluj 4,26 zl: pge-oplata.online", "scam"),
    ("Mamo to moj nowy numer, stary telefon sie zepsul. Pilnie potrzebuje 800 zl na rachunek, oddam jutro", "scam"),
    ("Hej, mozesz mi podeslac kod BLIK? Musze szybko zaplacic, a nie dziala mi aplikacja. Oddam wieczorem", "scam"),
    ("mObywatel: Sprawdz dostepne wyplaty po numerze PESEL: https://mobywatel-wyplaty.click", "scam"),
    ("Twoje konto PKO zostalo zablokowane. Potwierdz dane logowania: http://pkobp-weryfikacja.com/login", "scam"),
    ("Nieoplacony przejazd e-TOLL. Zaplac 15,40 zl w ciagu 24h aby uniknac kary: etoll-platnosc.site", "scam"),
    ("Gratulacje! Wygrales bon o wartosci 500 zl do Biedronki. Odbierz nagrode: bit.ly/3xYz", "scam"),
    ("Allegro: Twoja oferta zostala oplacona. Aby otrzymac srodki potwierdz dane karty: allegro-lokalnie.shop", "scam"),
    ("Zainstaluj nowa wersje aplikacji banku, stara wygasa jutro: https://mbank-update.app", "scam"),
    ("Zarabiaj 1500 zl dziennie na inwestycjach w kryptowaluty bez ryzyka! Zapisz sie: crypto-zysk.vip", "scam"),
    ("Vinted: Kupujacy oplacil przedmiot. Kliknij link, aby odebrac pieniadze: vinted-wyplata.com", "scam"),
    ("Dzien dobry, tu pracownik banku. Panstwa srodki sa zagrozone, prosze przelac je na bezpieczne konto.", "scam"),
    ("DPD: nie mozemy doreczyc paczki, adres nieprawidlowy. Zaktualizuj dane: dpd-paczka.top", "scam"),
    ("Urzad Skarbowy: nalezy ci sie zwrot podatku 412 zl. Wypelnij formularz: podatki-zwrot.net", "scam"),
    # Podróbka domeny operatora sieci (prawdziwa to energa-operator.pl)
    ("Energa Operator: zaleglosc 3,80 zl. Jutro odlaczenie pradu. Oplac: energa-operator-platnosc.top", "scam"),
]

LEGIT: list[str] = [
    "InPost: Twoja paczka czeka w Paczkomacie WAW123. Kod odbioru: 123456. Odbierz do 27.11.",
    "Czesc, bede za 10 minut, kupic cos jeszcze do sklepu?",
    "Przypominamy o wizycie u stomatologa jutro o 14:30. Gabinet Usmiech.",
    "Twoja przesylka DPD zostanie dostarczona dzisiaj miedzy 10:00 a 13:00. Sledz: https://www.dpd.com.pl",
    "Mamo, wroce dzis pozniej, mam dodatkowe zajecia na uczelni.",
    "Zamowienie nr 4521 zostalo wyslane. Szczegoly na allegro.pl w zakladce Moje zakupy.",
    "Kod weryfikacyjny do logowania: 482913. Nie przekazuj go nikomu.",
    "Hej, wyslesz mi zdjecia z wczorajszej imprezy?",
    "Spotkanie projektu przeniesione na czwartek 18:00, sala 2.14.",
    "Twoja faktura za listopad jest dostepna w aplikacji. Termin platnosci: 10.12.",
    "Biblioteka: termin zwrotu ksiazki mija za 3 dni. Mozesz ja przedluzyc w katalogu online.",
    "Witaj.Dziekujemy za zakupy w naszym sklepie, zapraszamy ponownie!",
    "Energa Operator: 3.12 w godz. 9-13 planowana przerwa w dostawie pradu przy ul. Polnej. Wiecej: energa-operator.pl",
]
