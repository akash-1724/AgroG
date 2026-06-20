import uuid
import httpx
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.core.cache import get_json_cache, set_json_cache
from app.api.deps import get_current_user_optional, get_current_user
from app.models.user import FarmerProfile, User
from app.models.recommendations import CropRecommendationRecord, FertilizerRecommendationRecord, DiseaseDetectionRecord
from app.models.intelligence import RecommendationHistory
from app.schemas.recommendations import (
    CropRecommendationCreate, CropRecommendationResponse,
    FertilizerRecommendationCreate, FertilizerRecommendationResponse,
    DiseaseDetectionResponse
)
from app.schemas.intelligence import RecommendationHistoryDetail, RecommendationHistoryListItem, WeatherAwareCropRecommendationCreate, WeatherAwareCropRecommendationResponse
from app.services.recommendation_history import add_recommendation_history
from app.services.weather import get_weather_provider

router = APIRouter()


async def _fetch_crop_recommendations(payload: CropRecommendationCreate):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{settings.ML_SERVICE_URL}/recommendations/crop",
                json=payload.model_dump(),
                timeout=10.0
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="ML service returned an error."
                )
            res_data = response.json()
            return (
                res_data.get("recommendations", []),
                res_data.get("model_status", "demo"),
                res_data.get("disclaimer", ""),
                res_data.get("limitations", ""),
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to connect to ML service: {str(e)}"
            )

