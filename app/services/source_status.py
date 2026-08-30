from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class SourceStatus:
    source: str
    is_healthy: bool = False
    last_attempt: Optional[datetime] = None
    last_success: Optional[datetime] = None
    last_error: Optional[str] = None


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
