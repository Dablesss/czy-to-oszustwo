"""AI może tylko podnieść ryzyko. Sprawdzamy to bez prawdziwego API (podmieniona funkcja)."""

import asyncio
from pathlib import Path

from app import analyzer, config
from app.checks.cert_list import CertList
from app.models import Signal, Verdict


def _run(text, fake_signal, monkeypatch):
    async def fake_assess(masked_text):
        assert "90010112345" not in masked_text  # do AI idzie tylko zamaskowany tekst
        return fake_signal

    monkeypatch.setattr(config, "LLM_ENABLED", True)
    monkeypatch.setattr(analyzer.llm, "assess", fake_assess)
    return asyncio.run(analyzer.analyze(text, CertList("", Path("/x"))))


def test_ai_can_raise_risk(monkeypatch):
    signal = Signal(code="llm_oszustwo", points=60, reason="AI: oszustwo", source="llm")
    result = _run("Pilnie odpisz na te wiadomosc, PESEL 90010112345", signal, monkeypatch)
    assert result.verdict == Verdict.SCAM
    assert result.used_ai


def test_ai_cannot_lower_risk(monkeypatch):
    # AI zwraca "brak oznak" (None), a reguły widzą oszustwo -> werdykt zostaje
    text = "Kliknij link i dokonaj doplaty 1,99 zl: inpost-doplata.top PESEL 90010112345"
    result = _run(text, None, monkeypatch)
    assert result.verdict == Verdict.SCAM