@router.post("/crop", response_model=CropRecommendationResponse)
async def get_crop_recommendation(
    payload: CropRecommendationCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Get crop recommendations based on soil and weather metrics.
    Caches predictions using Redis. Saves records to Postgres if user is authenticated.
    """
    # Create a unique cache key based on inputs (rounded to 2 decimal places to increase hit rates)
    cache_key = f"crop_rec:{round(payload.nitrogen, 1)}:{round(payload.phosphorus, 1)}:{round(payload.potassium, 1)}:{round(payload.ph, 1)}:{round(payload.temperature, 1)}:{round(payload.humidity, 1)}:{round(payload.rainfall, 1)}"
    
    # Try fetching from cache
    cached_data = await get_json_cache(cache_key)
    if cached_data:
        recommended_crops = cached_data
        model_status = "demo"
        disclaimer = "Cached Result. Run parameters again to fetch fresh advisory status."
        limitations = ""
    else:
        # Fetch from ML service
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{settings.ML_SERVICE_URL}/recommendations/crop",
                    json=payload.model_dump(),
                    timeout=10.0
                )
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="ML service returned an error."
                    )
                res_data = response.json()
                recommended_crops = res_data.get("recommendations", [])
                model_status = res_data.get("model_status", "demo")
                disclaimer = res_data.get("disclaimer", "")
                limitations = res_data.get("limitations", "")
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Failed to connect to ML service: {str(e)}"
                )
        
        # Cache the result in Redis for 2 hours
        await set_json_cache(cache_key, recommended_crops, expire_seconds=7200)

    # Save record to database if user is logged in
    new_record = CropRecommendationRecord(
        user_id=current_user.id if current_user else None,
        nitrogen=payload.nitrogen,
        phosphorus=payload.phosphorus,
        potassium=payload.potassium,
        ph=payload.ph,
        temperature=payload.temperature,
        humidity=payload.humidity,
        rainfall=payload.rainfall,
        recommended_crops={"crops": recommended_crops}
    )
    result_payload = {
        "recommended_crops": [(c["crop"] if isinstance(c, dict) else c) for c in recommended_crops],
        "model_status": model_status,
        "disclaimer": disclaimer,
        "limitations": limitations,
    }
    add_recommendation_history(
        db,
        current_user,
        "crop",
        payload.model_dump(),
        result_payload,
        model_status=model_status,
    )

    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)

    return CropRecommendationResponse(
        id=new_record.id,
        nitrogen=new_record.nitrogen,
        phosphorus=new_record.phosphorus,
        potassium=new_record.potassium,
        ph=new_record.ph,
        temperature=new_record.temperature,
        humidity=new_record.humidity,
        rainfall=new_record.rainfall,
        recommended_crops=[(c["crop"] if isinstance(c, dict) else c) for c in recommended_crops],
        created_at=new_record.created_at,
        model_status=model_status,
        disclaimer=disclaimer,
        limitations=limitations
    )


@router.post("/crop/weather-aware", response_model=WeatherAwareCropRecommendationResponse)
async def get_weather_aware_crop_recommendation(
    payload: WeatherAwareCropRecommendationCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    latitude = payload.latitude
    longitude = payload.longitude

    if (latitude is None or longitude is None) and current_user and payload.use_profile_location:
        profile_result = await db.execute(select(FarmerProfile).where(FarmerProfile.user_id == current_user.id))
        farmer_profile = profile_result.scalars().first()
        if farmer_profile and farmer_profile.latitude is not None and farmer_profile.longitude is not None:
            latitude = farmer_profile.latitude
            longitude = farmer_profile.longitude

    weather_response = None
    effective_payload = CropRecommendationCreate(**payload.model_dump(exclude={"latitude", "longitude", "use_profile_location"}))
    used_weather = False
    weather_warning = None
    provider_status = "not_requested"

    if latitude is not None and longitude is not None:
        weather_response = await get_weather_provider().get_current_weather(latitude, longitude)
        provider_status = weather_response.provider_status
        if weather_response.available and weather_response.weather:
            weather = weather_response.weather
            # Clip values to the valid ranges required by the ML model
            raw_temp = weather.temperature if weather.temperature is not None else payload.temperature
            clipped_temp = min(max(raw_temp, 0.0), 50.0)

            raw_humidity = weather.humidity if weather.humidity is not None else payload.humidity
            clipped_humidity = min(max(raw_humidity, 10.0), 100.0)

            raw_rainfall = (
                weather.rainfall
                if weather.rainfall is not None
                else weather.precipitation
                if weather.precipitation is not None
                else payload.rainfall
            )
            clipped_rainfall = min(max(raw_rainfall, 10.0), 500.0)

            effective_payload = CropRecommendationCreate(
                nitrogen=payload.nitrogen,
                phosphorus=payload.phosphorus,
                potassium=payload.potassium,
                ph=payload.ph,
                temperature=clipped_temp,
                humidity=clipped_humidity,
                rainfall=clipped_rainfall,
            )
            used_weather = True
        else:
            weather_warning = weather_response.warning or "Weather data unavailable; normal recommendation inputs were used."

    recommended_crops, model_status, disclaimer, limitations = await _fetch_crop_recommendations(effective_payload)

    new_record = CropRecommendationRecord(
        user_id=current_user.id if current_user else None,
        nitrogen=effective_payload.nitrogen,
        phosphorus=effective_payload.phosphorus,
        potassium=effective_payload.potassium,
        ph=effective_payload.ph,
        temperature=effective_payload.temperature,
        humidity=effective_payload.humidity,
        rainfall=effective_payload.rainfall,
        recommended_crops={"crops": recommended_crops}
    )
    result_payload = {
        "recommended_crops": [(c["crop"] if isinstance(c, dict) else c) for c in recommended_crops],
        "model_status": model_status,
        "disclaimer": disclaimer,
        "limitations": limitations,
        "used_weather": used_weather,
        "weather": weather_response.weather.model_dump(mode="json") if weather_response and weather_response.weather else None,
        "weather_warning": weather_warning,
        "provider_status": provider_status,
    }
    add_recommendation_history(
        db,
        current_user,
        "crop",
        payload.model_dump(),
        result_payload,
        model_status=model_status,
        used_weather=used_weather,
    )

    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)

    return WeatherAwareCropRecommendationResponse(
        id=new_record.id,
        nitrogen=new_record.nitrogen,
        phosphorus=new_record.phosphorus,
        potassium=new_record.potassium,
        ph=new_record.ph,
        temperature=new_record.temperature,
        humidity=new_record.humidity,
        rainfall=new_record.rainfall,
        recommended_crops=[(c["crop"] if isinstance(c, dict) else c) for c in recommended_crops],
        created_at=new_record.created_at,
        model_status=model_status,
        disclaimer=disclaimer,
        limitations=limitations,
        used_weather=used_weather,
        weather=weather_response.weather if weather_response and weather_response.available else None,
        weather_warning=weather_warning,
        provider_status=provider_status,
    )

@router.post("/fertilizer", response_model=FertilizerRecommendationResponse)
async def get_fertilizer_recommendation(
    payload: FertilizerRecommendationCreate,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Get fertilizer recommendations based on soil metrics.
    Caches predictions using Redis. Saves records to Postgres if user is authenticated.
    """
    cache_key = f"fert_rec:{round(payload.nitrogen, 1)}:{round(payload.phosphorus, 1)}:{round(payload.potassium, 1)}:{payload.crop_type}"
    
    cached_data = await get_json_cache(cache_key)
    if cached_data:
        recommended_fertilizer = cached_data
        model_status = "demo"
        disclaimer = "Cached Result. Run parameters again to fetch fresh advisory status."
        limitations = ""
    else:
        # Fetch from ML service
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{settings.ML_SERVICE_URL}/recommendations/fertilizer",
                    json={
                        "nitrogen": payload.nitrogen,
                        "phosphorus": payload.phosphorus,
                        "potassium": payload.potassium,
                        "crop_type": payload.crop_type
                    },
                    timeout=10.0
                )
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="ML service returned an error."
                    )
                res_data = response.json()
                recommended_fertilizer = res_data.get("recommended_fertilizer", "NPK-19-19-19")
                model_status = res_data.get("model_status", "demo")
                disclaimer = res_data.get("disclaimer", "")
                limitations = res_data.get("limitations", "")
            except httpx.RequestError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"Failed to connect to ML service: {str(e)}"
                )
        
        await set_json_cache(cache_key, recommended_fertilizer, expire_seconds=7200)

    # Save to database
    new_record = FertilizerRecommendationRecord(
        user_id=current_user.id if current_user else None,
        nitrogen=payload.nitrogen,
        phosphorus=payload.phosphorus,
        potassium=payload.potassium,
        crop_type=payload.crop_type,
        recommended_fertilizer=recommended_fertilizer
    )
    add_recommendation_history(
        db,
        current_user,
        "fertilizer",
        payload.model_dump(),
        {
            "recommended_fertilizer": recommended_fertilizer,
            "model_status": model_status,
            "disclaimer": disclaimer,
            "limitations": limitations,
        },
        model_status=model_status,
    )
    
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    
    return FertilizerRecommendationResponse(
        id=new_record.id,
        nitrogen=new_record.nitrogen,
        phosphorus=new_record.phosphorus,
        potassium=new_record.potassium,
        crop_type=new_record.crop_type,
        recommended_fertilizer=new_record.recommended_fertilizer,
        created_at=new_record.created_at,
        model_status=model_status,
        disclaimer=disclaimer,
        limitations=limitations
    )

