"""add source to weather_readings

Revision ID: 002
Revises: 001
Create Date: 2026-08-30
"""

from alembic import op
import sqlalchemy as sa

revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "weather_readings",
        sa.Column("source", sa.String(50), nullable=False, server_default="openweather"),
    )
    op.create_index("ix_weather_readings_source", "weather_readings", ["source"])


def downgrade() -> None:
    op.drop_index("ix_weather_readings_source", table_name="weather_readings")
    op.drop_column("weather_readings", "source")
