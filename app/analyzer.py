"""Łączy wszystkie sprawdzenia w jeden werdykt.

Kolejność:
1. Wyciągnięcie linków z oryginalnego tekstu.
2. Lista CERT + analiza domeny dla każdego linku.
3. Reguły na treść.
4. Suma punktów (max 100).
5. Jeśli wynik jest niepewny i AI jest włączone: ocena AI na zamaskowanym tekście.
   AI może wynik tylko PODNIEŚĆ, nigdy obniżyć.
"""

from . import config
from .checks import domain, llm, text_rules
from .checks.cert_list import CertList
from .checks.links import extract_hosts
from .models import CheckedLink, CheckResponse, Signal, Verdict
from .privacy import mask_personal_data

# Reguły tekstu, które razem z linkiem dają dodatkowe punkty
_ASKS_FOR_ACTION = {
    "small_payment", "account_blocked", "personal_data_request", "prize_or_refund",
    "fine_or_debt", "utility_cutoff", "parcel_problem", "install_app",
}

TEXTS = {
    Verdict.SCAM: (
        "To wygląda na oszustwo",
        [
            "Nie klikaj w link i nie odpisuj.",
            "Nie podawaj danych karty, kodu BLIK, PIN-u ani hasła.",
            "Przekaż tę wiadomość SMS-em na numer 8080 (CERT Polska), a potem ją usuń.",
            "Jeśli już podałeś dane karty lub logowania, od razu zadzwoń do banku.",
        ],
    ),
    Verdict.SUSPICIOUS: (
        "Uważaj, to wygląda podejrzanie",
        [
            "Nie klikaj w link. Wejdź na stronę firmy sam, wpisując jej adres.",
            "Zadzwoń do firmy albo osoby na numer, który znasz, a nie ten z wiadomości.",
            "Nie podawaj danych karty, kodu BLIK, PIN-u ani hasła.",
        ],
    ),
    Verdict.NO_SIGNS: (
        "Nie widzimy oznak oszustwa",
        [
            "To nie jest gwarancja, że wiadomość jest bezpieczna.",
            "Nigdy nie podawaj kodu BLIK, PIN-u ani danych karty przez link z wiadomości.",
            "Jeśli coś Cię niepokoi, zapytaj kogoś bliskiego.",
        ],
    ),
}


def _verdict_for(score: int) -> Verdict:
    if score >= config.SCAM_THRESHOLD:
        return Verdict.SCAM
    if score >= config.SUSPICIOUS_THRESHOLD:
        return Verdict.SUSPICIOUS
    return Verdict.NO_SIGNS


async def analyze(text: str, cert: CertList, use_llm: bool = True) -> CheckResponse:
    signals: list[Signal] = []
    links: list[CheckedLink] = []

    # --- linki ---
    for host in extract_hosts(text):
        if cert.is_listed(host):
            links.append(CheckedLink(host=host, status="cert_listed"))
            signals.append(Signal(
                code="cert_listed", points=100, source="cert",
                reason=f"Adres {host} jest na Liście Ostrzeżeń CERT Polska jako niebezpieczny.",
            ))
            continue
        status, host_signals = domain.analyze_host(host)
        links.append(CheckedLink(host=host, status=status))
        signals.extend(host_signals)

    # --- treść ---
    text_signals = text_rules.check_text(text)
    signals.extend(text_signals)

    has_risky_link = any(link.status != "official" for link in links)
    if has_risky_link and any(s.code in _ASKS_FOR_ACTION for s in text_signals):
        signals.append(Signal(
            code="link_with_request", points=15, source="text",
            reason="Wiadomość łączy prośbę o działanie z linkiem do nieznanej strony.",
        ))

    # Podróbka marki w adresie + jakakolwiek "sztuczka" w treści = bardzo silny sygnał
    fakes_brand = any(s.code in {"brand_in_foreign_domain", "brand_typo"} for s in signals)
    if fakes_brand and text_signals:
        signals.append(Signal(
            code="brand_with_request", points=15, source="domain",
            reason="Wiadomość podszywa się pod znaną firmę i prowadzi na obcą stronę.",
        ))

    score = min(100, sum(s.points for s in signals))

    # --- AI (tylko gdy wynik niepewny) ---
    used_ai = False
    unsure = config.LLM_ASK_MIN_SCORE <= score <= config.LLM_ASK_MAX_SCORE
    unknown_link_only = score == 0 and has_risky_link
    if use_llm and config.LLM_ENABLED and (unsure or unknown_link_only):
        ai_signal = await llm.assess(mask_personal_data(text))
        used_ai = True
        if ai_signal:
            signals.append(ai_signal)
            score = max(score, ai_signal.points)  # AI tylko podnosi

    verdict = _verdict_for(score)
    title, advice = TEXTS[verdict]

    # Pokazujemy maks. 3 najważniejsze powody, bez punktów
    reasons: list[str] = []
    for s in sorted(signals, key=lambda s: s.points, reverse=True):
        if s.reason not in reasons:
            reasons.append(s.reason)
    reasons = reasons[:3]
    if not reasons:
        reasons = ["Nie znaleźliśmy typowych sztuczek oszustów w tej wiadomości."]

    return CheckResponse(
        verdict=verdict,
        title=title,
        advice=advice,
        reasons=reasons,
        links=links,
        used_ai=used_ai,
        score=score if config.DEBUG else None,
        signals=signals if config.DEBUG else None,
    )
