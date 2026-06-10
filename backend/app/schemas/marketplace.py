import uuid
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, condecimal

# Schema for creating a crop listing
class CropListingCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10, max_length=1000)
    price_per_unit: float = Field(..., gt=0)
    unit: str = Field(..., min_length=1, max_length=50) # e.g. "kg", "ton"
    available_quantity: int = Field(..., ge=0)
    image_urls: Optional[str] = Field(None, max_length=2000) # Cloudinary image URL links

# Schema for updating a crop listing
class CropListingUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=10, max_length=1000)
    price_per_unit: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = Field(None, min_length=1, max_length=50)
    available_quantity: Optional[int] = Field(None, ge=0)
    image_urls: Optional[str] = Field(None, max_length=2000)

# Schema for listing response
class CropListingResponse(BaseModel):
    id: uuid.UUID
    farmer_id: uuid.UUID
    title: str
    description: str
    price_per_unit: float
    unit: str
    available_quantity: int
    image_urls: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schema for creating an item in the cart/order
class OrderItemCreate(BaseModel):
    crop_listing_id: uuid.UUID
    quantity: int = Field(..., gt=0)

# Schema for creating an order
class OrderCreate(BaseModel):
    items: List[OrderItemCreate] = Field(..., min_length=1)

# Schema for response representing an order item line
class OrderItemResponse(BaseModel):
    id: uuid.UUID
    crop_listing_id: uuid.UUID
    quantity: int
    price_at_purchase: float

    class Config:
        from_attributes = True

# Schema for detailed order response
class OrderResponse(BaseModel):
    id: uuid.UUID
    customer_id: uuid.UUID
    status: str
    total_amount: float
    items: List[OrderItemResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Schema for updating order status
class OrderStatusUpdate(BaseModel):
    status: str = Field(..., description="Target status: pending, shipped, completed, cancelled")

