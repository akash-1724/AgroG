from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import RoleChecker
from app.core.database import get_db
from app.models.user import User
from app.schemas.admin import AdminAnalyticsOverview
from app.services.admin_analytics import get_admin_analytics_overview


router = APIRouter()
admin_guard = RoleChecker(allowed_roles=["admin"])


@router.get("/analytics/overview", response_model=AdminAnalyticsOverview)
async def read_admin_analytics_overview(
    current_user: User = Depends(admin_guard),
    db: AsyncSession = Depends(get_db),
):
    return await get_admin_analytics_overview(db)
