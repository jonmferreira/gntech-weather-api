import os

# Variáveis mínimas para o pydantic-settings carregar sem .env real
os.environ.setdefault("OPENWEATHER_API_KEY", "test-key")
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("POSTGRES_USER", "test")
os.environ.setdefault("POSTGRES_PASSWORD", "test")
os.environ.setdefault("POSTGRES_DB", "test")
os.environ.setdefault("ENV", "development")
