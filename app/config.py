from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    openweather_api_key: str
    database_url: str
    postgres_user: str = "weather"
    postgres_password: str = "weather"
    postgres_db: str = "weather_db"
    cities: str = "Florianopolis,BR"
    cities_coords: str = "-27.5954,-48.548"
    fetch_interval_minutes: int = 30
    env: str = "development"

    model_config = {"env_file": ".env"}


settings = Settings()  # type: ignore[call-arg]
