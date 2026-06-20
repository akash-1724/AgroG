import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy import Boolean, String, DateTime, ForeignKey, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class CropListing(Base):
    __tablename__ = "crop_listings"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    farmer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("farmer_profiles.user_id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(String(1000), nullable=False)
    price_per_unit: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    unit: Mapped[str] = mapped_column(String(50), nullable=False) # kg, ton, quintal, etc.
    available_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    image_urls: Mapped[str] = mapped_column(String(2000), nullable=True) # comma-separated list of Cloudinary URLs
    status: Mapped[str] = mapped_column(String(50), default="active", nullable=False) # active, inactive, sold_out
    category: Mapped[str] = mapped_column(String(100), default="Vegetables", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    farmer: Mapped["FarmerProfile"] = relationship("FarmerProfile", back_populates="crop_listings")
    order_items: Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="crop_listing")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="listing")
    images: Mapped[List["ListingImage"]] = relationship(
        "ListingImage", back_populates="listing", cascade="all, delete-orphan"
    )


class ListingImage(Base):
    __tablename__ = "listing_images"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    listing_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("crop_listings.id", ondelete="CASCADE"), index=True, nullable=False
    )
    image_url: Mapped[str] = mapped_column(String(1000), nullable=False)
    public_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    alt_text: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    listing: Mapped["CropListing"] = relationship("CropListing", back_populates="images")

class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False) # pending, shipped, completed, cancelled
    total_amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    customer: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )

class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    crop_listing_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("crop_listings.id", ondelete="RESTRICT"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    price_at_purchase: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)
    status_updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    fulfilled_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    crop_listing: Mapped["CropListing"] = relationship("CropListing", back_populates="order_items")
