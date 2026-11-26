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
    ("Bank Polnocny: Twoja karta zostala zablokowana. Potwierdz dane karty: bankpolnocny-karta.top", "scam"),
    ("Skarbowka: aby otrzymac zwrot nadplaty 318 zl, wybierz swoj bank i zaloguj sie: zwrot-nadplaty.site", "scam"),
    ("Program Bon Rodzinny: wypelnij formularz i odbierz 300 zl na konto: bon-rodzinny.online", "scam"),
    ("Tu konsultantka z banku. Prosze zainstalowac TeamViewer, pomoge zablokowac podejrzany przelew.", "scam"),
    ("Telefon mi sie zepsul, pisze z telefonu kolegi. Mamo, przelej mi 600 zl na rachunek, to pilne", "scam"),
    ("Siema, podeslij mi szybko kod na 200 zl, nie dziala mi karta w sklepie. Zaraz oddam", "scam"),
    ("Straz Miejska: wezwanie do zaplaty za nieprawidlowe parkowanie. Oplac w ciagu 24h: strazmiejska-oplaty.top", "scam"),
    ("Parking Miejski: nieoplacony postoj. Zaplac teraz, aby uniknac dodatkowych oplat: parking-miasto.help", "scam"),
    ("Nowy system oplat w strefie: zeskanuj kod QR na parkomacie i zaplac karta na stronie.", "suspicious"),
    ("Bank Polnocny: wykryto podejrzana transakcje 1499 zl. Jesli to nie Ty, anuluj ja tutaj: bankpolnocny-anuluj.top", "scam"),
    # Ostrzezenie w pierwszym zdaniu nie "wylacza" prosby o bezpieczne konto w drugim
    ("Pracownik banku: nigdy nie podawaj nikomu hasla. Teraz prosze przelac srodki na bezpieczne konto.", "scam"),
    ("Dasz mi BLIKa na 200 zl? Karta mi nie dziala, oddam jutro", "scam"),
    ("Bank Polnocny: wykryto podejrzana transakcje 2300 zl. Zweryfikuj konto: bankpolnocny-weryfikacja.top", "scam"),
    ("Ankieta klienta: odpowiedz na 3 pytania i odbierz 200 zl na swoje konto: ankieta-nagrody.site", "scam"),
    ("Kontrola biletow: brak waznego biletu. Oplac wezwanie 120 zl w ciagu 24h: kontrola-biletow.site", "scam"),
    ("Mamo, to moj nowy numer. Napisz do mnie na WhatsApp, wszystko wyjasnie", "suspicious"),
    ("Wodociagi: nieoplacona faktura 76 zl. Zaplac teraz, aby uniknac odciecia wody: wodociagi-platnosc.top", "scam"),
    # Podrobki domen GITD, Orange i T-Mobile (prawdziwe: gitd.gov.pl, orange.pl, t-mobile.pl)
    ("GITD: zarejestrowano przekroczenie predkosci. Sprawdz mandat i zaplac online: gitd-mandat.online", "scam"),
    ("Orange: Twoja karta SIM zostanie zablokowana. Zaktualizuj dane: orange-karta-sim.com", "scam"),
    ("T-Mobile: nie udalo sie pobrac platnosci za abonament. Zaplac 4,99 zl: t-mobile-oplata.top", "scam"),
    # Ostrzezenie ze zdaniem "ktore..." w pierwszym zdaniu nie wylacza prosby o AnyDesk w drugim
    ("Nigdy nie podawaj hasla osobom, ktore dzwonia. Tu konsultant banku: prosze zainstalowac AnyDesk.", "scam"),
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
    "Bank Polnocny: Twoja karta debetowa wygasa 05/2027. Nowa karta zostanie wyslana poczta.",
    "Sklep Zielony Koszyk: zwrot srodkow 59,90 zl za anulowane zamowienie zostal zlecony na Twoja karte.",
    "Odbierz paczke z automatu do 12.12. Za pobraniem: 45 zl, platne karta przy automacie.",
    "Pan z serwisu zainstalowal juz pralke, dziala bez zarzutu. Dzwonil tez pracownik spoldzielni.",
    "Mam nowy numer do pracy, zapisz go sobie. Do zobaczenia w poniedzialek, Ola",
    "Oddalam Ci za bilety BLIKiem na telefon, sprawdz czy doszlo 80 zl",
    "Parkowanie oplacone do 15:30 w strefie A. Przedluz postoj w aplikacji, jesli potrzebujesz.",
    "Wodociagi: faktura 89 zl z terminem 10.12 jest w eBOK. Oplac w terminie, aby uniknac odsetek.",
    "Zeskanuj kod QR na ulotce, aby zobaczyc menu naszej restauracji. Smacznego!",
    "Bank Polnocny: logowanie z nowego urzadzenia 3.12 o 8:15. Jesli to nie Ty, zadzwon na numer z odwrotu karty.",
    # Prawdziwe ostrzezenie banku: "nigdy nie poprosi", "nie przelewaj"
    "Bank Polnocny: pracownik banku nigdy nie poprosi Cie o kod BLIK. Nie przelewaj pieniedzy na bezpieczne konto.",
    # Sklep DAJE kod rabatowy ("dajemy"), nikt nie prosi o kod BLIK
    # Ostrzezenie rozciaga sie na zdanie "ktora dzwoni jako konsultant banku" (po przecinku)
    "Bank Polnocny: nie instaluj AnyDesk na prosbe osoby, ktora dzwoni jako konsultant banku.",
    "Dajemy Ci kod na 30 zl rabatu na pierwsze zamowienie w sklepie Zielony Koszyk.",
    # Prawdziwy bank kieruje do aplikacji i na numer z karty, a nie w link
    "Bank Polnocny: zablokowalismy podejrzana transakcje 2300 zl. Sprawdz ja w aplikacji albo zadzwon na numer z karty.",
    # Rabat sklepu "na zakupy", a nie pieniadze "na konto"
    "Zielony Koszyk: odbierz 15 zl na pierwsze zakupy w naszej aplikacji.",
    "Brak biletu w aplikacji? Sprawdz strone przewoznika albo kup bilet w kasie.",
    # Drugi numer "do pracy / sluzbowy", bez historii o zepsutym telefonie i bez prosby o pieniadze
    "Tato, to moj nowy numer sluzbowy, zapisz go. Prywatny zostaje bez zmian",
    # Przypomnienie o zaleglej fakturze, ale z odeslaniem do eBOK / aplikacji, a nie w link
    "Wodociagi Miejskie: faktura 76 zl jest nieoplacona. Zaplac w eBOK lub w aplikacji, aby uniknac odsetek.",
    "GITD: informacje o punktach karnych i mandatach znajdziesz tylko na https://www.gitd.gov.pl",
    "Orange: faktura za grudzien 49,99 zl jest dostepna na https://www.orange.pl/moj-orange",
    "T-Mobile: Twoj pakiet internetu odnowi sie 01.12. Szczegoly: https://www.t-mobile.pl",
]
