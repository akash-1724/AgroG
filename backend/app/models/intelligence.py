import uuid
from datetime import date, datetime
from typing import Optional

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PriceSource(Base):
    __tablename__ = "price_sources"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    provider_type: Mapped[str] = mapped_column(String(50), default="sample", nullable=False)
    is_live: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    price_records: Mapped[list["CropPriceRecord"]] = relationship("CropPriceRecord", back_populates="price_source")


class CropPriceRecord(Base):
    __tablename__ = "crop_price_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    crop_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    market: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    district: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    state: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    min_price: Mapped[float] = mapped_column(Float, nullable=False)
    max_price: Mapped[float] = mapped_column(Float, nullable=False)
    modal_price: Mapped[float] = mapped_column(Float, nullable=False)
    unit: Mapped[str] = mapped_column(String(50), default="quintal", nullable=False)
    recorded_date: Mapped[date] = mapped_column(Date, index=True, nullable=False)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    is_sample: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("price_sources.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    price_source: Mapped[Optional[PriceSource]] = relationship("PriceSource", back_populates="price_records")


class CropPriceImportLog(Base):
    __tablename__ = "crop_price_import_logs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    source: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    records_imported: Mapped[int] = mapped_column(default=0, nullable=False)
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)


class RecommendationHistory(Base):
    __tablename__ = "recommendation_history"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    recommendation_type: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    input_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    result_payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    model_status: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    used_weather: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="recommendation_history")