@router.get("/history/crop", response_model=List[CropRecommendationResponse])
async def get_crop_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve the logged-in user's crop recommendation history."""
    query = select(CropRecommendationRecord).where(CropRecommendationRecord.user_id == current_user.id).order_by(CropRecommendationRecord.created_at.desc())
    result = await db.execute(query)
    records = result.scalars().all()
    
    response_records = []
    for r in records:
        response_records.append(CropRecommendationResponse(
            id=r.id,
            nitrogen=r.nitrogen,
            phosphorus=r.phosphorus,
            potassium=r.potassium,
            ph=r.ph,
            temperature=r.temperature,
            humidity=r.humidity,
            rainfall=r.rainfall,
            recommended_crops=r.recommended_crops.get("crops", []),
            created_at=r.created_at
        ))
    return response_records

@router.get("/history/fertilizer", response_model=List[FertilizerRecommendationResponse])
async def get_fertilizer_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve the logged-in user's fertilizer recommendation history."""
    query = select(FertilizerRecommendationRecord).where(FertilizerRecommendationRecord.user_id == current_user.id).order_by(FertilizerRecommendationRecord.created_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/history", response_model=List[RecommendationHistoryListItem])
async def get_recommendation_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(RecommendationHistory)
        .where(RecommendationHistory.user_id == current_user.id)
        .order_by(RecommendationHistory.created_at.desc())
    )
    result = await db.execute(query)
    return result.scalars().all()


