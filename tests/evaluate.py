"""Mierzy trafność reguł na zestawach przykładów (bez AI i bez listy CERT).

Uruchom: python -m tests.evaluate

Są trzy zestawy:
- podstawowy (tests/examples.py: SCAMS, LEGIT) – ten sam, którego używa pytest,
- realny (tests/examples_real.py: REAL_SCAMS, REAL_LEGIT) – przykłady wzorowane
  na prawdziwych kampaniach. Dla niego wypisujemy też listę pomyłek ze szczegółami,
- trudne zwykłe wiadomości (tests/examples_real.py: HARD_LEGIT) – same zwykłe SMS-y,
  które używają słów oszustów (np. ostrzeżenia banków). Liczymy tylko fałszywe alarmy.
"""

import asyncio
from pathlib import Path

from app import config
from app.analyzer import analyze
from app.checks.cert_list import CertList
from app.models import Verdict
from tests.examples import LEGIT, SCAMS
from tests.examples_real import HARD_LEGIT, REAL_LEGIT, REAL_SCAMS

# Werdykty jako liczby, żeby dało się je porównywać: "scam" jest "mocniejszy" niż "suspicious".
RANK = {Verdict.NO_SIGNS: 0, Verdict.SUSPICIOUS: 1, Verdict.SCAM: 2}

# Ile znaków tekstu pokazywać w jednej linii wyniku.
SHORT = 70


def shorten(text: str, length: int = SHORT) -> str:
    """Skraca tekst do jednej krótkiej linii (bez entera), żeby wynik był czytelny."""
    one_line = " ".join(text.split())
    if len(one_line) <= length:
        return one_line
    return one_line[: length - 3] + "..."


async def run_set(name: str, scams: list[tuple[str, str]], legit: list[str], cert: CertList) -> list[dict]:
    """Sprawdza jeden zestaw przykładów, wypisuje wynik i zwraca listę pomyłek.

    Pomyłka to:
    - oszustwo, które dostało słabszy werdykt niż oczekiwany (np. "suspicious" zamiast "scam"),
    - zwykła wiadomość, która dostała cokolwiek innego niż "no_signs" (fałszywy alarm).
    """
    mistakes: list[dict] = []

    caught = 0   # oszustwa z werdyktem co najmniej takim, jak oczekiwany
    missed = 0   # oszustwa, które dostały "no_signs", czyli zostały całkiem przepuszczone
    print(f"\n######## ZESTAW: {name} ########")
    print("=== OSZUSTWA ===")
    for text, expected in scams:
        result = await analyze(text, cert, use_llm=False)
        ok = RANK[result.verdict] >= RANK[Verdict(expected)]
        if ok:
            caught += 1
        else:
            mistakes.append({"text": text, "expected": expected, "result": result})
        if result.verdict == Verdict.NO_SIGNS:
            missed += 1
        print(f"{'OK  ' if ok else 'MISS'} {result.verdict.value:10} | {shorten(text)}")

    false_alarms = 0
    print("\n=== ZWYKŁE WIADOMOŚCI ===")
    for text in legit:
        result = await analyze(text, cert, use_llm=False)
        alarm = result.verdict != Verdict.NO_SIGNS
        if alarm:
            false_alarms += 1
            mistakes.append({"text": text, "expected": Verdict.NO_SIGNS.value, "result": result})
        print(f"{'ALARM' if alarm else 'OK   '} {result.verdict.value:10} | {shorten(text)}")

    # Trafność = ile wszystkich przykładów (oszustw i zwykłych) oceniliśmy dobrze.
    total = len(scams) + len(legit)
    correct = caught + (len(legit) - false_alarms)

    print(f"\n--- Podsumowanie: {name} ---")
    print(f"Trafność ogółem:     {correct}/{total} ({correct / total:.0%})")
    # Zestaw HARD_LEGIT nie ma oszustw, więc nie ma czego liczyć (i nie dzielimy przez zero).
    if scams:
        print(f"Wykryte oszustwa:    {caught}/{len(scams)} ({caught / len(scams):.0%})")
        print(f"Przepuszczone (no_signs): {missed}/{len(scams)} ({missed / len(scams):.0%})")
    print(f"Fałszywe alarmy:     {false_alarms}/{len(legit)} ({false_alarms / len(legit):.0%})")
    return mistakes


def print_mistakes(title: str, mistakes: list[dict]) -> None:
    """Wypisuje pomyłki: tekst, oczekiwany i otrzymany werdykt, punkty i kody sygnałów."""
    print(f"\n=== POMYŁKI: {title} ({len(mistakes)}) ===")
    for m in mistakes:
        result = m["result"]
        # Kody sygnałów, np. "parcel_problem(15)". Działa, bo niżej włączamy config.DEBUG.
        codes = ", ".join(f"{s.code}({s.points})" for s in result.signals or []) or "brak"
        print(f"- {shorten(m['text'], 90)}")
        print(f"    oczekiwano: {m['expected']:10} otrzymano: {result.verdict.value:10} "
              f"punkty: {result.score}  sygnały: {codes}")


async def main() -> None:
    # Tryb debug: analyze() zwraca wtedy punkty i listę sygnałów (potrzebne do listy pomyłek).
    # Zmieniamy to tylko na czas tego skryptu, nie w aplikacji.
    config.DEBUG = True

    cert = CertList("", Path("/nonexistent"))  # bez listy CERT: mierzymy same reguły

    await run_set("PODSTAWOWY (examples.py)", SCAMS, LEGIT, cert)
    real_mistakes = await run_set("REALNY (examples_real.py)", REAL_SCAMS, REAL_LEGIT, cert)
    print_mistakes("ZESTAW REALNY", real_mistakes)

    # Trudne zwykłe wiadomości: każda pomyłka w tym zestawie to fałszywy alarm.
    hard_mistakes = await run_set("TRUDNE ZWYKŁE (HARD_LEGIT)", [], HARD_LEGIT, cert)
    print_mistakes("TRUDNE ZWYKŁE – FAŁSZYWE ALARMY", hard_mistakes)


if __name__ == "__main__":
    asyncio.run(main())
