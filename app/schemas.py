from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class WeatherReadingOut(BaseModel):
    id: int
    city: str
    country: str
    temp_celsius: float = Field(..., description="Temperatura atual em °C")
    feels_like: float = Field(..., description="Sensação térmica em °C")
    temp_min: float = Field(..., description="Temperatura mínima registrada em °C")
    temp_max: float = Field(..., description="Temperatura máxima registrada em °C")
    humidity_pct: int = Field(..., description="Umidade relativa do ar em %")
    pressure_hpa: int = Field(..., description="Pressão atmosférica em hPa")
    wind_speed_ms: float = Field(..., description="Velocidade do vento em m/s")
    wind_deg: int = Field(..., description="Direção do vento em graus")
    cloudiness_pct: int = Field(..., description="Cobertura de nuvens em %")
    description: str = Field(..., description="Descrição do clima em português")
    icon: str = Field(..., description="Código do ícone OpenWeather")
    dt: datetime = Field(..., description="Timestamp do dado na fonte (UTC)")
    fetched_at: datetime = Field(..., description="Timestamp da coleta pela aplicação (UTC)")
    source: str = Field(..., description="Fonte dos dados: openweather | openmeteo")

    model_config = {"from_attributes": True}


class SourceStatusOut(BaseModel):
    source: str = Field(..., description="Nome da fonte de dados")
    is_healthy: bool = Field(..., description="True se a última coleta foi bem-sucedida")
    last_attempt: Optional[datetime] = Field(None, description="Última tentativa de coleta (UTC)")
    last_success: Optional[datetime] = Field(None, description="Última coleta bem-sucedida (UTC)")
    last_error: Optional[str] = Field(None, description="Mensagem do último erro, se houver")


class CityStatsOut(BaseModel):
    city: str
    country: str
    avg_temp: float = Field(..., description="Temperatura média em °C")
    max_temp: float = Field(..., description="Temperatura máxima registrada em °C")
    min_temp: float = Field(..., description="Temperatura mínima registrada em °C")
    avg_humidity: float = Field(..., description="Umidade média em %")
    avg_wind_speed: float = Field(..., description="Velocidade média do vento em m/s")
    total_readings: int = Field(..., description="Total de leituras no período")
