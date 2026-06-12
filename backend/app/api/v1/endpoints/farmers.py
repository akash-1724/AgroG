import uuid
import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text, select

from app.core.database import get_db
from app.api.deps import get_current_user, RoleChecker
from app.models.user import User, FarmerProfile
from app.schemas.farmers import FarmerLocationUpdate, NearbyFarmerResponse

router = APIRouter()

farmer_guard = RoleChecker(allowed_roles=["farmer"])

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
