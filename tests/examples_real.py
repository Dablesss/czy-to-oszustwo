"""Zestaw "realnych" przykładów do mierzenia trafności (tylko tests/evaluate.py).

Skąd dane
---------
Oszustwa (REAL_SCAMS) są wzorowane na prawdziwych kampaniach z lat 2025–2026, opisanych przez:
- CERT Polska / NASK: publiczny wykaz wzorców SMS z systemu Telegraf
  (https://telegraf.cert.pl/api/v1/public/patterns), komunikaty i podsumowania miesięczne,
- CERT Orange Polska, CSIRT KNF, FinCERT.pl, Policję (BZPE KGP),
- banki (PKO BP, mBank, ING, Santander) i serwisy gov.pl,
- artykuły prasowe, które cytują te ostrzeżenia (link przy każdym przykładzie).

Zwykłe wiadomości (REAL_LEGIT) to typowe, prawdziwe w stylu powiadomienia: z banku bez linku,
kody 2FA, awizo, przypomnienia o wizycie, SMS-y od rodziny, faktury. Część ma linki
do PRAWDZIWYCH oficjalnych domen marek – to test, czy nie robimy fałszywych alarmów.

Jak zanonimizowano
------------------
- Treści są PRZEFORMUŁOWANE, a nie skopiowane słowo w słowo.
- Domeny oszustów są ZMYŚLONE (w tym samym stylu, np. "inpost-clo24.top").
  Prawdziwe złośliwe adresy z ostrzeżeń celowo pominęliśmy.
- Brak prawdziwych numerów telefonów, PESEL-i, nazwisk i numerów kont.
  Kwoty, numery paczek i kody są wymyślone.

Ważne
-----
Ten zestaw NIE jest używany przez pytest. Służy tylko do pomiaru: `python -m tests.evaluate`.
Część przykładów reguły dziś przepuszczają i tak ma zostać – to lista rzeczy do poprawy,
a nie test, który musi przechodzić.

Oczekiwany werdykt:
- "scam" – człowiek, który zna te sztuczki, od razu widzi oszustwo,
- "suspicious" – sam tekst jest dwuznaczny (bez kontekstu mógłby być prawdziwy).
"""