@router.get("/history/{history_id}", response_model=RecommendationHistoryDetail)
async def get_recommendation_history_detail(
    history_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(RecommendationHistory).where(
            RecommendationHistory.id == history_id,
            RecommendationHistory.user_id == current_user.id,
        )
    )
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation history not found")
    return record


@router.delete("/history/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recommendation_history(
    history_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(RecommendationHistory).where(
            RecommendationHistory.id == history_id,
            RecommendationHistory.user_id == current_user.id,
        )
    )
    record = result.scalars().first()
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recommendation history not found")
    await db.delete(record)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/disease/detect", response_model=DiseaseDetectionResponse)
async def detect_disease(
    file: UploadFile = File(...),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db)
):
    """
    Detect leaf diseases by routing the leaf image file to the ML service.
    Saves diagnostic record to Postgres database if user is authenticated.
    """
    allowed_content_types = {"image/jpeg", "image/png", "image/jpg"}
    allowed_extensions = {".jpg", ".jpeg", ".png"}
    if file.content_type not in allowed_content_types or Path(file.filename or "").suffix.lower() not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Invalid image format. Supported: JPEG, PNG."
        )

    # Read file content
    contents = await file.read()
    max_bytes = settings.MAX_LISTING_IMAGE_UPLOAD_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=f"Image exceeds {settings.MAX_LISTING_IMAGE_UPLOAD_MB}MB limit.")
    if not (contents.startswith(b"\xff\xd8\xff") or contents.startswith(b"\x89PNG\r\n\x1a\n")):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid image file signature.")
    
    # Reset file cursor for safe reuse (if needed)
    await file.seek(0)
    
    async with httpx.AsyncClient() as client:
        try:
            # Route to ML Service
            response = await client.post(
                f"{settings.ML_SERVICE_URL}/disease/detect",
                files={"file": (file.filename, contents, file.content_type)},
                timeout=15.0
            )
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="ML service returned an error."
                )
            result = response.json()
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to connect to ML service: {str(e)}"
            )

    # Mock an image URL for the record (e.g. data URL or placeholder)
    mock_url = f"https://cloudinary.agroguide.internal/uploads/{uuid.uuid4()}-{file.filename}"

    new_record = DiseaseDetectionRecord(
        user_id=current_user.id if current_user else None,
        image_url=mock_url,
        predicted_disease=result.get("predicted_disease", "Healthy Leaf"),
        confidence=result.get("confidence", 1.0),
        remedy=result.get("remedy", "No treatment required.")
    )
    add_recommendation_history(
        db,
        current_user,
        "disease",
        {"filename": file.filename, "content_type": file.content_type},
        {
            "predicted_disease": result.get("predicted_disease", "Healthy Leaf"),
            "confidence": result.get("confidence", 1.0),
            "remedy": result.get("remedy", "No treatment required."),
            "model_status": result.get("model_status", "demo"),
            "disclaimer": result.get("disclaimer", ""),
            "limitations": result.get("limitations", ""),
        },
        model_status=result.get("model_status", "demo"),
    )

    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)

    return DiseaseDetectionResponse(
        id=new_record.id,
        image_url=new_record.image_url,
        predicted_disease=new_record.predicted_disease,
        confidence=new_record.confidence,
        remedy=new_record.remedy,
        created_at=new_record.created_at,
        model_status=result.get("model_status", "demo"),
        disclaimer=result.get("disclaimer", ""),
        limitations=result.get("limitations", "")
    )
