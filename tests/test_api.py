"""Testy całego API (bez sieci i bez AI)."""

import os

os.environ["CERT_AUTO_REFRESH"] = "false"
os.environ["ANTHROPIC_API_KEY"] = ""
os.environ["RATE_LIMIT_PER_MINUTE"] = "1000"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app, cert, limiter  # noqa: E402
from tests.examples import LEGIT, SCAMS  # noqa: E402


@pytest.fixture()
def client():
    with TestClient(app) as c:
        cert.domains = {"znana-zla-domena.pl"}
        yield c


def test_homepage_is_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "Czy to oszustwo?" in response.text


def test_health(client):
    data = client.get("/api/health").json()
    assert data["status"] == "ok"
    assert data["ai_enabled"] is False


def test_cert_listed_domain_is_scam(client):
    data = client.post("/api/check", json={"text": "Sprawdz: https://znana-zla-domena.pl/x"}).json()
    assert data["verdict"] == "scam"
    assert data["links"] == [{"host": "znana-zla-domena.pl", "status": "cert_listed"}]
    assert "score" not in data  # punkty ukryte poza trybem DEBUG


@pytest.mark.parametrize("text,expected", SCAMS)
def test_scam_examples(client, text, expected):
    verdict = client.post("/api/check", json={"text": text}).json()["verdict"]
    assert verdict in ({"scam"} if expected == "scam" else {"scam", "suspicious"})


@pytest.mark.parametrize("text", LEGIT)
def test_legit_examples(client, text):
    assert client.post("/api/check", json={"text": text}).json()["verdict"] == "no_signs"


def test_rejects_empty_and_too_long(client):
    assert client.post("/api/check", json={"text": "   "}).status_code == 422
    assert client.post("/api/check", json={"text": "a" * 5000}).status_code == 413


def test_rate_limit(client):
    old = limiter.max_requests
    limiter.max_requests = 2
    limiter._hits.clear()
    try:
        codes = [client.post("/api/check", json={"text": "test"}).status_code for _ in range(3)]
        assert codes == [200, 200, 429]
    finally:
        limiter.max_requests = old
        limiter._hits.clear()