# (tekst, oczekiwany minimalny werdykt) — "scam" albo "suspicious"
REAL_SCAMS: list[tuple[str, str]] = [
    # --- Paczki ---
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorzec "inpost ... podlega oplatom celnym", 2026-10)
    ("InPost: Twoja przesylka 48213 podlega oplatom celnym 3,18 zl, ktore nie zostaly uiszczone. "
     "Oplac do jutra: inpost-clo24.top/p", "scam"),
    # źródło: https://superbiz.se.pl/wiadomosci/poczta-polska-ostrzega-przed-nowa-kampania-oszustow-zadajacych-rzekomej-oplaty-celnej-za-przesylke-aa-m1iD-EFTp-Yvrn.html
    ("Poczta Polska: przesylka nr PL7730 wymaga oplaty celnej 4,99 zl. Bez wplaty wroci do nadawcy. "
     "pocztapolska-odprawa.icu", "scam"),
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorzec "paczka za dlugo w paczkomacie ... zwrot", 2026-10)
    ("Paczka czekala za dlugo w Paczkomacie i uruchomilismy zwrot do nadawcy. "
     "Mozesz go anulowac tutaj: https://paczkomat-zwrot.click/x7", "scam"),
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorzec "w adresie brakuje numeru domu", 2026-10)
    ("Dostawa Twojej paczki jest wstrzymana: w adresie brakuje numeru domu. "
     "Uzupelnij dane pod linkiem: https://dostawa-adres.cfd/pl", "scam"),
    # źródło: https://tvn24.pl/biznes/tech/oszustwo-w-sieci-na-pocztex-ostrzezenie-nask-st8557707
    ("Pocztex: nie mozemy doreczyc przesylki z powodu niepelnego adresu. "
     "Popraw dane i oplac ponowna dostawe 1,50 zl: pocztex-dostawa.sbs", "scam"),
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorzec "dpd ... nie udalo sie dostarczyc", 2026-09)
    ("DPD: nie udalo sie dostarczyc Twojej przesylki. Sprawdz szczegoly i wybierz nowy termin: "
     "https://dpd-termin.live/s", "scam"),
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorzec "dhl ostatnie przypomnienie ... zablokowana", 2026-09)
    ("DHL: ostatnie przypomnienie. Twoja przesylka zostala zablokowana. Odblokuj ja: dhl-pl-odbior.top", "scam"),

    # --- Prąd / gaz ---
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorce "planowane wylaczenie pradu ... oplata", 2026-03)
    ("PGE: planowane wylaczenie pradu pod Twoim adresem dzis o 20:00 z powodu nieuregulowanej faktury. "
     "Oplac 6,73 zl: pge-rozliczenia.online", "scam"),
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorzec "PGE ... nadplata/zwrot", 2026-03)
    ("PGE Obrot: wykryto nadplate za energie. Zwrot 187,40 zl czeka na odbior, wystarczy podac dane karty: "
     "pge-nadplata.site", "scam"),
    # źródło: https://www.telepolis.pl/wiadomosci/bezpieczenstwo/cert-polska-pge-falszywy-sms-o-zaleglosci-oszustwo
    ("Zaleglosc za gaz 12,30 zl. Jutro nastapi wstrzymanie dostaw gazu do Twojego mieszkania. "
     "Zaplac teraz: gaz-rozliczenie.top", "scam"),

    # --- BLIK i "mamo, nowy numer" ---
    # źródło: https://www.mbank.pl/komunikaty/klienci-indywidualni/10349-uwazaj-na-oszustow-ktorzy-podszywaja-sie-pod-rodzine-lub-znajomych-na-portalach-spolecznosciowych/
    ("Hej, masz chwile? Musze pilnie zaplacic za zamowienie, a mam limit na koncie. "
     "Wygenerujesz mi BLIKa na 500? Oddam jutro rano", "scam"),
    # źródło: https://www.erste.pl/erste-education/odpal-cyberswiadomosc/oszustwo-na-blik
    ("Czesc, podeslesz mi kod na 300 zl z aplikacji banku? Telefon mi pada, a musze oplacic kuriera", "scam"),
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorce "mamo ... zepsulem telefon ... napisz na whatsap", 2026-10)
    ("Mamo, zepsulem telefon. Usun stary numer i napisz do mnie na WhatsApp na ten", "suspicious"),
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorzec "mam nowy numer tato napisz do mnie na wh", 2026-09)
    ("Czesc tato, mam nowy numer. Napisz do mnie na WhatsAppie, tam wszystko wyjasnie", "suspicious"),
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorzec "przewrocilem sie i telefon mi sie zepsul", 2026-10)
    ("Przewrocilem sie i telefon mi sie zepsul, mam nowy numer. Tato, zrobisz za mnie przelew 1200 zl? "
     "To pilne, oddam w piatek", "scam"),

    # --- Mandaty, e-TOLL, parkowanie ---
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorce "e-TOLL nieuregulowany przejazd", 2026-02/03)
    ("e-TOLL: nieuregulowany przejazd odcinkiem platnym. Aby uniknac kary administracyjnej 500 zl, "
     "oplac 9,80 zl: etoll-przejazd.top", "scam"),
    # źródło: https://android.com.pl/tech/1096925-gitd-uodo-falszywy-mandat-oszusci/
    ("Zarejestrowano przekroczenie predkosci Twojego pojazdu. Sprawdz status mandatu i zaplac online: "
     "gitd-mandaty.online", "scam"),
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorzec "mobywatel ... czas do dnia ... na oplacenie mandatu", 2026-10)
    ("mObywatel: masz czas do 28.11 na oplacenie mandatu, zanim kwota zostanie podwyzszona. "
     "Szczegoly: mobywatel-sprawy.click", "scam"),
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorzec "oplata za parking pozostaje niezaplacona", 2026-10)
    ("Twoja oplata za parking pozostaje niezaplacona. Spozniona platnosc oznacza dodatkowe koszty. "
     "Zaplac teraz: strefa-parkuj.help", "scam"),
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorzec "kontrola w tramwaju ... brak biletu", 2026-10)
    ("Kontrola w tramwaju: brak biletu. Wezwanie do zaplaty w toku. Zaplac teraz 9,60 zl, "
     "aby uniknac kary 280 zl: mpk-wezwanie.site", "scam"),

    # --- Urzędy: mObywatel, podatki, Profil Zaufany ---
    # źródło: https://android.com.pl/tech/1082502-mobywatel-stracil-waznosc-oszustwo/
    ("Gov PL: waznosc Twoich danych w mObywatelu wygasa. Zaktualizuj swoje dane: "
     "https://login-gov-pl.dane-odnow.com", "scam"),
    # źródło: https://www.telepolis.pl/tech/bezpieczenstwo/zwrot-podatku-oszustwo-cert
    ("e-Urzad Skarbowy: stwierdzono nadplate podatku 642,00 zl. Aby otrzymac zwrot, wybierz swoj bank "
     "i potwierdz dane: e-urzad-zwrot.info", "scam"),
    # źródło: https://www.gsmmaniak.pl/1311313/oszustwo-wiadomosci-sms-ministerstwo-finansow/amp/
    ("Ministerstwo Finansow: wypelnij krotka ankiete i odbierz 250 zl na swoje konto: mf-ankieta.store", "scam"),
    # źródło: https://android.com.pl/tech/979336-scam-nask-ostrzezenie-oszustwo-kredyt/
    ("Gov.pl: wykryto logowanie do Profilu Zaufanego z nowego urzadzenia i zlozono wniosek kredytowy. "
     "Jesli to nie Ty, zadzwon do wsparcia technicznego pod numer z tej wiadomosci.", "scam"),

    # --- Banki, konsultanci, "bezpieczne konto", zdalny pulpit ---
    # źródło: https://www.benchmark.pl/ostrzezenie-pko-bp-uwazaj-na-sms-y-o-nowej-aplikacji-7330400727210208a
    ("PKO BP: Twoja aplikacja mobilna traci waznosc 30.11. Zainstaluj nowa wersje: pkobp-aplikacja.app", "scam"),
    # źródło: https://www.benchmark.pl/ostrzezenie-pko-bp-uwazaj-na-sms-y-o-nowej-aplikacji-7330400727210208a
    ("Zmienilismy strone logowania do bankowosci. Kliknij link i potwierdz dane: ipko-logowanie.com", "scam"),
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorzec "Santander ... karta zablokowana ... aktualizacja", 2026-04)
    ("Santander: Twoja karta zostala tymczasowo zablokowana przez system bezpieczenstwa. "
     "Aby ja odblokowac, przeprowadz aktualizacje: santander-karta.eu", "scam"),
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorzec "weryfikacja pracownika banku ... nie podawaj nikomu", 2026-06)
    ("Weryfikacja pracownika banku: Twoj kod to 4821. Nie podawaj go nikomu. "
     "Popros konsultanta, z ktorym rozmawiasz, aby sam go odczytal.", "suspicious"),
    # źródło: https://www.bankier.pl/wiadomosc/Policjant-dzwoni-z-kamera-Mundur-ma-uwiarygodnic-oszustwo-Nowy-scam-9173798.html
    ("Dzien dobry, dzwonie z komendy w sprawie proby zaciagniecia kredytu na Pana dane. Za chwile polaczy sie "
     "konsultant z banku. Prosze przelac oszczednosci na konto techniczne do czasu zakonczenia sprawy.", "scam"),
    # źródło: https://www.pkobp.pl/aktualnosci/bezpieczenstwo/oszusci-podszywaja-sie-pod-pracownikow-banku
    ("Prosze zainstalowac program AnyDesk z linku, ktory wyslalem SMS-em, i podac mi numer, "
     "ktory sie wyswietli. Wtedy zabezpiecze Panstwa srodki.", "scam"),
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorzec "zalogowales sie z innej lokalizacji ... sprawdz natychmiast", 2026-10)
    ("Zalogowales sie na swoje konto z innej lokalizacji. Sprawdz natychmiast: https://konto-alert.info/x", "scam"),

    # --- Sprzedaż w internecie: OLX, Vinted ---
    # źródło: https://www.benchmark.pl/cert-orange-ostrzega-sms-verify-i-falszywa-weryfikacja-olx-7327576877594784a
    ("Verify: Twoje konto sprzedawcy wymaga weryfikacji, kupujacy oplacil przedmiot. "
     "https://olx-pl.weryfikacja-sprzedazy.eu.cc/olx/482913774", "scam"),
    # źródło: https://spidersweb.pl/2026/10/falszywy-link-oszustwo-sms-zabezpieczenie.html
    ("Dzien dobry, kupilem Pani kurtke na Vinted i oplacilem z dostawa. Prosze wejsc w link i wybrac "
     "'odbierz srodki': vinted-transakcja.shop", "scam"),
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorzec "czy to panstwo sprzedaja", 2026-08)
    ("Czy to Panstwo sprzedaja? https://ogloszenie-sprawdz.click/8812", "suspicious"),

    # --- Inwestycje, krypto, praca, pożyczki ---
    # źródło: https://cebrf.knf.gov.pl/images/Komunikaty/Raporty/Pdf/Schematy_i_metody_oszustw_inwestycyjnych.pdf
    ("Inwestycja w projekt Baltic Pipe pozwala zarabiac od 4000 zl miesiecznie. Polecaja ja znani eksperci "
     "z telewizji. Zarejestruj sie dzis: baltic-inwest.vip", "scam"),
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorzec "proba przelania srodkow na portfel ledger", 2026-09)
    ("Wykryto probe przelania srodkow z Twojego portfela Ledger. Jesli to nie Ty, anuluj transakcje: "
     "ledger-anuluj.top", "scam"),
    # źródło: https://www.benchmark.pl/falszywe-oferty-pracy-przez-sms-i-telegram-cert-ostrzega-7334285676505312a
    ("Czesc! Szukamy osob do prostej pracy z domu: lajkowanie filmow na TikToku, 300 PLN dziennie. "
     "Kliknij link i napisz do nas: praca-zdalna24.site", "scam"),
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorzec "nowa praca online dla N osob ... euro godzina ... tg", 2026-09)
    ("Nowa praca online dla 20 osob, 25 euro za godzine. Dolacz do grupy na Telegramie i odbierz 10 euro na start",
     "scam"),
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorzec "wniosek o udzielenie pozyczki zostal zaakceptowany", 2026-10)
    ("Twoj wniosek o pozyczke zostal zaakceptowany. Kwota 4500 zl czeka na wyplate, potwierdz ja tutaj: "
     "szybka-wyplata.online", "scam"),

    # --- Operatorzy, komunikatory, subskrypcje ---
    # źródło: https://android.com.pl/tech/1037052-cert-atak-phishing-aktualizacja-sim/
    ("Twoja karta SIM zostanie zablokowana. Zweryfikuj numer i zaktualizuj karte SIM: "
     "orange-sim-aktualizacja.com", "scam"),
    # źródło: https://antyweb.pl/whatsapp-kradziez-konta-cert
    ("WhatsApp: Twoje konto zostalo zablokowane. Aby je odblokowac, wpisz kod weryfikacyjny z SMS-a: "
     "whatsapp-odblokuj.net", "scam"),
    # źródło: https://telegraf.cert.pl/api/v1/public/patterns (wzorzec "netflix nie udalo nam sie przetworzyc platnosci", 2026-07)
    ("Netflix: nie udalo nam sie przetworzyc Twojej platnosci. Odnow subskrypcje: netfiix-konto.com", "scam"),

    # --- Kody QR (quishing) ---
    # źródło: https://www.eset.com/pl/about/newsroom/press-releases/news/cyberprzestepcy-znow-wykorzystuja-qr-kody-uwaga-min-na-parkomaty/
    ("Zaplac za parkowanie szybciej! Zeskanuj kod QR na naklejce i oplac postoj telefonem: parkuj-szybko.pl",
     "suspicious"),
    # źródło: https://android.com.pl/tech/645126-oszustwo-falszywy-mandat-kody-qr/
    ("Wezwanie Strazy Miejskiej: nieprawidlowe parkowanie, kara 100 zl. Oplac w ciagu 7 dni, "
     "skanujac kod QR z tego wezwania.", "suspicious"),
]


