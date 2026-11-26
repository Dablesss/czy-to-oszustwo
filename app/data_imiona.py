"""Najpopularniejsze polskie imiona (z popularnymi zdrobnieniami) do maskowania przed AI.

Zapis: małe litery, bez polskich znaków, w mianowniku ("lukasz", "malgorzata"),
bo porównujemy je ze słowem po normalizacji (app/checks/text_rules.normalize_text).

Celowo pominięte imiona, które są też zwykłymi słowami albo nazwami usług
i dawałyby fałszywe maskowanie: "Pola" (pola), "Róża" (kwiat), "Max" (HBO Max), "Lech" (piwo, klub),
"Wiara", "Nadzieja", "Wit".
"""

IMIONA: frozenset[str] = frozenset({
    # --- imiona żeńskie ---
    "anna", "ania", "maria", "marysia", "katarzyna", "kasia", "malgorzata", "gosia",
    "agnieszka", "barbara", "basia", "krystyna", "ewa", "elzbieta", "ela", "zofia", "zosia",
    "teresa", "magdalena", "magda", "joanna", "asia", "janina", "monika", "danuta",
    "jadwiga", "aleksandra", "ola", "halina", "irena", "beata", "marta", "dorota",
    "jolanta", "jola", "iwona", "karolina", "grazyna", "natalia", "bozena", "renata",
    "urszula", "ula", "sylwia", "justyna", "helena", "paulina", "agata", "wanda",
    "alicja", "julia", "julka", "anita", "stanislawa", "patrycja", "izabela", "iza",
    "ewelina", "marianna", "weronika", "edyta", "dominika", "wiktoria", "kamila", "lucyna",
    "zuzanna", "zuzia", "martyna", "emilia", "genowefa", "wieslawa", "marzena",
    "gabriela", "kinga", "klaudia", "aneta", "jozefa", "henryka", "zdzislawa", "bogumila",
    "amelia", "lena", "hanna", "hania", "maja", "oliwia", "nikola", "laura", "antonina",
    "nina", "michalina", "milena", "malwina", "roksana", "sandra", "angelika", "adrianna",
    "wioletta", "violetta", "lidia", "ilona", "honorata", "regina", "stefania", "kazimiera",
    "leokadia", "mieczyslawa", "czeslawa", "bronislawa", "ryszarda", "tamara", "hanka",
    "iga", "ada", "klara", "jagoda", "ksenia", "blanka", "lucja", "pamela", "dagmara",
    # --- imiona męskie ---
    "jan", "janek", "piotr", "krzysztof", "andrzej", "tomasz", "tomek", "pawel", "jozef",
    "marcin", "marek", "michal", "grzegorz", "jerzy", "jurek", "tadeusz", "adam",
    "lukasz", "zbigniew", "ryszard", "dariusz", "darek", "henryk", "mariusz", "kazimierz",
    "wojciech", "wojtek", "robert", "mateusz", "marian", "rafal", "jacek", "janusz",
    "miroslaw", "maciej", "maciek", "slawomir", "jaroslaw", "kamil", "wieslaw", "roman",
    "wladyslaw", "jakub", "kuba", "artur", "zdzislaw", "edward", "mieczyslaw", "damian",
    "dawid", "przemyslaw", "sebastian", "czeslaw", "leszek", "daniel", "waldemar",
    "stanislaw", "staszek", "bartosz", "bartek", "szymon", "filip", "antoni", "antek",
    "aleksander", "olek", "franciszek", "franek", "wiktor", "igor", "oliwier", "nikodem",
    "hubert", "kacper", "patryk", "adrian", "konrad", "karol", "norbert", "emil",
    "bogdan", "bogumil", "boguslaw", "witold", "zenon", "eugeniusz", "stefan",
    "leon", "ignacy", "tymon", "tymoteusz", "julian", "milosz", "dominik", "krystian",
    "lucjan", "gabriel", "hieronim", "bronislaw", "ireneusz", "arkadiusz",
    "arek", "sylwester", "radoslaw", "radek", "fabian", "olaf", "borys",
    "maksymilian", "ksawery", "bruno", "alan", "kajetan", "gustaw", "jedrzej", "kornel",
})
