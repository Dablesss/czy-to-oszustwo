"""Prosty limit zapytań na adres IP (okno przesuwne, w pamięci).

Wystarczy na jeden serwer. Przy kilku instancjach przenieś licznik do Redisa.
"""

import time
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: float = 60.0):
        self.max_requests = max_requests
        self.window = window_seconds
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        hits = self._hits[key]
        while hits and now - hits[0] > self.window:
            hits.popleft()
        if len(hits) >= self.max_requests:
            return False
        hits.append(now)
        # Sprzątanie, żeby słownik nie rósł w nieskończoność
        if len(self._hits) > 10_000:
            self._hits = defaultdict(deque, {k: v for k, v in self._hits.items() if v})
        return True


def client_ip(headers: dict, fallback: str | None) -> str:
    """Adres klienta. Za proxy (Railway, Fly) prawdziwe IP jest w X-Forwarded-For."""
    forwarded = headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return fallback or "unknown"
