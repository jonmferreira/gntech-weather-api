import logging
from datetime import datetime, timezone

import httpx
import sqlalchemy.exc

from app.config import settings
from app.db import SessionLocal
from app.models import WeatherReading
from app.services import source_status

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
        msg = f"timeout ao buscar '{city}'"
        logger.error("OpenWeather: %s.", msg)
        source_status.mark_failure("openweather", msg)
        return

    if response.status_code == 429:
        msg = "rate limit excedido — ciclo ignorado"
        logger.warning("OpenWeather: %s.", msg)
        source_status.mark_failure("openweather", msg)
        return
    if response.status_code == 401:
        msg = "chave de API invalida ou ainda nao ativada"
        logger.error("OpenWeather: %s.", msg)
        source_status.mark_failure("openweather", msg)
        return
    if response.status_code == 404:
        msg = f"cidade '{city}' nao encontrada"
        logger.warning("OpenWeather: %s.", msg)
        source_status.mark_failure("openweather", msg)
        return

    try:
        response.raise_for_status()
        data = response.json()
    except httpx.HTTPStatusError as exc:
        msg = f"erro HTTP {exc.response.status_code}"
        logger.error("OpenWeather: %s para '%s'.", msg, city)
        source_status.mark_failure("openweather", msg)
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
        source="openweather",
    )

    db = SessionLocal()
    try:
        db.add(reading)
        db.commit()
        source_status.mark_success("openweather")
        logger.info(
            "Leitura salva: %s/%s — %.1f°C, umidade %d%%",
            reading.city,
            reading.country,
            reading.temp_celsius,
            reading.humidity_pct,
        )
    except sqlalchemy.exc.SQLAlchemyError as exc:
        db.rollback()
        source_status.mark_failure("openweather", str(exc))
        logger.error("Erro ao salvar leitura de '%s': %s", city, exc)
    finally:
        db.close()


def fetch_all_cities() -> None:
    cities = [c for c in settings.cities.split(";") if c.strip()]
    for city_country in cities:
        _fetch_city(city_country)
