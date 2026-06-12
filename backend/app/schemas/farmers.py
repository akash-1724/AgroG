import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field

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
