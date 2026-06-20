import uuid
from datetime import date, datetime
from typing import Any, Optional

from pydantic import BaseModel, Field

from app.schemas.recommendations import CropRecommendationCreate


class WeatherData(BaseModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    precipitation: Optional[float] = None
    rainfall: Optional[float] = None
    forecast_window: str = "current"
    latitude: float
    longitude: float
    timestamp: Optional[datetime] = None
    provider: str
    provider_status: str


class WeatherResponse(BaseModel):
    available: bool
    weather: Optional[WeatherData] = None
    provider: str
    provider_status: str
    warning: Optional[str] = None


class WeatherAwareCropRecommendationCreate(CropRecommendationCreate):
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    use_profile_location: bool = True


class WeatherAwareCropRecommendationResponse(BaseModel):
    id: uuid.UUID
    nitrogen: float
    phosphorus: float
    potassium: float
    ph: float
    temperature: float
    humidity: float
    rainfall: float
    recommended_crops: list[str]
    created_at: datetime
    model_status: Optional[str] = "demo"
    disclaimer: Optional[str] = None
    limitations: Optional[str] = None
    used_weather: bool
    weather: Optional[WeatherData] = None
    weather_warning: Optional[str] = None
    provider_status: Optional[str] = None


class CropPriceRecordResponse(BaseModel):
    id: uuid.UUID
    crop_name: str
    market: str
    district: Optional[str] = None
    state: str
    min_price: float
    max_price: float
    modal_price: float
    unit: str
    recorded_date: date
    source: str
    is_sample: bool

    class Config:
        from_attributes = True


class CropPriceCatalogItem(BaseModel):
    crop_name: str
    latest_recorded_date: Optional[date] = None
    markets: list[str] = []
    states: list[str] = []
    is_sample: bool
    source: str


class CropPriceCatalogResponse(BaseModel):
    crops: list[CropPriceCatalogItem]
    provider_status: str
    disclaimer: Optional[str] = None


class CropPriceTrendResponse(BaseModel):
    crop_name: Optional[str]
    records: list[CropPriceRecordResponse]
    provider_status: str
    is_sample: bool
    disclaimer: Optional[str] = None


class RecommendationHistoryListItem(BaseModel):
    id: uuid.UUID
    recommendation_type: str
    model_status: Optional[str] = None
    used_weather: bool
    created_at: datetime

    class Config:
        from_attributes = True


class RecommendationHistoryDetail(RecommendationHistoryListItem):
    input_payload: dict[str, Any]
    result_payload: dict[str, Any]

    class Config:
        from_attributes = True
