import logging
from contextlib import asynccontextmanager

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI

from app.config import settings
from app.routers.readings import router as readings_router
from app.routers.sources import router as sources_router
from app.services.fetcher import fetch_all_cities
from app.services.openmeteo import fetch_all_openmeteo

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    def fetch_all_sources() -> None:
        fetch_all_cities()
        fetch_all_openmeteo()

    scheduler.add_job(
        fetch_all_sources,
        "interval",
        minutes=settings.fetch_interval_minutes,
        id="weather_fetch",
    )
    scheduler.start()
    fetch_all_cities()
    fetch_all_openmeteo()
    yield
    scheduler.shutdown(wait=False)


def create_app() -> FastAPI:
    docs_url = "/docs" if settings.env != "production" else None
    redoc_url = "/redoc" if settings.env != "production" else None

    application = FastAPI(
        title="GnTech Weather API",
        description=(
            "Pipeline de dados climáticos: coleta automática da OpenWeather API, "
            "armazenamento em PostgreSQL e consulta via REST."
        ),
        version="1.0.0",
        lifespan=lifespan,
        docs_url=docs_url,
        redoc_url=redoc_url,
    )
    return application


app = create_app()

app.include_router(readings_router)
app.include_router(sources_router)


@app.get("/health", tags=["health"], summary="Healthcheck do serviço")
def health():
    return {"status": "ok"}
