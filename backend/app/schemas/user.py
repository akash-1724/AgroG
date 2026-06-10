import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

# Schema for Farmer Registration details
class FarmerProfileCreate(BaseModel):
    farm_name: str
    latitude: float
    longitude: float
    address: str
    description: Optional[str] = None

# Schema for User Registration
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str
    phone_number: Optional[str] = None
    role: str = "customer" # "customer", "farmer", "admin"
    farmer_details: Optional[FarmerProfileCreate] = None

# Schema for User Login
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# Schema for User Response
class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: str
    phone_number: Optional[str] = None
    role: str
    created_at: datetime

    class Config:
        from_attributes = True

# Schema for Token Response
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

# Schema for Google OAuth Token Login
class GoogleLogin(BaseModel):
    id_token: str

