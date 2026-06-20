import uuid
import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, text, select
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import RoleChecker
from app.models.marketplace import CropListing
from app.models.review import Review
from app.models.user import User, FarmerProfile
from app.schemas.farmers import FarmerLocationUpdate, FarmerProfileUpdate, NearbyFarmerResponse, PublicFarmerProfileResponse, PublicListingSummary

router = APIRouter()

farmer_guard = RoleChecker(allowed_roles=["farmer"])


async def get_farmer_rating_summary(db: AsyncSession, farmer_id: uuid.UUID) -> dict:
    result = await db.execute(
        select(func.avg(Review.rating), func.count(Review.id)).where(Review.farmer_id == farmer_id)
    )
    average, count = result.one()
    return {
        "average_rating": round(float(average), 2) if average is not None else None,
        "review_count": int(count or 0),
    }


def public_listing_summary(listing: CropListing) -> dict:
    return {
        "id": listing.id,
        "title": listing.title,
        "description": listing.description,
        "price_per_unit": float(listing.price_per_unit),
        "unit": listing.unit,
        "available_quantity": listing.available_quantity,
        "image_urls": listing.image_urls,
        "category": listing.category,
        "status": listing.status,
    }

@router.patch("/me/location", response_model=NearbyFarmerResponse)
async def update_my_location(
    payload: FarmerLocationUpdate,
    current_user: User = Depends(farmer_guard),
    db: AsyncSession = Depends(get_db)
):
    """
    Allow farmers to create or update their own location details.
    Enforces that authenticated farmer updates only their own profile.
    """
    # Load profile
    result = await db.execute(select(FarmerProfile).where(FarmerProfile.user_id == current_user.id))
    profile = result.scalars().first()
    
    if not profile:
        # If farmer profile doesn't exist, create it
        profile = FarmerProfile(user_id=current_user.id)
        db.add(profile)

    profile.latitude = payload.latitude
    profile.longitude = payload.longitude
    profile.address = payload.address
    profile.district = payload.district
    profile.city = payload.city
    profile.state = payload.state
    profile.location_visibility = payload.location_visibility
    
    await db.commit()
    await db.refresh(profile)
    
    # Return response with raw coordinates for the owner
    return NearbyFarmerResponse(
        farmer_id=profile.user_id,
        full_name=current_user.full_name,
        farm_name=profile.farm_name,
        latitude=profile.latitude,
        longitude=profile.longitude,
        address=profile.address,
        district=profile.district,
        city=profile.city,
        state=profile.state,
        distance_km=0.0,
        rating=profile.rating
    )


@router.patch("/me/profile", response_model=PublicFarmerProfileResponse)
async def update_my_profile(
    payload: FarmerProfileUpdate,
    current_user: User = Depends(farmer_guard),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(FarmerProfile).where(FarmerProfile.user_id == current_user.id))
    profile = result.scalars().first()
    if not profile:
        profile = FarmerProfile(user_id=current_user.id)
        db.add(profile)

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(profile, key, value)

    await db.commit()
    return await build_public_profile(db, current_user.id)


async def build_public_profile(db: AsyncSession, farmer_id: uuid.UUID) -> dict:
    result = await db.execute(
        select(FarmerProfile)
        .where(FarmerProfile.user_id == farmer_id)
        .options(selectinload(FarmerProfile.user))
    )
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer profile not found.")

    listings_result = await db.execute(
        select(CropListing)
        .where(CropListing.farmer_id == farmer_id, CropListing.status == "active")
        .order_by(CropListing.created_at.desc())
    )
    reviews_result = await db.execute(
        select(Review)
        .where(Review.farmer_id == farmer_id)
        .options(selectinload(Review.customer))
        .order_by(Review.created_at.desc())
        .limit(10)
    )
    rating = await get_farmer_rating_summary(db, farmer_id)

    return {
        "farmer_id": profile.user_id,
        "full_name": profile.user.full_name if profile.user else "Unknown farmer",
        "farm_name": profile.farm_name,
        "address": profile.address if profile.location_visibility else None,
        "district": profile.district if profile.location_visibility else None,
        "city": profile.city if profile.location_visibility else None,
        "state": profile.state if profile.location_visibility else None,
        "description": profile.description,
        "average_rating": rating["average_rating"],
        "review_count": rating["review_count"],
        "active_listings": [public_listing_summary(listing) for listing in listings_result.scalars().all()],
        "recent_reviews": [
            {
                "id": review.id,
                "rating": review.rating,
                "comment": review.comment,
                "reviewer_name": review.customer.full_name if review.customer else None,
                "created_at": review.created_at,
            }
            for review in reviews_result.scalars().all()
        ],
    }


