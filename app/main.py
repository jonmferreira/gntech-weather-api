from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


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


@app.get("/health", tags=["health"], summary="Healthcheck do serviço")
def health():
    return {"status": "ok"}
