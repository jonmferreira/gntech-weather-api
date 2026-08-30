"""create weather_readings

Revision ID: 001
Revises:
Create Date: 2026-08-29
"""

from alembic import op
import sqlalchemy as sa

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "weather_readings",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("country", sa.String(10), nullable=False),
        sa.Column("temp_celsius", sa.Float(), nullable=False),
        sa.Column("feels_like", sa.Float(), nullable=False),
        sa.Column("temp_min", sa.Float(), nullable=False),
        sa.Column("temp_max", sa.Float(), nullable=False),
        sa.Column("humidity_pct", sa.Integer(), nullable=False),
        sa.Column("pressure_hpa", sa.Integer(), nullable=False),
        sa.Column("wind_speed_ms", sa.Float(), nullable=False),
        sa.Column("wind_deg", sa.Integer(), nullable=False),
        sa.Column("cloudiness_pct", sa.Integer(), nullable=False),
        sa.Column("description", sa.String(200), nullable=False),
        sa.Column("icon", sa.String(20), nullable=False),
        sa.Column("dt", sa.DateTime(timezone=True), nullable=False),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_weather_readings_city", "weather_readings", ["city"])


def downgrade() -> None:
    op.drop_index("ix_weather_readings_city", table_name="weather_readings")
    op.drop_table("weather_readings")
