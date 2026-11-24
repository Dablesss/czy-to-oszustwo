"""Schematy danych: co przychodzi do API i co z niego wychodzi."""

from enum import Enum

from pydantic import BaseModel, Field


class Verdict(str, Enum):
    SCAM = "scam"              # czerwona karta
    SUSPICIOUS = "suspicious"  # żółta karta
    NO_SIGNS = "no_signs"      # zielona karta: NIE "bezpieczne", tylko "brak oznak"


class Signal(BaseModel):
    """Pojedynczy sygnał ostrzegawczy znaleziony przez jedno ze sprawdzeń."""

    code: str            # np. "cert_listed", "brand_lookalike"
    points: int          # ile punktów ryzyka dokłada
    reason: str          # wyjaśnienie prostym językiem, pokazywane użytkownikowi
    source: str          # "cert", "domain", "text", "llm"


class CheckedLink(BaseModel):
    host: str
    status: str          # "cert_listed" | "official" | "suspicious" | "unknown"


class CheckRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Treść wiadomości albo sam link")


class CheckResponse(BaseModel):
    verdict: Verdict
    title: str
    advice: list[str]
    reasons: list[str]
    links: list[CheckedLink]
    used_ai: bool
    # Tylko w trybie DEBUG:
    score: int | None = None
    signals: list[Signal] | None = None
