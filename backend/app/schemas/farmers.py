import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from pydantic import ConfigDict

class FarmerLocationUpdate(BaseModel):
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    address: str = Field(..., min_length=5, max_length=500)
    district: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    location_visibility: bool = True

class NearbyFarmerResponse(BaseModel):
    farmer_id: uuid.UUID
    full_name: str
    farm_name: Optional[str]
    latitude: float  # Rounded/blurred
    longitude: float # Rounded/blurred
    address: str
    district: Optional[str]
    city: Optional[str]
    state: Optional[str]
    distance_km: float
    rating: float

    class Config:
        from_attributes = True


class FarmerProfileUpdate(BaseModel):
    farm_name: Optional[str] = Field(None, max_length=255)
    address: Optional[str] = Field(None, min_length=5, max_length=500)
    district: Optional[str] = Field(None, max_length=100)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    location_visibility: Optional[bool] = None


class PublicListingSummary(BaseModel):
    id: uuid.UUID
    title: str
    description: str
    price_per_unit: float
    unit: str
    available_quantity: int
    image_urls: Optional[str] = None
    category: str
    status: str


class PublicReviewSummary(BaseModel):
    id: uuid.UUID
    rating: int
    comment: str
    reviewer_name: Optional[str] = None
    created_at: datetime


class PublicFarmerProfileResponse(BaseModel):
    farmer_id: uuid.UUID
    full_name: str
    farm_name: Optional[str]
    address: Optional[str]
    district: Optional[str]
    city: Optional[str]
    state: Optional[str]
    description: Optional[str]
    average_rating: Optional[float] = None
    review_count: int = 0
    active_listings: List[PublicListingSummary] = Field(default_factory=list)
    recent_reviews: List[PublicReviewSummary] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
