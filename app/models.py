from datetime import datetime
from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db import Base


class WeatherReading(Base):
    __tablename__ = "weather_readings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    city: Mapped[str] = mapped_column(String(100), index=True)
    country: Mapped[str] = mapped_column(String(10))
    temp_celsius: Mapped[float] = mapped_column(Float)
    feels_like: Mapped[float] = mapped_column(Float)
    temp_min: Mapped[float] = mapped_column(Float)
    temp_max: Mapped[float] = mapped_column(Float)
    humidity_pct: Mapped[int] = mapped_column(Integer)
    pressure_hpa: Mapped[int] = mapped_column(Integer)
    wind_speed_ms: Mapped[float] = mapped_column(Float)
    wind_deg: Mapped[int] = mapped_column(Integer)
    cloudiness_pct: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(String(200))
    icon: Mapped[str] = mapped_column(String(20))
    dt: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    source: Mapped[str] = mapped_column(String(50), index=True, default="openweather")
