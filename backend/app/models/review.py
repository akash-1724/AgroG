import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Review(Base):
    __tablename__ = "reviews"
    __table_args__ = (
        CheckConstraint("rating >= 1 AND rating <= 5", name="ck_reviews_rating_range"),
        UniqueConstraint("customer_id", "order_item_id", "listing_id", name="uq_review_customer_order_item_listing"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    farmer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("farmer_profiles.user_id", ondelete="CASCADE"), nullable=False, index=True)
    listing_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("crop_listings.id", ondelete="SET NULL"), nullable=True, index=True)
    order_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("orders.id", ondelete="SET NULL"), nullable=True, index=True)
    order_item_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("order_items.id", ondelete="SET NULL"), nullable=True, index=True)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    target_type: Mapped[str] = mapped_column(String(20), default="listing", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    customer: Mapped["User"] = relationship("User", back_populates="reviews")
    farmer: Mapped["FarmerProfile"] = relationship("FarmerProfile", back_populates="reviews")
    listing: Mapped[Optional["CropListing"]] = relationship("CropListing", back_populates="reviews")
    order: Mapped[Optional["Order"]] = relationship("Order")
    order_item: Mapped[Optional["OrderItem"]] = relationship("OrderItem")
