from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.intelligence import CropPriceCatalogResponse, CropPriceTrendResponse
from app.services.prices import get_price_provider


router = APIRouter()


@router.get("/crops", response_model=CropPriceCatalogResponse)
async def get_price_crops(db: AsyncSession = Depends(get_db)):
    return await get_price_provider(db).list_crops()


@router.get("/trends", response_model=CropPriceTrendResponse)
async def get_price_trends(
    crop: Optional[str] = Query(None),
    market: Optional[str] = Query(None),
    state: Optional[str] = Query(None),
    days: Optional[int] = Query(None, ge=1, le=3650),
    db: AsyncSession = Depends(get_db),
):
    return await get_price_provider(db).get_trends(crop=crop, market=market, state=state, days=days)
