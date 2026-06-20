"""add_cart_and_reviews

Revision ID: 9c4d5e6f7a81
Revises: 6b3a6fb5d5b3
Create Date: 2026-06-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9c4d5e6f7a81"
down_revision: Union[str, Sequence[str], None] = "6b3a6fb5d5b3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "carts",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("customer_id"),
    )
    op.create_index(op.f("ix_carts_customer_id"), "carts", ["customer_id"], unique=False)

    op.create_table(
        "cart_items",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("cart_id", sa.Uuid(), nullable=False),
        sa.Column("crop_listing_id", sa.Uuid(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["cart_id"], ["carts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["crop_listing_id"], ["crop_listings.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cart_id", "crop_listing_id", name="uq_cart_listing"),
    )
    op.create_index(op.f("ix_cart_items_cart_id"), "cart_items", ["cart_id"], unique=False)
    op.create_index(op.f("ix_cart_items_crop_listing_id"), "cart_items", ["crop_listing_id"], unique=False)

    op.create_table(
        "reviews",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("customer_id", sa.Uuid(), nullable=False),
        sa.Column("farmer_id", sa.Uuid(), nullable=False),
        sa.Column("listing_id", sa.Uuid(), nullable=True),
        sa.Column("order_id", sa.Uuid(), nullable=True),
        sa.Column("order_item_id", sa.Uuid(), nullable=True),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False),
        sa.Column("target_type", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("rating >= 1 AND rating <= 5", name="ck_reviews_rating_range"),
        sa.ForeignKeyConstraint(["customer_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["farmer_id"], ["farmer_profiles.user_id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["listing_id"], ["crop_listings.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["order_item_id"], ["order_items.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("customer_id", "order_item_id", "listing_id", name="uq_review_customer_order_item_listing"),
    )
    op.create_index(op.f("ix_reviews_customer_id"), "reviews", ["customer_id"], unique=False)
    op.create_index(op.f("ix_reviews_farmer_id"), "reviews", ["farmer_id"], unique=False)
    op.create_index(op.f("ix_reviews_listing_id"), "reviews", ["listing_id"], unique=False)
    op.create_index(op.f("ix_reviews_order_id"), "reviews", ["order_id"], unique=False)
    op.create_index(op.f("ix_reviews_order_item_id"), "reviews", ["order_item_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_reviews_order_item_id"), table_name="reviews")
    op.drop_index(op.f("ix_reviews_order_id"), table_name="reviews")
    op.drop_index(op.f("ix_reviews_listing_id"), table_name="reviews")
    op.drop_index(op.f("ix_reviews_farmer_id"), table_name="reviews")
    op.drop_index(op.f("ix_reviews_customer_id"), table_name="reviews")
    op.drop_table("reviews")
    op.drop_index(op.f("ix_cart_items_crop_listing_id"), table_name="cart_items")
    op.drop_index(op.f("ix_cart_items_cart_id"), table_name="cart_items")
    op.drop_table("cart_items")
    op.drop_index(op.f("ix_carts_customer_id"), table_name="carts")
    op.drop_table("carts")
