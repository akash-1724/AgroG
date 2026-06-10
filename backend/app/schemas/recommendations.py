import uuid
from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class CropRecommendationCreate(BaseModel):
    nitrogen: float = Field(..., description="Soil Nitrogen level (N)")
    phosphorus: float = Field(..., description="Soil Phosphorus level (P)")
    potassium: float = Field(..., description="Soil Potassium level (K)")
    ph: float = Field(..., description="Soil pH level")
    temperature: float = Field(..., description="Local Temperature in Celsius")
    humidity: float = Field(..., description="Local relative Humidity percentage")
    rainfall: float = Field(..., description="Average Rainfall in mm")

class CropRecommendationResponse(BaseModel):
    id: uuid.UUID
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    temperature: float
    humidity: float
    rainfall: float
    recommended_crops: List[str]
    created_at: datetime

    class Config:
        from_attributes = True

class FertilizerRecommendationCreate(BaseModel):
    nitrogen: float = Field(..., description="Soil Nitrogen level (N)")
    phosphorus: float = Field(..., description="Soil Phosphorus level (P)")
    potassium: float = Field(..., description="Soil Potassium level (K)")
    crop_type: str = Field(..., description="Target crop type")

class FertilizerRecommendationResponse(BaseModel):
    id: uuid.UUID
    nitrogen: float
    phosphorus: float
    potassium: float
    crop_type: str
    recommended_fertilizer: str
    created_at: datetime

    class Config:
        from_attributes = True

class DiseaseDetectionResponse(BaseModel):
    id: uuid.UUID
    image_url: str
    predicted_disease: str
    confidence: float
    remedy: str
    created_at: datetime

    class Config:
        from_attributes = True
