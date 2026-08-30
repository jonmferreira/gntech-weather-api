import os
from unittest.mock import patch

os.environ.setdefault("OPENWEATHER_API_KEY", "test-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test.db")
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("ENV", "development")

from app.db import Base, engine  # noqa: E402
import app.models  # noqa: F401, E402 — registra WeatherReading na metadata antes do create_all

Base.metadata.create_all(bind=engine)

patch("app.main.fetch_all_cities", return_value=None).start()
patch("app.main.fetch_all_openmeteo", return_value=None).start()
