"""Ustawienia aplikacji czytane ze zmiennych środowiskowych (plik .env)."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent


def _bool(name: str, default: bool) -> bool:
    return os.getenv(name, str(default)).strip().lower() in {"1", "true", "yes", "tak"}


# --- AI (opcjonalne) ---
# Bez klucza aplikacja działa wyłącznie na regułach.
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "").strip()
LLM_MODEL = os.getenv("LLM_MODEL", "claude-haiku-5-5")
LLM_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT_SECONDS", "10"))
LLM_ENABLED = bool(ANTHROPIC_API_KEY) and _bool("LLM_ENABLED", True)

# --- Lista Ostrzeżeń CERT Polska ---
CERT_LIST_URL = os.getenv("CERT_LIST_URL", "https://hole.cert.pl/domains/v2/domains.txt")
CERT_CACHE_PATH = Path(os.getenv("CERT_CACHE_PATH", BASE_DIR / "data" / "cert_domains.txt"))
CERT_REFRESH_MINUTES = int(os.getenv("CERT_REFRESH_MINUTES", "60"))
CERT_AUTO_REFRESH = _bool("CERT_AUTO_REFRESH", True)

# --- Ochrona przed nadużyciami ---
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", "10"))
MAX_TEXT_LENGTH = int(os.getenv("MAX_TEXT_LENGTH", "3000"))

# --- Progi werdyktu (punkty 0–100) ---
SCAM_THRESHOLD = 60
SUSPICIOUS_THRESHOLD = 25
# Przedział, w którym wynik reguł jest "niepewny" i warto zapytać AI.
LLM_ASK_MIN_SCORE = 5
LLM_ASK_MAX_SCORE = SCAM_THRESHOLD - 1

# W trybie debug odpowiedź API zawiera punkty i pełną listę sygnałów.
# Na produkcji wyłącz, żeby oszuści nie uczyli się, jak obejść reguły.
DEBUG = _bool("DEBUG", False)
