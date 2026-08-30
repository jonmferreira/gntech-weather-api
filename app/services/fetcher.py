import logging
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.db import SessionLocal
from app.models import WeatherReading

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.openweathermap.org/data/2.5/weather"


def _fetch_city(city_country: str) -> None:
    city, country = city_country.strip().split(",", 1)
    params = {
        "q": f"{city.strip()},{country.strip()}",
        "appid": settings.openweather_api_key,
        "units": "metric",
        "lang": "pt_br",
    }

    try:
        response = httpx.get(_BASE_URL, params=params, timeout=10)
    except httpx.TimeoutException:
        logger.error("OpenWeather: timeout ao buscar '%s'.", city)
        return

    if response.status_code == 429:
        logger.warning("OpenWeather: rate limit excedido — ciclo ignorado.")
        return
    if response.status_code == 401:
        logger.error("OpenWeather: chave de API inválida ou ainda não ativada.")
        return
    if response.status_code == 404:
        logger.warning("OpenWeather: cidade '%s' não encontrada.", city)
        return

    try:
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPStatusError as exc:
        logger.error("OpenWeather: erro %s para '%s'.", exc.response.status_code, city)
        return

    reading = WeatherReading(
        city=data["name"],
        country=data["sys"]["country"],
        temp_celsius=data["main"]["temp"],
        feels_like=data["main"]["feels_like"],
        temp_min=data["main"]["temp_min"],
        temp_max=data["main"]["temp_max"],
        humidity_pct=data["main"]["humidity"],
        pressure_hpa=data["main"]["pressure"],
        wind_speed_ms=data["wind"]["speed"],
        wind_deg=data["wind"].get("deg", 0),
        cloudiness_pct=data["clouds"]["all"],
        description=data["weather"][0]["description"],
        icon=data["weather"][0]["icon"],
        dt=datetime.fromtimestamp(data["dt"], tz=timezone.utc),
        fetched_at=datetime.now(tz=timezone.utc),
    )

    db = SessionLocal()
    try:
        db.add(reading)
        db.commit()
        logger.info(
            "Leitura salva: %s/%s — %.1f°C, umidade %d%%",
            reading.city,
            reading.country,
            reading.temp_celsius,
            reading.humidity_pct,
        )
    except Exception as exc:
        db.rollback()
        logger.error("Erro ao salvar leitura de '%s': %s", city, exc)
    finally:
        db.close()


def fetch_all_cities() -> None:
    cities = [c for c in settings.cities.split(";") if c.strip()]
    for city_country in cities:
        _fetch_city(city_country)
