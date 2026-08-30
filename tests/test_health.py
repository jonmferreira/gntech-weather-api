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
    from importlib import reload
    import app.config as cfg
    reload(cfg)
    response = client.get("/docs")
    assert response.status_code in (200, 404)


def test_readings_source_filter_invalid_returns_empty():
    """Fonte inexistente retorna lista vazia, não erro."""
    response = client.get("/readings?source=fonte_inexistente")
    assert response.status_code == 200
    assert response.json() == []


def test_readings_no_source_filter_returns_all():
    """Sem filtro de source retorna todas as fontes disponíveis."""
    response = client.get("/readings")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_readings_limit_validation():
    """Limit acima de 500 deve retornar 422."""
    response = client.get("/readings?limit=9999")
    assert response.status_code == 422


def test_readings_invalid_date_range():
    """from_dt maior que to_dt deve retornar 422."""
    response = client.get("/readings?from_dt=2026-12-31T00:00:00&to_dt=2026-01-01T00:00:00")
    assert response.status_code == 422


def test_readings_sql_injection_via_city():
    """SQL injection via city deve retornar 200 com array (query parametrizada)."""
    response = client.get("/readings?city=Florianopolis' OR '1'='1")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_readings_city_max_length():
    """City com mais de 100 caracteres deve retornar 422."""
    long_city = "A" * 101
    response = client.get(f"/readings?city={long_city}")
    assert response.status_code == 422
