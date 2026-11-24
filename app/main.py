"""Serwer FastAPI: API /api/check oraz strona (PWA) z katalogu static/.

Uruchomienie: uvicorn app.main:app --reload
"""

import asyncio
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from . import config
from .analyzer import analyze
from .checks.cert_list import CertList
from .models import CheckRequest, CheckResponse
from .ratelimit import RateLimiter, client_ip

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("app")

cert = CertList(config.CERT_LIST_URL, config.CERT_CACHE_PATH)
limiter = RateLimiter(config.RATE_LIMIT_PER_MINUTE)


@asynccontextmanager
async def lifespan(app: FastAPI):
    cert.load_cache()
    task = None
    if config.CERT_AUTO_REFRESH:
        task = asyncio.create_task(cert.refresh_forever(config.CERT_REFRESH_MINUTES))
    log.info("AI: %s", "włączone" if config.LLM_ENABLED else "wyłączone (brak klucza API)")
    yield
    if task:
        task.cancel()


app = FastAPI(title="Czy to oszustwo?", lifespan=lifespan, docs_url="/api/docs", redoc_url=None)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
        "connect-src 'self'; manifest-src 'self'"
    )
    return response


@app.post("/api/check", response_model=CheckResponse, response_model_exclude_none=True)
async def check(body: CheckRequest, request: Request) -> CheckResponse:
    ip = client_ip(dict(request.headers), request.client.host if request.client else None)
    if not limiter.allow(ip):
        raise HTTPException(status_code=429, detail="Za dużo sprawdzeń. Spróbuj ponownie za minutę.")

    text = body.text.strip()
    if len(text) > config.MAX_TEXT_LENGTH:
        raise HTTPException(
            status_code=413,
            detail=f"Wiadomość jest za długa. Wklej maksymalnie {config.MAX_TEXT_LENGTH} znaków.",
        )
    if not text:
        raise HTTPException(status_code=422, detail="Wklej treść wiadomości albo link.")

    # Uwaga: celowo NIE logujemy treści wiadomości (prywatność). Tylko werdykt.
    result = await analyze(text, cert)
    log.info("check verdict=%s links=%d ai=%s", result.verdict.value, len(result.links), result.used_ai)
    return result


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "cert_domains": len(cert.domains),
        "cert_last_refresh_minutes_ago": (
            round((time.time() - cert.last_refresh) / 60) if cert.last_refresh else None
        ),
        "ai_enabled": config.LLM_ENABLED,
    }


@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


# Strona musi być zamontowana na końcu, żeby nie przykryć /api/...
app.mount("/", StaticFiles(directory=config.BASE_DIR / "static", html=True), name="static")
