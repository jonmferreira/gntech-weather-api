import logging
from datetime import datetime, timezone

import httpx

from app.config import settings
from app.db import SessionLocal
from app.models import WeatherReading

logger = logging.getLogger(__name__)

_BASE_URL = "https://api.open-meteo.com/v1/forecast"

# Mapeamento WMO weather codes → descrição em português
_WMO_DESCRIPTIONS: dict[int, str] = {
    0: "céu limpo",
    1: "predominantemente limpo",
    2: "parcialmente nublado",
    3: "nublado",
    45: "neblina",
    48: "neblina com geada",
    51: "garoa leve",
    53: "garoa moderada",
    55: "garoa intensa",
    61: "chuva leve",
    63: "chuva moderada",
    65: "chuva intensa",
    71: "neve leve",
    73: "neve moderada",
    75: "neve intensa",
    80: "pancadas de chuva leve",
    81: "pancadas de chuva moderada",
    82: "pancadas de chuva intensa",
    95: "trovoada",
    99: "trovoada com granizo",
}


def _fetch_coords(city_name: str, country: str, lat: float, lon: float) -> None:
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ",".join([
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "weather_code",
            "surface_pressure",
            "wind_speed_10m",
            "wind_direction_10m",
            "cloud_cover",
        ]),
        "timezone": "America/Sao_Paulo",
    }

    try:
        response = httpx.get(_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except httpx.TimeoutException:
        logger.error("Open-Meteo: timeout ao buscar '%s'.", city_name)
        return
    except httpx.HTTPStatusError as exc:
        logger.error("Open-Meteo: erro %s para '%s'.", exc.response.status_code, city_name)
        return

    current = data["current"]
    wmo_code = current["weather_code"]
    description = _WMO_DESCRIPTIONS.get(wmo_code, f"código WMO {wmo_code}")

    reading = WeatherReading(
        city=city_name,
        country=country,
        temp_celsius=current["temperature_2m"],
        feels_like=current["apparent_temperature"],
        temp_min=current["temperature_2m"],
        temp_max=current["temperature_2m"],
        humidity_pct=current["relative_humidity_2m"],
        pressure_hpa=int(current["surface_pressure"]),
        wind_speed_ms=round(current["wind_speed_10m"] / 3.6, 2),  # km/h → m/s
        wind_deg=current["wind_direction_10m"],
        cloudiness_pct=current["cloud_cover"],
        description=description,
        icon=str(wmo_code),
        dt=datetime.fromisoformat(current["time"]).replace(tzinfo=timezone.utc),
        fetched_at=datetime.now(tz=timezone.utc),
        source="openmeteo",
    )

    db = SessionLocal()
    try:
        db.add(reading)
        db.commit()
        logger.info(
            "Open-Meteo — leitura salva: %s/%s — %.1f°C, umidade %d%%",
            reading.city,
            reading.country,
            reading.temp_celsius,
            reading.humidity_pct,
        )
    except Exception as exc:
        db.rollback()
        logger.error("Erro ao salvar leitura Open-Meteo de '%s': %s", city_name, exc)
    finally:
        db.close()


def fetch_all_openmeteo() -> None:
    cities = [c.strip() for c in settings.cities.split(";") if c.strip()]
    coords = [c.strip() for c in settings.cities_coords.split(";") if c.strip()]

    for city_entry, coord_entry in zip(cities, coords):
        parts = city_entry.split(",")
        city_name = parts[0].strip()
        country = parts[1].strip() if len(parts) > 1 else "BR"

        lat_str, lon_str = coord_entry.split(",")
        _fetch_coords(city_name, country, float(lat_str), float(lon_str))
