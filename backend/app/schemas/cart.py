import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.marketplace import OrderResponse


class CartItemCreate(BaseModel):
    crop_listing_id: uuid.UUID
    quantity: int = Field(..., gt=0)


class CartItemUpdate(BaseModel):
    quantity: int = Field(..., gt=0)


class CartItemResponse(BaseModel):
    id: uuid.UUID
    crop_listing_id: uuid.UUID
    title: str
    farmer_id: uuid.UUID
    farmer_name: str
    unit_price: float
    unit: str
    quantity: int
    available_quantity: int
    status: str
    image_urls: Optional[str] = None
    subtotal: float


class CartResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    items: List[CartItemResponse]
    estimated_total: float
    created_at: datetime
    updated_at: datetime


class CartCheckoutResponse(BaseModel):
    order: OrderResponse
    cart_cleared: bool = True
