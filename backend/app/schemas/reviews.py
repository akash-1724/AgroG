import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RatingSummary(BaseModel):
    average_rating: Optional[float] = None
    review_count: int = 0


class ReviewCreate(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    comment: str = Field(..., min_length=3, max_length=2000)
    listing_id: uuid.UUID
    order_item_id: uuid.UUID
    target_type: str = Field("listing", pattern="^(listing|farmer)$")


class ReviewResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    farmer_id: uuid.UUID
    listing_id: Optional[uuid.UUID]
    order_id: Optional[uuid.UUID]
    order_item_id: Optional[uuid.UUID]
    rating: int
    comment: str
    target_type: str
    reviewer_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
