from datetime import date, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.intelligence import CropPriceRecord
from app.schemas.intelligence import CropPriceCatalogItem, CropPriceCatalogResponse, CropPriceTrendResponse


SAMPLE_PRICE_DISCLAIMER = "Price records marked as sample/demo are for development only and are not live market prices."


class DatabasePriceDataProvider:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_crops(self) -> CropPriceCatalogResponse:
        result = await self.db.execute(select(CropPriceRecord).order_by(CropPriceRecord.crop_name.asc()))
        records = result.scalars().all()
        crops: dict[str, dict] = {}

        for record in records:
            bucket = crops.setdefault(
                record.crop_name,
                {
                    "crop_name": record.crop_name,
                    "latest_recorded_date": record.recorded_date,
                    "markets": set(),
                    "states": set(),
                    "is_sample": record.is_sample,
                    "source": record.source,
                },
            )
            bucket["latest_recorded_date"] = max(bucket["latest_recorded_date"], record.recorded_date)
            bucket["markets"].add(record.market)
            bucket["states"].add(record.state)
            bucket["is_sample"] = bucket["is_sample"] and record.is_sample

        items = [
            CropPriceCatalogItem(
                crop_name=item["crop_name"],
                latest_recorded_date=item["latest_recorded_date"],
                markets=sorted(item["markets"]),
                states=sorted(item["states"]),
                is_sample=item["is_sample"],
                source=item["source"],
            )
            for item in crops.values()
        ]
        return CropPriceCatalogResponse(
            crops=items,
            provider_status="available" if items else "no_data",
            disclaimer=SAMPLE_PRICE_DISCLAIMER if any(item.is_sample for item in items) else None,
        )

    async def get_trends(
        self,
        crop: Optional[str] = None,
        market: Optional[str] = None,
        state: Optional[str] = None,
        days: Optional[int] = None,
    ) -> CropPriceTrendResponse:
        query = select(CropPriceRecord)
        if crop:
            query = query.where(CropPriceRecord.crop_name.ilike(crop))
        if market:
            query = query.where(CropPriceRecord.market.ilike(market))
        if state:
            query = query.where(CropPriceRecord.state.ilike(state))
        if days:
            query = query.where(CropPriceRecord.recorded_date >= date.today() - timedelta(days=days))

        result = await self.db.execute(query.order_by(CropPriceRecord.recorded_date.asc()))
        records = result.scalars().all()
        return CropPriceTrendResponse(
            crop_name=crop,
            records=records,
            provider_status="available" if records else "no_data",
            is_sample=any(record.is_sample for record in records),
            disclaimer=SAMPLE_PRICE_DISCLAIMER if any(record.is_sample for record in records) else None,
        )


def get_price_provider(db: AsyncSession) -> DatabasePriceDataProvider:
    return DatabasePriceDataProvider(db)
