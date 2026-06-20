from fastapi import APIRouter, Query

from app.schemas.intelligence import WeatherResponse
from app.services.weather import get_weather_provider


router = APIRouter()


@router.get("/current", response_model=WeatherResponse)
async def get_current_weather(
    lat: float = Query(..., ge=-90, le=90),
    lon: float = Query(..., ge=-180, le=180),
):
    provider = get_weather_provider()
    return await provider.get_current_weather(lat, lon)
