"""Lista Ostrzeżeń przed niebezpiecznymi stronami CERT Polska.

Źródło: https://hole.cert.pl/domains/v2/domains.txt (jedna domena na linię).
Lista jest trzymana w pamięci i odświeżana w tle. Ostatnia pobrana kopia
leży na dysku, więc aplikacja działa także wtedy, gdy CERT jest chwilowo niedostępny.
"""

import asyncio
import logging
import time
from pathlib import Path

import httpx

from .links import normalize_host

log = logging.getLogger(__name__)


class CertList:
    def __init__(self, url: str, cache_path: Path):
        self.url = url
        self.cache_path = cache_path
        self.domains: set[str] = set()
        self.last_refresh: float | None = None

    # --- ładowanie ---

    @staticmethod
    def _parse(text: str) -> set[str]:
        domains = set()
        for line in text.splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                domains.add(normalize_host(line))
        return domains

    def load_cache(self) -> None:
        if self.cache_path.exists():
            self.domains = self._parse(self.cache_path.read_text(encoding="utf-8"))
            log.info("Wczytano %d domen z kopii na dysku", len(self.domains))

    async def refresh(self) -> bool:
        """Pobiera świeżą listę. Zwraca True, jeśli się udało."""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.get(self.url)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            log.warning("Nie udało się pobrać listy CERT: %s", exc)
            return False

        domains = self._parse(response.text)
        # Zabezpieczenie: jeśli CERT zmieni format i dostaniemy śmieci, nie nadpisujemy dobrej listy.
        if len(domains) < 100:
            log.warning("Lista CERT podejrzanie krótka (%d), zostawiam poprzednią", len(domains))
            return False

        self.domains = domains
        self.last_refresh = time.time()
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(response.text, encoding="utf-8")
        log.info("Pobrano listę CERT: %d domen", len(domains))
        return True

    async def refresh_forever(self, every_minutes: int) -> None:
        while True:
            await self.refresh()
            await asyncio.sleep(every_minutes * 60)

    # --- sprawdzanie ---

    def is_listed(self, host: str) -> bool:
        """Czy host albo któraś z jego domen nadrzędnych jest na liście.

        "a.b.zla-domena.pl" pasuje, jeśli na liście jest "zla-domena.pl".
        """
        parts = host.split(".")
        return any(".".join(parts[i:]) in self.domains for i in range(len(parts) - 1))
