from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import WeatherReading
from app.schemas import CityStatsOut, WeatherReadingOut

router = APIRouter(prefix="/readings", tags=["readings"])


@router.get(
    "",
    response_model=list[WeatherReadingOut],
    summary="Lista leituras climáticas",
    description="Retorna leituras armazenadas com filtros opcionais por cidade, período e fonte.",
)
def list_readings(
    city: str | None = Query(None, max_length=100, description="Nome da cidade (ex: Florianopolis)"),
    from_dt: datetime | None = Query(None, description="Data/hora inicial (UTC) — ex: 2026-08-01T00:00:00"),
    to_dt: datetime | None = Query(None, description="Data/hora final (UTC) — ex: 2026-08-31T23:59:59"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de resultados (1–500)"),
    source: list[str] | None = Query(None, description="Fontes de dados (openweather, openmeteo). Sem filtro retorna todas."),
    db: Session = Depends(get_db),
):
    if from_dt and to_dt and from_dt > to_dt:
        raise HTTPException(status_code=422, detail="from_dt não pode ser maior que to_dt.")

    query = db.query(WeatherReading)

    if city:
        query = query.filter(WeatherReading.city.ilike(f"%{city}%"))
    if from_dt:
        query = query.filter(WeatherReading.fetched_at >= from_dt)
    if to_dt:
        query = query.filter(WeatherReading.fetched_at <= to_dt)
    if source:
        query = query.filter(WeatherReading.source.in_(source))

    return query.order_by(WeatherReading.fetched_at.desc()).limit(limit).all()


@router.get(
    "/latest",
    response_model=list[WeatherReadingOut],
    summary="Última leitura por fonte",
    description=(
        "Retorna a leitura mais recente de cada fonte integrada. "
        "O campo `source` identifica a origem do dado. "
        "Para verificar a saúde de cada fonte use `GET /sources/status`."
    ),
)
def latest_readings(
    city: str | None = Query(None, max_length=100, description="Nome da cidade (ex: Florianopolis)"),
    db: Session = Depends(get_db),
):
    subq = (
        db.query(
            WeatherReading.source,
            func.max(WeatherReading.fetched_at).label("max_fetched_at"),
        )
        .group_by(WeatherReading.source)
        .subquery()
    )

    query = db.query(WeatherReading).join(
        subq,
        (WeatherReading.source == subq.c.source)
        & (WeatherReading.fetched_at == subq.c.max_fetched_at),
    )

    if city:
        query = query.filter(WeatherReading.city.ilike(f"%{city}%"))

    results = query.all()

    if not results:
        raise HTTPException(status_code=404, detail="Nenhuma leitura encontrada.")

    return results


@router.get(
    "/stats",
    response_model=list[CityStatsOut],
    summary="Estatísticas por cidade",
    description="Retorna média, máxima e mínima de temperatura, umidade e vento "
                "agrupadas por cidade. Suporta filtro por período e fonte.",
)
def stats(
    city: str | None = Query(None, max_length=100, description="Nome da cidade (ex: Florianopolis)"),
    from_dt: datetime | None = Query(None, description="Data/hora inicial (UTC)"),
    to_dt: datetime | None = Query(None, description="Data/hora final (UTC)"),
    source: list[str] | None = Query(None, description="Fontes de dados (openweather, openmeteo). Sem filtro retorna todas."),
    db: Session = Depends(get_db),
):
    if from_dt and to_dt and from_dt > to_dt:
        raise HTTPException(status_code=422, detail="from_dt não pode ser maior que to_dt.")

    query = db.query(
        WeatherReading.city,
        WeatherReading.country,
        func.avg(WeatherReading.temp_celsius).label("avg_temp"),
        func.max(WeatherReading.temp_celsius).label("max_temp"),
        func.min(WeatherReading.temp_celsius).label("min_temp"),
        func.avg(WeatherReading.humidity_pct).label("avg_humidity"),
        func.avg(WeatherReading.wind_speed_ms).label("avg_wind_speed"),
        func.count(WeatherReading.id).label("total_readings"),
    ).group_by(WeatherReading.city, WeatherReading.country)

    if city:
        query = query.filter(WeatherReading.city.ilike(f"%{city}%"))
    if from_dt:
        query = query.filter(WeatherReading.fetched_at >= from_dt)
    if to_dt:
        query = query.filter(WeatherReading.fetched_at <= to_dt)
    if source:
        query = query.filter(WeatherReading.source.in_(source))

    rows = query.all()

    if not rows:
        raise HTTPException(status_code=404, detail="Nenhuma leitura encontrada para os filtros informados.")

    return [
        CityStatsOut(
            city=r.city,
            country=r.country,
            avg_temp=round(r.avg_temp, 2),
            max_temp=round(r.max_temp, 2),
            min_temp=round(r.min_temp, 2),
            avg_humidity=round(r.avg_humidity, 2),
            avg_wind_speed=round(r.avg_wind_speed, 2),
            total_readings=r.total_readings,
        )
        for r in rows
    ]
