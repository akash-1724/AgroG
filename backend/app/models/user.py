import uuid
from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, ForeignKey, Double, Float, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone_number: Mapped[str] = mapped_column(String(50), nullable=True)
    role: Mapped[str] = mapped_column(String(50), default="customer", nullable=False) # farmer, customer, admin
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    farmer_profile: Mapped[Optional["FarmerProfile"]] = relationship(
        "FarmerProfile", back_populates="user", uselist=False, cascade="all, delete-orphan"
    )
    orders: Mapped[List["Order"]] = relationship("Order", back_populates="customer")
    crop_recommendations: Mapped[List["CropRecommendationRecord"]] = relationship("CropRecommendationRecord", back_populates="user")
    fertilizer_recommendations: Mapped[List["FertilizerRecommendationRecord"]] = relationship("FertilizerRecommendationRecord", back_populates="user")
    disease_detections: Mapped[List["DiseaseDetectionRecord"]] = relationship("DiseaseDetectionRecord", back_populates="user")
    articles: Mapped[List["EducationalArticle"]] = relationship("EducationalArticle", back_populates="author")
    refresh_tokens: Mapped[List["RefreshToken"]] = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    cart: Mapped[Optional["Cart"]] = relationship("Cart", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="customer", cascade="all, delete-orphan")
    recommendation_history: Mapped[List["RecommendationHistory"]] = relationship(
        "RecommendationHistory", back_populates="user", cascade="all, delete-orphan"
    )

class FarmerProfile(Base):
    __tablename__ = "farmer_profiles"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    farm_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    latitude: Mapped[Optional[float]] = mapped_column(Double, nullable=True)
    longitude: Mapped[Optional[float]] = mapped_column(Double, nullable=True)
    address: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    district: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location_visibility: Mapped[bool] = mapped_column(default=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    rating: Mapped[float] = mapped_column(Float, default=5.0, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="farmer_profile")
    crop_listings: Mapped[List["CropListing"]] = relationship(
        "CropListing", back_populates="farmer", cascade="all, delete-orphan"
    )
    reviews: Mapped[List["Review"]] = relationship("Review", back_populates="farmer", cascade="all, delete-orphan")
