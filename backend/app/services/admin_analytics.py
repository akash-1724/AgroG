from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.educational import EducationalArticle
from app.models.intelligence import RecommendationHistory
from app.models.marketplace import CropListing, Order
from app.models.recommendations import CropRecommendationRecord, DiseaseDetectionRecord, FertilizerRecommendationRecord
from app.models.review import Review
from app.models.user import User
from app.schemas.admin import (
    AdminAnalyticsOverview,
    AdvisoryAnalytics,
    ContentAnalytics,
    ListingAnalytics,
    OrderAnalytics,
    TimeBucket,
    TrustAnalytics,
    UserAnalytics,
)


async def _count_by(db: AsyncSession, model, column) -> dict[str, int]:
    result = await db.execute(select(column, func.count(model.id)).group_by(column))
    return {str(key or "unknown"): int(count or 0) for key, count in result.all()}


async def _scalar_count(db: AsyncSession, model) -> int:
    result = await db.execute(select(func.count(model.id)))
    return int(result.scalar() or 0)


async def get_admin_analytics_overview(db: AsyncSession) -> AdminAnalyticsOverview:
    total_users = await _scalar_count(db, User)
    users_by_role = await _count_by(db, User, User.role)
    user_buckets_result = await db.execute(
        select(func.date(User.created_at), func.count(User.id)).group_by(func.date(User.created_at)).order_by(func.date(User.created_at).asc())
    )
    new_users = [TimeBucket(date=date.fromisoformat(str(bucket)), count=int(count or 0)) for bucket, count in user_buckets_result.all()]

    total_orders_result = await db.execute(select(func.count(Order.id), func.coalesce(func.sum(Order.total_amount), 0), func.coalesce(func.avg(Order.total_amount), 0)))
    total_orders, gross_value, average_value = total_orders_result.one()

    review_result = await db.execute(select(func.count(Review.id), func.avg(Review.rating)))
    review_count, average_rating = review_result.one()

    return AdminAnalyticsOverview(
        users=UserAnalytics(total=total_users, by_role=users_by_role, new_over_time=new_users),
        listings=ListingAnalytics(
            total=await _scalar_count(db, CropListing),
            by_status=await _count_by(db, CropListing, CropListing.status),
            by_category=await _count_by(db, CropListing, CropListing.category),
        ),
        orders=OrderAnalytics(
            total=int(total_orders or 0),
            by_status=await _count_by(db, Order, Order.status),
            gross_value=float(gross_value or 0),
            average_value=float(average_value or 0),
        ),
        advisory=AdvisoryAnalytics(
            crop_recommendations=await _scalar_count(db, CropRecommendationRecord),
            fertilizer_recommendations=await _scalar_count(db, FertilizerRecommendationRecord),
            disease_detections=await _scalar_count(db, DiseaseDetectionRecord),
            recommendation_history=await _scalar_count(db, RecommendationHistory),
        ),
        content=ContentAnalytics(educational_resources=await _scalar_count(db, EducationalArticle)),
        trust=TrustAnalytics(
            reviews=int(review_count or 0),
            average_rating=round(float(average_rating), 2) if average_rating is not None else None,
        ),
    )
