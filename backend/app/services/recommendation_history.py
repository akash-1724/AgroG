from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.intelligence import RecommendationHistory
from app.models.user import User


def add_recommendation_history(
    db: AsyncSession,
    user: Optional[User],
    recommendation_type: str,
    input_payload: dict[str, Any],
    result_payload: dict[str, Any],
    model_status: Optional[str] = None,
    used_weather: bool = False,
) -> Optional[RecommendationHistory]:
    if not user:
        return None

    record = RecommendationHistory(
        user_id=user.id,
        recommendation_type=recommendation_type,
        input_payload=input_payload,
        result_payload=result_payload,
        model_status=model_status,
        used_weather=used_weather,
    )
    db.add(record)
    return record
