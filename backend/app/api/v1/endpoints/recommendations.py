import uuid
import httpx
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.config import settings
from app.core.cache import get_json_cache, set_json_cache
from app.api.deps import get_current_user_optional, get_current_user
from app.models.user import User
from app.models.recommendations import CropRecommendationRecord, FertilizerRecommendationRecord, DiseaseDetectionRecord
from app.schemas.recommendations import (
    CropRecommendationCreate, CropRecommendationResponse,
    FertilizerRecommendationCreate, FertilizerRecommendationResponse,
    DiseaseDetectionResponse
)

router = APIRouter()

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
                recommended_crops = response.json().get("recommendations", [])
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
        recommended_crops=recommended_crops,
        created_at=new_record.created_at
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
    cache_key = f"fert_rec:{round(payload.nitrogen, 1)}:{round(payload.phosphorus, 1)}:{round(payload.potassium, 1)}"
    
    cached_data = await get_json_cache(cache_key)
    if cached_data:
        recommended_fertilizer = cached_data
    else:
        # Fetch from ML service
        async with httpx.AsyncClient() as client:
            try:
                # ML service doesn't take crop_type, it just takes nitrogen, phosphorus, potassium
                response = await client.post(
                    f"{settings.ML_SERVICE_URL}/recommendations/fertilizer",
                    json={
                        "nitrogen": payload.nitrogen,
                        "phosphorus": payload.phosphorus,
                        "potassium": payload.potassium
                    },
                    timeout=10.0
                )
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_502_BAD_GATEWAY,
                        detail="ML service returned an error."
                    )
                recommended_fertilizer = response.json().get("recommended_fertilizer", "10-26-26")
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
    
    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)
    
    return new_record

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
    if file.content_type not in ["image/jpeg", "image/png", "image/jpg"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid image format. Supported: JPEG, PNG."
        )

    # Read file content
    contents = await file.read()
    
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

    db.add(new_record)
    await db.commit()
    await db.refresh(new_record)

    return new_record