@router.get("/{farmer_id}/public", response_model=PublicFarmerProfileResponse)
async def get_public_farmer_profile(farmer_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    return await build_public_profile(db, farmer_id)


@router.get("/{farmer_id}/listings", response_model=List[PublicListingSummary])
async def get_public_farmer_listings(farmer_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(FarmerProfile).where(FarmerProfile.user_id == farmer_id))
    if not result.scalars().first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Farmer profile not found.")

    listings = await db.execute(
        select(CropListing)
        .where(CropListing.farmer_id == farmer_id, CropListing.status == "active")
        .order_by(CropListing.created_at.desc())
    )
    return [public_listing_summary(listing) for listing in listings.scalars().all()]

@router.get("/nearby", response_model=List[NearbyFarmerResponse])
async def get_nearby_farmers(
    lat: float = Query(..., description="Target Latitude"),
    lon: float = Query(..., description="Target Longitude"),
    radius: float = Query(10.0, description="Proximity search radius in kilometers"),
    db: AsyncSession = Depends(get_db)
):
    """
    Discover nearby active farmers within a specific radius of geo-coordinates.
    Suppresses exact latitude/longitude coordinates, rounding to 2 decimal places.
    Filters out locations where location_visibility is false.
    """
    # 1 degree of latitude is roughly 111 km
    lat_delta = radius / 111.0
    
    # Pre-calculate bounding box in Python
    min_lat = lat - lat_delta
    max_lat = lat + lat_delta
    
    # Avoid zero division or cosine calculations at poles
    cos_lat = math.cos(math.radians(lat))
    lon_factor = 111.32 * cos_lat if abs(lat) < 89.9 else 1.0
    min_lon = lon - (radius / lon_factor)
    max_lon = lon + (radius / lon_factor)
    
    haversine_formula = """
        (6371 * acos(
            least(1.0, greatest(-1.0, 
                cos(radians(:lat)) * cos(radians(latitude)) * 
                cos(radians(longitude) - radians(:lon)) + 
                sin(radians(:lat)) * sin(radians(latitude))
            ))
        ))
    """
    
    query = text(f"""
        SELECT fp.user_id, fp.farm_name, fp.latitude, fp.longitude, fp.address, 
               fp.district, fp.city, fp.state, fp.rating, u.full_name,
               {haversine_formula} AS distance
        FROM farmer_profiles fp
        JOIN users u ON fp.user_id = u.id
        WHERE fp.latitude BETWEEN :min_lat AND :max_lat
          AND fp.longitude BETWEEN :min_lon AND :max_lon
          AND fp.location_visibility = true
          AND {haversine_formula} <= :radius
        ORDER BY distance ASC
    """)
    
    result = await db.execute(query, {
        "lat": lat,
        "lon": lon,
        "radius": radius,
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    })
    
    nearby_list = []
    for row in result.all():
        # Round coords to 2 decimal places to protect exact exact privacy (~1.1km blur)
        rounded_lat = round(float(row[2]), 2) if row[2] is not None else 0.0
        rounded_lon = round(float(row[3]), 2) if row[3] is not None else 0.0
        
        nearby_list.append(NearbyFarmerResponse(
            farmer_id=row[0],
            farm_name=row[1],
            latitude=rounded_lat,
            longitude=rounded_lon,
            address=row[4],
            district=row[5],
            city=row[6],
            state=row[7],
            rating=row[8],
            full_name=row[9],
            distance_km=round(float(row[10]), 2)
        ))
        
    return nearby_list
