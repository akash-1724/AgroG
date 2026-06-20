"""add_admin_media_fulfillment

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b2c3d4e5f6a7"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "listing_images",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("listing_id", sa.Uuid(), nullable=False),
        sa.Column("image_url", sa.String(length=1000), nullable=False),
        sa.Column("public_id", sa.String(length=255), nullable=True),
        sa.Column("alt_text", sa.String(length=255), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["listing_id"], ["crop_listings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_listing_images_listing_id"), "listing_images", ["listing_id"], unique=False)

    op.add_column("order_items", sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"))
    op.add_column("order_items", sa.Column("status_updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.add_column("order_items", sa.Column("fulfilled_at", sa.DateTime(), nullable=True))
    op.create_index("ix_order_items_status", "order_items", ["status"], unique=False)
    op.create_index("ix_order_items_order_status", "order_items", ["order_id", "status"], unique=False)
    op.alter_column("order_items", "status", server_default=None)
    op.alter_column("order_items", "status_updated_at", server_default=None)


def downgrade() -> None:
    op.drop_index("ix_order_items_order_status", table_name="order_items")
    op.drop_index("ix_order_items_status", table_name="order_items")
    op.drop_column("order_items", "fulfilled_at")
    op.drop_column("order_items", "status_updated_at")
    op.drop_column("order_items", "status")
    op.drop_index(op.f("ix_listing_images_listing_id"), table_name="listing_images")
    op.drop_table("listing_images")
