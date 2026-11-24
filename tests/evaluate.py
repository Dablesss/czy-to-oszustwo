"""Mierzy trafność reguł na zestawie przykładów (bez AI).

Uruchom: python -m tests.evaluate
"""

import asyncio
from pathlib import Path

from app.analyzer import analyze
from app.checks.cert_list import CertList
from app.models import Verdict
from tests.examples import LEGIT, SCAMS

RANK = {Verdict.NO_SIGNS: 0, Verdict.SUSPICIOUS: 1, Verdict.SCAM: 2}


async def main() -> None:
    cert = CertList("", Path("/nonexistent"))  # bez listy CERT: mierzymy same reguły

    caught = 0
    print("=== OSZUSTWA ===")
    for text, expected in SCAMS:
        result = await analyze(text, cert, use_llm=False)
        ok = RANK[result.verdict] >= RANK[Verdict(expected)]
        caught += ok
        print(f"{'OK  ' if ok else 'MISS'} {result.verdict.value:10} | {text[:70]}")

    false_alarms = 0
    print("\n=== ZWYKŁE WIADOMOŚCI ===")
    for text in LEGIT:
        result = await analyze(text, cert, use_llm=False)
        alarm = result.verdict != Verdict.NO_SIGNS
        false_alarms += alarm
        print(f"{'ALARM' if alarm else 'OK   '} {result.verdict.value:10} | {text[:70]}")

    print(f"\nWykryte oszustwa: {caught}/{len(SCAMS)} ({caught / len(SCAMS):.0%})")
    print(f"Fałszywe alarmy:  {false_alarms}/{len(LEGIT)} ({false_alarms / len(LEGIT):.0%})")


if __name__ == "__main__":
    asyncio.run(main())
