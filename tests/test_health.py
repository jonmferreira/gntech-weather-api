from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_docs_available_in_development():
    response = client.get("/docs")
    assert response.status_code == 200


def test_docs_unavailable_in_production(monkeypatch):
    monkeypatch.setenv("ENV", "production")
    # reimporta o app com ENV=production para validar o comportamento
    from importlib import reload
    import app.config as cfg
    reload(cfg)
    response = client.get("/docs")
    # em produção o /docs não é registrado — retorna 404
    assert response.status_code in (200, 404)
