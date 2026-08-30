from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Float, func
from sqlalchemy.orm import Session

from app.db import get_db
from app.models import WeatherReading
from app.schemas import CityStatsOut, SourceReadingOut, WeatherReadingOut
from app.services import source_status as ss

router = APIRouter(prefix="/readings", tags=["readings"])


@router.get(
    "",
    response_model=list[WeatherReadingOut],
    summary="Lista leituras climáticas",
    description="Retorna leituras armazenadas com filtros opcionais por cidade, período e fonte.",
)
def list_readings(
    city: Optional[str] = Query(None, max_length=100, description="Nome da cidade (ex: Florianopolis)"),
    from_dt: Optional[datetime] = Query(None, description="Data/hora inicial (UTC) — ex: 2026-08-01T00:00:00"),
    to_dt: Optional[datetime] = Query(None, description="Data/hora final (UTC) — ex: 2026-08-31T23:59:59"),
    limit: int = Query(100, ge=1, le=500, description="Máximo de resultados (1–500)"),
    source: Optional[List[str]] = Query(None, description="Fontes de dados (openweather, openmeteo). Sem filtro retorna todas."),
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
    response_model=list[SourceReadingOut],
    summary="Última leitura por fonte de dados",
    description=(
        "Retorna a leitura mais recente de cada fonte de dados integrada. "
        "Para cada fonte informa se está saudável e o último erro, caso tenha falhado. "
        "Fontes com falha aparecem com `data: null` e `error` preenchido — "
        "as fontes que funcionaram retornam os dados normalmente."
    ),
)
def latest_readings(
    city: Optional[str] = Query(None, max_length=100, description="Nome da cidade (ex: Florianopolis)"),
    db: Session = Depends(get_db),
):
    statuses = {s.source: s for s in ss.get_all()}

    result = []
    for source_name, status in statuses.items():
        query = db.query(WeatherReading).filter(WeatherReading.source == source_name)
        if city:
            query = query.filter(WeatherReading.city.ilike(f"%{city}%"))

        latest = query.order_by(WeatherReading.fetched_at.desc()).first()

        result.append(
            SourceReadingOut(
                source=source_name,
                is_healthy=status.is_healthy,
                last_success=status.last_success,
                error=status.last_error,
                data=WeatherReadingOut.model_validate(latest) if latest else None,
            )
        )

    return result


@router.get(
    "/stats",
    response_model=list[CityStatsOut],
    summary="Estatísticas por cidade",
    description="Retorna média, máxima e mínima de temperatura, umidade e vento "
                "agrupadas por cidade. Suporta filtro por período e fonte.",
)
def stats(
    city: Optional[str] = Query(None, max_length=100, description="Nome da cidade (ex: Florianopolis)"),
    from_dt: Optional[datetime] = Query(None, description="Data/hora inicial (UTC)"),
    to_dt: Optional[datetime] = Query(None, description="Data/hora final (UTC)"),
    source: Optional[List[str]] = Query(None, description="Fontes de dados (openweather, openmeteo). Sem filtro retorna todas."),
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
