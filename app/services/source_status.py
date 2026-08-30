from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass
class SourceStatus:
    source: str
    is_healthy: bool = False
    last_attempt: datetime | None = None
    last_success: datetime | None = None
    last_error: str | None = None


_registry: dict[str, SourceStatus] = {
    "openweather": SourceStatus(source="openweather"),
    "openmeteo": SourceStatus(source="openmeteo"),
}


def mark_success(source: str) -> None:
    now = datetime.now(tz=timezone.utc)
    _registry[source].last_attempt = now
    _registry[source].last_success = now
    _registry[source].last_error = None
    _registry[source].is_healthy = True


def mark_failure(source: str, error: str) -> None:
    now = datetime.now(tz=timezone.utc)
    _registry[source].last_attempt = now
    _registry[source].last_error = error
    _registry[source].is_healthy = False


def get_all() -> list[SourceStatus]:
    return list(_registry.values())
