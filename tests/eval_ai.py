"""Mierzy, ile AI poprawia wynik reguł, ile to kosztuje i jak długo trwa.

Uruchom:
    python -m tests.eval_ai              # bez klucza: atrapa AI, nic nie idzie do sieci
    python -m tests.eval_ai --atrapa     # atrapa nawet wtedy, gdy klucz jest w .env
    python -m tests.eval_ai --limit 5    # maks. 5 wiadomości z każdego zestawu (0 = wszystkie)
    python -m tests.eval_ai --yes        # z kluczem: bez pytania o potwierdzenie

Dla każdej wiadomości z SCAMS, REAL_SCAMS, LEGIT, REAL_LEGIT i HARD_LEGIT liczymy:
- werdykt samych reguł (use_llm=False),
- werdykt z AI (ta sama ścieżka co w aplikacji: analyzer.analyze -> llm.assess),
- czy AI w ogóle było pytane (AI pytamy tylko przy niepewnym wyniku reguł),
- czas odpowiedzi AI i tokeny wejścia/wyjścia (z pola usage w odpowiedzi API).

Jak to działa bez zmieniania app/:
llm.py trzyma klienta API w zmiennej modułu `_client`. Podstawiamy tam własny obiekt
z metodą messages.create. W trybie atrapy ten obiekt sam zwraca stałą odpowiedź
(bez sieci). W trybie prawdziwym przekazuje zapytanie do prawdziwego klienta
i po drodze zapisuje czas i tokeny.
"""

import argparse
import asyncio
import time
from pathlib import Path
from types import SimpleNamespace

from app import config
from app.analyzer import analyze
from app.checks import llm
from app.checks.cert_list import CertList
from app.models import Verdict
from tests.examples import LEGIT, SCAMS
from tests.examples_real import HARD_LEGIT, REAL_LEGIT, REAL_SCAMS

# Werdykty jako liczby, żeby dało się je porównywać (jak w tests/evaluate.py).
RANK = {Verdict.NO_SIGNS: 0, Verdict.SUSPICIOUS: 1, Verdict.SCAM: 2}

# Ceny w USD za 1 mln tokenów: (wejście, wyjście). Źródło: cennik Anthropic, stan na 11.2026.
# Jeśli zmienisz LLM_MODEL na model spoza tabeli, dopisz go tutaj.
PRICES = {
    "claude-haiku-5-5": (0.10, 0.50),
    "claude-sonnet-5-5": (2.00, 10.00),
    "claude-opus-5-5": (4.00, 20.00),
}
DEFAULT_PRICE = PRICES["claude-haiku-5-5"]

# Szacunek przed startem: ok. 3 znaki tekstu na token (polski tekst tokenizuje się gorzej
# niż angielski, więc liczymy ostrożnie). Na wyjściu zakładamy najgorszy przypadek,
# czyli pełne max_tokens=200 z llm.py.
CHARS_PER_TOKEN = 3
MAX_OUTPUT_TOKENS = 200

# Stała odpowiedź atrapy. "podejrzane" daje 25 pkt, więc widać, jak działa zasada
# "AI tylko podnosi": oszustwo z regułami 60+ nie spadnie, zwykła wiadomość z 5-24 pkt
# urośnie do "suspicious" (fałszywy alarm). Wynik atrapy NIE mówi nic o jakości AI.
FAKE_ANSWER = '{"ocena": "podejrzane", "powod": "Atrapa AI: stała odpowiedź do testu skryptu."}'

SHORT = 60


def shorten(text: str, length: int = SHORT) -> str:
    """Skraca tekst do jednej krótkiej linii."""
    one_line = " ".join(text.split())
    return one_line if len(one_line) <= length else one_line[: length - 3] + "..."


class Recorder:
    """Zapisuje każde zapytanie do AI: czas, tokeny, powód zakończenia, błędy."""

    def __init__(self):
        self.calls: list[dict] = []

    def add(self, seconds: float, response=None, error: str | None = None) -> None:
        usage = getattr(response, "usage", None)
        self.calls.append({
            "seconds": seconds,
            "input_tokens": getattr(usage, "input_tokens", 0) or 0,
            "output_tokens": getattr(usage, "output_tokens", 0) or 0,
            "stop_reason": getattr(response, "stop_reason", None),
            "error": error,
        })