# Zwykłe, prawdziwe w stylu wiadomości. Każda powinna dostać "no_signs".
REAL_LEGIT: list[str] = [
    # --- Paczki (oficjalne domeny) ---
    "InPost: Paczka od Allegro czeka w Paczkomacie KRA05M do 28.11. Kod odbioru: 551204. "
    "Szczegoly w aplikacji InPost Mobile lub na inpost.pl",
    "Kurier InPost bedzie dzis miedzy 14 a 16. Sledz przesylke: https://inpost.pl/sledzenie-przesylek",
    "DPD Polska: kurier dostarczy paczke 0012345 dzis w godz. 9-12. Zmien termin: https://www.dpd.com.pl",
    "Poczta Polska: przesylka polecona czeka do odbioru w placowce do 02.12. "
    "Sledz: https://emonitoring.poczta-polska.pl",
    "Allegro: Twoje zamowienie zostalo wyslane. Szczegoly: https://allegro.pl/moje-allegro/zakupy",

    # --- Banki i płatności (bez linków) ---
    "PKO BP: uznanie rachunku kwota 2350,00 PLN. Saldo dostepne: 3112,45 PLN.",
    "Platnosc BLIK 45,99 zl w sklepie Zabka zostala zaakceptowana.",
    "ING: zalogowano do Moje ING z nowego urzadzenia 24.11 o 19:02. Jesli to nie Ty, zadzwon na infolinie z karty.",
    "Santander: Twoja karta wygasa 12/2026. Nowa karta zostala wyslana na adres korespondencyjny.",
    "Allegro: zwrot srodkow 129,00 zl za zwrocony produkt zostal zlecony. Pieniadze pojawia sie na koncie do 3 dni.",

    # --- Kody 2FA ---
    "mBank: kod do potwierdzenia logowania: 739201. Nie podawaj go nikomu.",
    "Twoj kod weryfikacyjny WhatsApp: 418-552. Nie udostepniaj tego kodu nikomu.",
    "G-492811 to Twoj kod weryfikacyjny Google.",

    # --- Urzędy, media, operatorzy ---
    "ZUS: na Twoim koncie PUE ZUS jest nowa wiadomosc. Zaloguj sie na www.zus.pl, aby ja przeczytac.",
    "mObywatel: Twoje zeznanie PIT zostalo przetworzone. Zwrot podatku zostanie przekazany na wskazany rachunek. "
    "Szczegoly na podatki.gov.pl",
    "Orange: faktura za listopad na kwote 59,99 zl jest dostepna w Moim Orange. Termin platnosci 15.12.",
    "PGE Obrot: prognoza rozliczenia za energie jest dostepna w eBOK na pge.pl. Termin platnosci 10.12.",
    "Tauron: 27.11 w godz. 8-14 planowana przerwa w dostawie energii przy ul. Lipowej z powodu prac sieciowych. "
    "Wiecej: tauron-dystrybucja.pl",
    "Netflix: platnosc za subskrypcje zostala zrealizowana. Dziekujemy! Szczegoly konta na netflix.com",

    # --- Sprzedaż w internecie (w aplikacji, bez linku) ---
    "Vinted: kupujacy oplacil zamowienie. Wydrukuj etykiete w aplikacji Vinted i nadaj paczke w ciagu 5 dni.",
    "OLX: masz nowa wiadomosc od kupujacego w sprawie ogloszenia 'Rower miejski'. Odpowiedz w aplikacji OLX.",

    # --- Zdrowie, uczelnia, sklepy ---
    "Przychodnia: przypominamy o wizycie u lekarza rodzinnego 27.11 o 10:20. Aby odwolac, odpowiedz NIE.",
    "Zajecia z analizy w piatek odwolane, termin odrobienia podamy w USOS.",
    "Biedronka: Twoj kupon -20% na owoce jest aktywny do niedzieli w aplikacji Moja Biedronka.",

    # --- Rodzina ---
    "Mamo, dojechalam, wszystko ok. Zadzwonie wieczorem",
    "Kupisz chleb wracajac? I zadzwon do babci, pytala o Ciebie",
]
