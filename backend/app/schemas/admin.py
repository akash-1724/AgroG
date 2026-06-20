from datetime import date
from typing import Optional

from pydantic import BaseModel


class TimeBucket(BaseModel):
    date: date
    count: int


class UserAnalytics(BaseModel):
    total: int = 0
    by_role: dict[str, int] = {}
    new_over_time: list[TimeBucket] = []


class ListingAnalytics(BaseModel):
    total: int = 0
    by_status: dict[str, int] = {}
    by_category: dict[str, int] = {}


class OrderAnalytics(BaseModel):
    total: int = 0
    by_status: dict[str, int] = {}
    gross_value: float = 0.0
    average_value: float = 0.0


class AdvisoryAnalytics(BaseModel):
    crop_recommendations: int = 0
    fertilizer_recommendations: int = 0
    disease_detections: int = 0
    recommendation_history: int = 0


class ContentAnalytics(BaseModel):
    educational_resources: int = 0


class TrustAnalytics(BaseModel):
    reviews: int = 0
    average_rating: Optional[float] = None


class AdminAnalyticsOverview(BaseModel):
    users: UserAnalytics
    listings: ListingAnalytics
    orders: OrderAnalytics
    advisory: AdvisoryAnalytics
    content: ContentAnalytics
    trust: TrustAnalytics