class _Messages:
    """Odpowiednik client.messages: ma tylko metodę create, której używa llm.py."""

    def __init__(self, recorder: Recorder, real_client=None):
        self.recorder = recorder
        self.real_client = real_client  # None = atrapa

    async def create(self, **kwargs):
        start = time.perf_counter()
        if self.real_client is None:
            # Atrapa: udajemy odpowiedź API. Tokeny wejścia szacujemy z długości tekstu.
            chars = len(kwargs.get("system", "")) + sum(len(m["content"]) for m in kwargs["messages"])
            response = SimpleNamespace(
                content=[SimpleNamespace(type="text", text=FAKE_ANSWER)],
                usage=SimpleNamespace(input_tokens=chars // CHARS_PER_TOKEN, output_tokens=25),
                stop_reason="end_turn",
            )
            self.recorder.add(time.perf_counter() - start, response)
            return response
        try:
            response = await self.real_client.messages.create(**kwargs)
        except Exception as exc:
            # Zapisujemy błąd i oddajemy go dalej: llm.assess go złapie i pominie AI.
            self.recorder.add(time.perf_counter() - start, error=type(exc).__name__)
            raise
        self.recorder.add(time.perf_counter() - start, response)
        return response


class RecordingClient:
    """Klient podstawiany w llm._client."""

    def __init__(self, recorder: Recorder, real_client=None):
        self.messages = _Messages(recorder, real_client)


def pick_sets(limit: int) -> list[tuple[str, list[tuple[str, str]]]]:
    """Zestawy jako listy (tekst, oczekiwany werdykt). Zwykłe wiadomości: "no_signs"."""
    sets = [
        ("SCAMS", list(SCAMS)),
        ("REAL_SCAMS", list(REAL_SCAMS)),
        ("LEGIT", [(t, Verdict.NO_SIGNS.value) for t in LEGIT]),
        ("REAL_LEGIT", [(t, Verdict.NO_SIGNS.value) for t in REAL_LEGIT]),
        ("HARD_LEGIT", [(t, Verdict.NO_SIGNS.value) for t in HARD_LEGIT]),
    ]
    if limit > 0:
        sets = [(name, items[:limit]) for name, items in sets]
    return sets


def is_correct(verdict: Verdict, expected: str) -> bool:
    """Oszustwo: werdykt co najmniej oczekiwany. Zwykła wiadomość: tylko "no_signs"."""
    if expected == Verdict.NO_SIGNS.value:
        return verdict == Verdict.NO_SIGNS
    return RANK[verdict] >= RANK[Verdict(expected)]


def ai_would_be_asked(score: int, has_risky_link: bool) -> bool:
    """Ten sam warunek co w analyzer.py (kopiujemy go tylko do szacunku kosztu)."""
    unsure = config.LLM_ASK_MIN_SCORE <= score <= config.LLM_ASK_MAX_SCORE
    return unsure or (score == 0 and has_risky_link)


def cost_usd(input_tokens: int, output_tokens: int) -> float:
    price_in, price_out = PRICES.get(config.LLM_MODEL, DEFAULT_PRICE)
    return input_tokens * price_in / 1_000_000 + output_tokens * price_out / 1_000_000


async def estimate(sets, cert: CertList) -> tuple[int, float]:
    """Liczy, ile razy AI zostanie zapytane, i szacuje koszt (górna granica)."""
    calls = 0
    input_tokens = 0
    for _, items in sets:
        for text, _ in items:
            result = await analyze(text, cert, use_llm=False)
            has_risky_link = any(link.status != "official" for link in result.links)
            if ai_would_be_asked(result.score, has_risky_link):
                calls += 1
                input_tokens += (len(llm.SYSTEM_PROMPT) + len(text) + 30) // CHARS_PER_TOKEN
    return calls, cost_usd(input_tokens, calls * MAX_OUTPUT_TOKENS)


async def run(sets, cert: CertList, recorder: Recorder) -> None:
    summary = []
    for name, items in sets:
        print(f"\n######## {name} ({len(items)}) ########")
        print("reguły     -> z AI       AI?   czas   tokeny  | tekst")
        ok_rules = ok_ai = asked = 0
        for text, expected in items:
            rules = await analyze(text, cert, use_llm=False)
            calls_before = len(recorder.calls)
            with_ai = await analyze(text, cert, use_llm=True)
            new_calls = recorder.calls[calls_before:]

            ok_rules += is_correct(rules.verdict, expected)
            ok_ai += is_correct(with_ai.verdict, expected)
            asked += with_ai.used_ai

            if new_calls:
                call = new_calls[0]
                ai_info = f"tak {call['seconds']:5.2f}s {call['input_tokens']:4}/{call['output_tokens']:<3}"
                if call["error"]:
                    ai_info = f"BŁĄD {call['error']}"
            else:
                ai_info = "nie"
            changed = " *" if rules.verdict != with_ai.verdict else "  "
            mark = "OK " if is_correct(with_ai.verdict, expected) else "ŹLE"
            print(f"{rules.verdict.value:10} -> {with_ai.verdict.value:10}{changed} {ai_info:22} "
                  f"{mark} | {shorten(text)}")
        summary.append((name, len(items), ok_rules, ok_ai, asked))

    print_summary(summary, recorder)


def print_summary(summary, recorder: Recorder) -> None:
    print("\n=================== PODSUMOWANIE ===================")
    print(f"{'zestaw':12} {'reguły':>10} {'z AI':>10} {'pytań do AI':>12}")
    for name, total, ok_rules, ok_ai, asked in summary:
        print(f"{name:12} {ok_rules:>4}/{total:<3}    {ok_ai:>4}/{total:<3}    {asked:>8}")
    print("(liczba = dobrze ocenione: oszustwa wykryte, zwykłe bez alarmu; * w tabeli = AI zmieniło werdykt)")

    calls = recorder.calls
    good = [c for c in calls if not c["error"]]
    errors = len(calls) - len(good)
    tokens_in = sum(c["input_tokens"] for c in good)
    tokens_out = sum(c["output_tokens"] for c in good)
    print(f"\nZapytania do AI:   {len(calls)} (błędy: {errors})")
    if good:
        avg = sum(c["seconds"] for c in good) / len(good)
        slowest = max(c["seconds"] for c in good)
        print(f"Czas odpowiedzi:   średnio {avg:.2f} s, najdłużej {slowest:.2f} s")
        print(f"Tokeny:            wejście {tokens_in}, wyjście {tokens_out}")
        print(f"Koszt:             {cost_usd(tokens_in, tokens_out):.6f} USD "
              f"(średnio {cost_usd(tokens_in, tokens_out) / len(good):.6f} USD na zapytanie)")
        cut = sum(1 for c in good if c["stop_reason"] == "max_tokens")
        if cut:
            print(f"UWAGA: {cut} odpowiedzi ucięte przez max_tokens (AI nie dokończyło JSON-a).")


def ask_confirmation() -> bool:
    """Pytanie przed wydaniem pieniędzy. Brak odpowiedzi (np. w CI) = nie."""
    try:
        answer = input("Użyć prawdziwego klucza API? Wpisz 't', aby kontynuować: ")
    except EOFError:
        return False
    return answer.strip().lower() in {"t", "tak", "y", "yes"}


async def main() -> None:
    parser = argparse.ArgumentParser(description="Pomiar AI na zestawach przykładów.")
    parser.add_argument("--limit", type=int, default=20,
                        help="maks. liczba wiadomości z każdego zestawu (0 = wszystkie), domyślnie 20")
    parser.add_argument("--yes", action="store_true", help="nie pytaj o potwierdzenie przed użyciem klucza")
    parser.add_argument("--atrapa", action="store_true", help="użyj atrapy, nawet jeśli jest klucz")
    args = parser.parse_args()

    # Tryb debug, żeby analyze() zwracało punkty (potrzebne do szacunku). Tylko w tym skrypcie.
    config.DEBUG = True
    cert = CertList("", Path("/nonexistent"))  # bez listy CERT, jak w tests/evaluate.py
    sets = pick_sets(args.limit)
    use_fake = args.atrapa or not config.ANTHROPIC_API_KEY

    calls, estimated = await estimate(sets, cert)
    print(f"Model: {config.LLM_MODEL}")
    if config.LLM_MODEL not in PRICES:
        print("UWAGA: modelu nie ma w tabeli PRICES, liczę według ceny Haiku.")
    print(f"Wiadomości: {sum(len(items) for _, items in sets)}, zapytań do AI: {calls}")
    print(f"Szacowany koszt (górna granica): {estimated:.4f} USD")

    if use_fake:
        print("\n*** TRYB ATRAPY: brak ANTHROPIC_API_KEY albo --atrapa. Nic nie idzie do sieci. ***")
        print(f"*** AI zawsze odpowiada: {FAKE_ANSWER} ***")
        print("*** Wynik pokazuje działanie skryptu, NIE jakość AI. Czas i tokeny są udawane. ***")
        real_client = None
    else:
        print("\n*** TRYB PRAWDZIWY: zapytania idą do API Anthropic i kosztują. ***")
        if not args.yes and not ask_confirmation():
            print("Przerwano. Nic nie wysłano.")
            return
        real_client = llm._get_client()

    recorder = Recorder()
    # Podstawiamy klienta w llm.py i włączamy AI na czas tego skryptu.
    llm._client = RecordingClient(recorder, real_client)
    config.LLM_ENABLED = True
    try:
        await run(sets, cert, recorder)
    finally:
        llm._client = None  # sprzątamy, żeby nic nie zostało po skrypcie

    if use_fake:
        print("\n(Atrapa. Prawdziwy pomiar: ustaw ANTHROPIC_API_KEY i uruchom python -m tests.eval_ai)")


if __name__ == "__main__":
    asyncio.run(main())
