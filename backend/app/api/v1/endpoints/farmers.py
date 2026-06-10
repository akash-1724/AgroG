import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from pydantic import BaseModel

from app.core.database import get_db

router = APIRouter()

# Response Schema for Farmer Search with Distance
class FarmerSearchResponse(BaseModel):
    user_id: uuid.UUID
    farm_name: str
    latitude: float
    longitude: float
    address: str
    description: Optional[str] = None
    rating: float
    distance_km: float

    class Config:
        from_attributes = True

@router.get("/search", response_model=List[FarmerSearchResponse])
async def search_farmers(
    lat: float = Query(..., description="Target Latitude of center coordinate"),
    lon: float = Query(..., description="Target Longitude of center coordinate"),
    radius: float = Query(10.0, description="Proximity search radius in kilometers"),
    db: AsyncSession = Depends(get_db)
):
    """
    Search for farmers within a specific radius of geo-coordinates.
    Calculates distance using the Haversine formula in SQL.
    """
    # 6371 represents Earth's radius in kilometers
    # We use a bounding box check first to reduce CPU overhead of acos
    # 1 degree of latitude is roughly 111 km
    import math
    lat_delta = radius / 111.0
    lon_delta = radius / (111.0 * abs(float(math.cos(math.radians(lat)))) if lat != 90 and lat != -90 else 1.0)
    
    # SQL query with Haversine formula. To prevent math domain error when cos calculation is slightly > 1,
    # we use least/greatest or simple acos bounds handling in SQL.
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
        SELECT user_id, farm_name, latitude, longitude, address, description, rating,
        {haversine_formula} AS distance
        FROM farmer_profiles
        WHERE latitude BETWEEN :min_lat AND :max_lat
          AND longitude BETWEEN :min_lon AND :max_lon
          AND {haversine_formula} <= :radius
        ORDER BY distance ASC
    """)
    
    # Calculate bounding box values in Python
    import math
    min_lat = lat - lat_delta
    max_lat = lat + lat_delta
    
    # Handle longitude wrap around or simple bounding
    min_lon = lon - (radius / (111.32 * math.cos(math.radians(lat))))
    max_lon = lon + (radius / (111.32 * math.cos(math.radians(lat))))
    
    result = await db.execute(query, {
        "lat": lat,
        "lon": lon,
        "radius": radius,
        "min_lat": min_lat,
        "max_lat": max_lat,
        "min_lon": min_lon,
        "max_lon": max_lon
    })
    
    farmers = []
    for row in result.all():
        farmers.append(FarmerSearchResponse(
            user_id=row[0],
            farm_name=row[1],
            latitude=row[2],
            longitude=row[3],
            address=row[4],
            description=row[5],
            rating=row[6],
            distance_km=round(float(row[7]), 2)
        ))
        
    return farmers
