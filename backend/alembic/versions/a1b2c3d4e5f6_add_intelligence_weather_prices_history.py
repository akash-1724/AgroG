"""add_intelligence_weather_prices_history

Revision ID: a1b2c3d4e5f6
Revises: 9c4d5e6f7a81
Create Date: 2026-06-19 00:00:00.000000

"""
from typing import Sequence, Union
import uuid
from datetime import date, datetime

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "9c4d5e6f7a81"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "price_sources",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("provider_type", sa.String(length=50), nullable=False),
        sa.Column("is_live", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "crop_price_import_logs",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("records_imported", sa.Integer(), nullable=False),
        sa.Column("message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "crop_price_records",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("crop_name", sa.String(length=255), nullable=False),
        sa.Column("market", sa.String(length=255), nullable=False),
        sa.Column("district", sa.String(length=255), nullable=True),
        sa.Column("state", sa.String(length=255), nullable=False),
        sa.Column("min_price", sa.Float(), nullable=False),
        sa.Column("max_price", sa.Float(), nullable=False),
        sa.Column("modal_price", sa.Float(), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("recorded_date", sa.Date(), nullable=False),
        sa.Column("source", sa.String(length=255), nullable=False),
        sa.Column("is_sample", sa.Boolean(), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["source_id"], ["price_sources.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_crop_price_records_crop_name"), "crop_price_records", ["crop_name"], unique=False)
    op.create_index(op.f("ix_crop_price_records_market"), "crop_price_records", ["market"], unique=False)
    op.create_index(op.f("ix_crop_price_records_recorded_date"), "crop_price_records", ["recorded_date"], unique=False)
    op.create_index(op.f("ix_crop_price_records_state"), "crop_price_records", ["state"], unique=False)
    op.create_index("ix_crop_price_records_crop_date", "crop_price_records", ["crop_name", "recorded_date"], unique=False)

    op.create_table(
        "recommendation_history",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("recommendation_type", sa.String(length=50), nullable=False),
        sa.Column("input_payload", sa.JSON(), nullable=False),
        sa.Column("result_payload", sa.JSON(), nullable=False),
        sa.Column("model_status", sa.String(length=100), nullable=True),
        sa.Column("used_weather", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_recommendation_history_created_at"), "recommendation_history", ["created_at"], unique=False)
    op.create_index(op.f("ix_recommendation_history_recommendation_type"), "recommendation_history", ["recommendation_type"], unique=False)
    op.create_index(op.f("ix_recommendation_history_user_id"), "recommendation_history", ["user_id"], unique=False)
    op.create_index("ix_recommendation_history_user_created", "recommendation_history", ["user_id", "created_at"], unique=False)

    sample_source_id = uuid.UUID("11111111-1111-4111-8111-111111111111")
    now = datetime.utcnow()
    op.bulk_insert(
        sa.table(
            "price_sources",
            sa.column("id", sa.Uuid()),
            sa.column("name", sa.String()),
            sa.column("description", sa.Text()),
            sa.column("provider_type", sa.String()),
            sa.column("is_live", sa.Boolean()),
            sa.column("created_at", sa.DateTime()),
        ),
        [
            {
                "id": sample_source_id,
                "name": "Sample Mandi Prices",
                "description": "Seeded demo data for development; not live market prices.",
                "provider_type": "sample",
                "is_live": False,
                "created_at": now,
            }
        ],
    )
    price_table = sa.table(
        "crop_price_records",
        sa.column("id", sa.Uuid()),
        sa.column("crop_name", sa.String()),
        sa.column("market", sa.String()),
        sa.column("district", sa.String()),
        sa.column("state", sa.String()),
        sa.column("min_price", sa.Float()),
        sa.column("max_price", sa.Float()),
        sa.column("modal_price", sa.Float()),
        sa.column("unit", sa.String()),
        sa.column("recorded_date", sa.Date()),
        sa.column("source", sa.String()),
        sa.column("is_sample", sa.Boolean()),
        sa.column("source_id", sa.Uuid()),
        sa.column("created_at", sa.DateTime()),
        sa.column("updated_at", sa.DateTime()),
    )
    op.bulk_insert(
        price_table,
        [
            {
                "id": uuid.UUID("22222222-2222-4222-8222-222222222201"),
                "crop_name": "Tomato",
                "market": "Bengaluru Mandi",
                "district": "Bengaluru Urban",
                "state": "Karnataka",
                "min_price": 900,
                "max_price": 1300,
                "modal_price": 1100,
                "unit": "quintal",
                "recorded_date": date(2026, 6, 17),
                "source": "Sample Mandi Prices",
                "is_sample": True,
                "source_id": sample_source_id,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": uuid.UUID("22222222-2222-4222-8222-222222222202"),
                "crop_name": "Tomato",
                "market": "Mysuru Mandi",
                "district": "Mysuru",
                "state": "Karnataka",
                "min_price": 850,
                "max_price": 1250,
                "modal_price": 1025,
                "unit": "quintal",
                "recorded_date": date(2026, 6, 18),
                "source": "Sample Mandi Prices",
                "is_sample": True,
                "source_id": sample_source_id,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": uuid.UUID("22222222-2222-4222-8222-222222222203"),
                "crop_name": "Wheat",
                "market": "Indore Mandi",
                "district": "Indore",
                "state": "Madhya Pradesh",
                "min_price": 2200,
                "max_price": 2480,
                "modal_price": 2350,
                "unit": "quintal",
                "recorded_date": date(2026, 6, 18),
                "source": "Sample Mandi Prices",
                "is_sample": True,
                "source_id": sample_source_id,
                "created_at": now,
                "updated_at": now,
            },
            {
                "id": uuid.UUID("22222222-2222-4222-8222-222222222204"),
                "crop_name": "Rice",
                "market": "Raichur Mandi",
                "district": "Raichur",
                "state": "Karnataka",
                "min_price": 1900,
                "max_price": 2300,
                "modal_price": 2100,
                "unit": "quintal",
                "recorded_date": date(2026, 6, 18),
                "source": "Sample Mandi Prices",
                "is_sample": True,
                "source_id": sample_source_id,
                "created_at": now,
                "updated_at": now,
            },
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_recommendation_history_user_created", table_name="recommendation_history")
    op.drop_index(op.f("ix_recommendation_history_user_id"), table_name="recommendation_history")
    op.drop_index(op.f("ix_recommendation_history_recommendation_type"), table_name="recommendation_history")
    op.drop_index(op.f("ix_recommendation_history_created_at"), table_name="recommendation_history")
    op.drop_table("recommendation_history")
    op.drop_index("ix_crop_price_records_crop_date", table_name="crop_price_records")
    op.drop_index(op.f("ix_crop_price_records_state"), table_name="crop_price_records")
    op.drop_index(op.f("ix_crop_price_records_recorded_date"), table_name="crop_price_records")
    op.drop_index(op.f("ix_crop_price_records_market"), table_name="crop_price_records")
    op.drop_index(op.f("ix_crop_price_records_crop_name"), table_name="crop_price_records")
    op.drop_table("crop_price_records")
    op.drop_table("crop_price_import_logs")
    op.drop_table("price_sources")
