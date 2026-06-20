import uuid
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, update, delete
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.api.deps import get_current_user, RoleChecker
from app.models.user import User
from app.models.marketplace import CropListing, ListingImage, Order, OrderItem
from app.models.review import Review
from app.schemas.marketplace import (
    CropListingCreate, CropListingUpdate, CropListingResponse,
    ListingImageUploadResponse,
    OrderCreate, OrderResponse, OrderStatusUpdate, FarmerOrderResponse,
    OrderItemStatusUpdate,
)
from app.services.uploads import get_storage_provider, validate_listing_image

router = APIRouter()

# Instantiate role guards
farmer_guard = RoleChecker(allowed_roles=["farmer", "admin"])

ORDER_ITEM_STATUSES = {"pending", "accepted", "rejected", "ready", "completed", "cancelled"}
ORDER_ITEM_TERMINAL_STATUSES = {"rejected", "completed", "cancelled"}
STOCK_RESTORE_STATUSES = {"rejected", "cancelled"}
ORDER_ITEM_TRANSITIONS = {
    "pending": {"accepted", "rejected", "cancelled"},
    "accepted": {"ready", "rejected", "cancelled"},
    "ready": {"completed", "cancelled"},
}


def validate_item_status_transition(current_status: str, target_status: str, role: str) -> None:
    if target_status not in ORDER_ITEM_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid order item status.")
    if current_status == target_status:
        return
    if current_status in ORDER_ITEM_TERMINAL_STATUSES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition order item from terminal state '{current_status}'.",
        )
    if target_status == "pending":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Order items cannot return to pending status.")
    if role == "farmer" and target_status == "cancelled":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Farmers must reject unavailable items instead of cancelling them.")
    if target_status not in ORDER_ITEM_TRANSITIONS.get(current_status, set()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transition from '{current_status}' to '{target_status}'.",
        )


def derive_order_status(item_statuses: list[str]) -> str:
    if not item_statuses:
        return "pending"
    if all(item_status == "completed" for item_status in item_statuses):
        return "completed"
    if all(item_status in {"rejected", "cancelled"} for item_status in item_statuses):
        return "cancelled"
    if any(item_status == "ready" for item_status in item_statuses):
        return "ready"
    if any(item_status == "accepted" for item_status in item_statuses):
        return "accepted"
    return "pending"


async def restore_item_stock_once(db: AsyncSession, item: OrderItem, target_status: str) -> None:
    if item.status in STOCK_RESTORE_STATUSES or target_status not in STOCK_RESTORE_STATUSES:
        return
    result = await db.execute(select(CropListing).where(CropListing.id == item.crop_listing_id))
    listing = result.scalars().first()
    if listing:
        listing.available_quantity += item.quantity


async def listing_rating_summary(db: AsyncSession, listing_id: uuid.UUID) -> dict:
    result = await db.execute(
        select(func.avg(Review.rating), func.count(Review.id)).where(Review.listing_id == listing_id)
    )
    average, count = result.one()
    return {
        "average_rating": round(float(average), 2) if average is not None else None,
        "review_count": int(count or 0),
    }


async def serialize_listing(db: AsyncSession, listing: CropListing) -> dict:
    rating = await listing_rating_summary(db, listing.id)
    image_result = await db.execute(select(ListingImage).where(ListingImage.listing_id == listing.id).order_by(ListingImage.is_primary.desc(), ListingImage.sort_order.asc(), ListingImage.created_at.asc()))
    images = image_result.scalars().all()
    primary_image_url = images[0].image_url if images else None
    if not primary_image_url and listing.image_urls:
        primary_image_url = listing.image_urls.split(",")[0].strip() or None
    return {
        "id": listing.id,
        "farmer_id": listing.farmer_id,
        "title": listing.title,
        "description": listing.description,
        "price_per_unit": float(listing.price_per_unit),
        "unit": listing.unit,
        "available_quantity": listing.available_quantity,
        "image_urls": listing.image_urls,
        "images": images,
        "primary_image_url": primary_image_url,
        "category": listing.category,
        "status": listing.status,
        "average_rating": rating["average_rating"],
        "review_count": rating["review_count"],
        "created_at": listing.created_at,
        "updated_at": listing.updated_at,
    }

@router.get("/", response_model=List[CropListingResponse])
async def read_listings(
    search: Optional[str] = Query(None, description="Search term in listing titles or description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query("active", description="Filter by availability status: active, inactive, sold_out, or 'all'"),
    sort: Optional[str] = Query("latest", description="Sort options: latest, price_asc, price_desc"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve crop listings with paginated search, filtering, and sorting."""
    query = select(CropListing)
    
    # Filter by status
    if status and status != "all":
        query = query.where(CropListing.status == status)
    
    # Filter by category
    if category:
        query = query.where(CropListing.category.ilike(category))
        
    # Search title or description
    if search:
        query = query.where(
            (CropListing.title.ilike(f"%{search}%")) | 
            (CropListing.description.ilike(f"%{search}%"))
        )
        
    # Sorting
    if sort == "price_asc":
        query = query.order_by(CropListing.price_per_unit.asc())
    elif sort == "price_desc":
        query = query.order_by(CropListing.price_per_unit.desc())
    else: # Default latest
        query = query.order_by(CropListing.created_at.desc())
        
    query = query.offset(offset).limit(limit)
    result = await db.execute(query)
    return [await serialize_listing(db, listing) for listing in result.scalars().all()]

@router.post("/listings", response_model=CropListingResponse, status_code=status.HTTP_201_CREATED)
async def create_listing(
    payload: CropListingCreate,
    current_user: User = Depends(farmer_guard),
    db: AsyncSession = Depends(get_db)
):
    """Create a new crop listing in the marketplace (Farmer only)."""
    # Verify that the user has a profile initialized
    from app.models.user import FarmerProfile
    res = await db.execute(select(FarmerProfile).where(FarmerProfile.user_id == current_user.id))
    farmer_profile = res.scalars().first()
    if not farmer_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User must initialize a Farmer Profile before posting listings."
        )
        
    new_listing = CropListing(
        farmer_id=current_user.id,
        title=payload.title,
        description=payload.description,
        price_per_unit=payload.price_per_unit,
        unit=payload.unit,
        available_quantity=payload.available_quantity,
        image_urls=payload.image_urls,
        category=payload.category or "Vegetables",
        status=payload.status or "active"
    )
    
    db.add(new_listing)
    await db.commit()
    await db.refresh(new_listing)
    return await serialize_listing(db, new_listing)

@router.get("/listings/{id}", response_model=CropListingResponse)
async def read_listing(id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    """Retrieve details of a single crop listing."""
    result = await db.execute(select(CropListing).where(CropListing.id == id))
    listing = result.scalars().first()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop listing not found."
        )
    return await serialize_listing(db, listing)


async def get_owned_listing(db: AsyncSession, listing_id: uuid.UUID, current_user: User) -> CropListing:
    result = await db.execute(select(CropListing).where(CropListing.id == listing_id))
    listing = result.scalars().first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Crop listing not found.")
    if listing.farmer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this listing.")
    return listing


@router.post("/listings/{id}/images", response_model=ListingImageUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_listing_image(
    id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(farmer_guard),
    db: AsyncSession = Depends(get_db),
):
    listing = await get_owned_listing(db, id, current_user)
    content = await file.read()
    validate_listing_image(file, content)
    stored = await get_storage_provider().upload_listing_image(file, content)
    if not stored.get("secure_url"):
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Image storage provider did not return a secure URL.")
    existing_count = await db.execute(select(func.count(ListingImage.id)).where(ListingImage.listing_id == listing.id))
    image_count = int(existing_count.scalar() or 0)
    image = ListingImage(
        listing_id=listing.id,
        image_url=stored["secure_url"],
        public_id=stored.get("public_id"),
        alt_text=listing.title,
        sort_order=image_count,
        is_primary=image_count == 0,
    )
    db.add(image)
    await db.commit()
    await db.refresh(image)
    return {"image": image}


@router.delete("/listings/{id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing_image(
    id: uuid.UUID,
    image_id: uuid.UUID,
    current_user: User = Depends(farmer_guard),
    db: AsyncSession = Depends(get_db),
):
    await get_owned_listing(db, id, current_user)
    result = await db.execute(select(ListingImage).where(ListingImage.id == image_id, ListingImage.listing_id == id))
    image = result.scalars().first()
    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing image not found.")
    was_primary = image.is_primary
    await db.delete(image)
    await db.flush()
    if was_primary:
        next_result = await db.execute(select(ListingImage).where(ListingImage.listing_id == id).order_by(ListingImage.sort_order.asc(), ListingImage.created_at.asc()))
        next_image = next_result.scalars().first()
        if next_image:
            next_image.is_primary = True
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/listings/{id}", response_model=CropListingResponse)
async def update_listing(
    id: uuid.UUID,
    payload: CropListingUpdate,
    current_user: User = Depends(farmer_guard),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing crop listing. Only the owner farmer can perform updates."""
    result = await db.execute(select(CropListing).where(CropListing.id == id))
    listing = result.scalars().first()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop listing not found."
        )
        
    # Owner restriction (unless admin)
    if listing.farmer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this listing."
        )
        
    update_data = payload.model_dump(exclude_unset=True)
    for key, val in update_data.items():
        setattr(listing, key, val)
        
    await db.commit()
    await db.refresh(listing)
    return await serialize_listing(db, listing)

@router.delete("/listings/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_listing(
    id: uuid.UUID,
    current_user: User = Depends(farmer_guard),
    db: AsyncSession = Depends(get_db)
):
    """Delete a crop listing. Only the owner farmer or admin can delete."""
    result = await db.execute(select(CropListing).where(CropListing.id == id))
    listing = result.scalars().first()
    
    if not listing:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crop listing not found."
        )
        
    if listing.farmer_id != current_user.id and current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this listing."
        )
        
    await db.delete(listing)
    await db.commit()
    return

@router.post("/orders", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def place_order(
    payload: OrderCreate,
    current_user: User = Depends(get_current_user),
):
    """Direct marketplace checkout is disabled; customers must use cart checkout."""
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Direct marketplace checkout is disabled. Add items to cart and use cart checkout.",
    )

@router.get("/orders", response_model=List[OrderResponse])
async def list_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List orders. Admin sees all, Farmer sees items from their shop, Customer sees their orders."""
    from sqlalchemy.orm import selectinload
    if current_user.role == "admin":
        result = await db.execute(select(Order).options(selectinload(Order.items)))
        return result.scalars().all()
        
    elif current_user.role == "farmer":
        # Select orders that contain at least one item belonging to this farmer's crop listings
        query = select(Order).join(OrderItem).join(CropListing).where(
            CropListing.farmer_id == current_user.id
        ).options(
            selectinload(Order.items).selectinload(OrderItem.crop_listing)
        ).distinct()
        result = await db.execute(query)
        orders = result.scalars().all()
        
        farmer_orders = []
        for order in orders:
            filtered_items = []
            total_farmer_amount = 0.0
            for item in order.items:
                if item.crop_listing and item.crop_listing.farmer_id == current_user.id:
                    filtered_items.append(item)
                    total_farmer_amount += item.quantity * item.price_at_purchase
            
            # Construct a response object compatible with OrderResponse schema, but containing only farmer's info
            farmer_orders.append({
                "id": order.id,
                "customer_id": order.customer_id,
                "status": derive_order_status([item.status for item in filtered_items]),
                "total_amount": total_farmer_amount,
                "items": filtered_items,
                "created_at": order.created_at,
                "updated_at": order.updated_at
            })
        return farmer_orders
        
    else:
        # Customer sees their own orders
        result = await db.execute(
            select(Order)
            .where(Order.customer_id == current_user.id)
            .options(selectinload(Order.items))
        )
        return result.scalars().all()

@router.get("/orders/{id}", response_model=OrderResponse)
async def read_order(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve details of a single order."""
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Order)
        .where(Order.id == id)
        .options(selectinload(Order.items))
    )
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found."
        )
        
    # Check permissions (Customer who placed it, Farmer selling, or Admin)
    if current_user.role == "farmer":
        filtered_items = []
        total_farmer_amount = 0.0
        for item in order.items:
            res_cl = await db.execute(select(CropListing).where(CropListing.id == item.crop_listing_id))
            cl = res_cl.scalars().first()
            if cl and cl.farmer_id == current_user.id:
                item.crop_listing = cl
                filtered_items.append(item)
                total_farmer_amount += item.quantity * item.price_at_purchase
        if not filtered_items:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to view this order."
            )
        return {
            "id": order.id,
            "customer_id": order.customer_id,
            "status": derive_order_status([item.status for item in filtered_items]),
            "total_amount": total_farmer_amount,
            "items": filtered_items,
            "created_at": order.created_at,
            "updated_at": order.updated_at
        }
        
    if current_user.role != "admin" and order.customer_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this order."
        )
             
    return order


@router.patch("/order-items/{id}/status", response_model=OrderResponse)
async def update_order_item_status(
    id: uuid.UUID,
    payload: OrderItemStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if current_user.role not in {"farmer", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Farmers or Admins can update order item status.")

    result = await db.execute(
        select(OrderItem)
        .where(OrderItem.id == id)
        .options(
            selectinload(OrderItem.crop_listing),
            selectinload(OrderItem.order).selectinload(Order.items),
        )
        .with_for_update()
    )
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order item not found.")
    if current_user.role == "farmer" and item.crop_listing.farmer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not own this order item.")

    target_status = payload.status.lower()
    validate_item_status_transition(item.status.lower(), target_status, current_user.role)
    await restore_item_stock_once(db, item, target_status)
    item.status = target_status
    item.status_updated_at = datetime.utcnow()
    if target_status == "completed":
        item.fulfilled_at = datetime.utcnow()

    order = item.order
    order.status = derive_order_status([order_item.status for order_item in order.items])
    await db.commit()

    reload_result = await db.execute(
        select(Order)
        .where(Order.id == order.id)
        .options(selectinload(Order.items).selectinload(OrderItem.crop_listing))
    )
    reloaded_order = reload_result.scalars().first()
    if current_user.role == "farmer":
        filtered_items = [order_item for order_item in reloaded_order.items if order_item.crop_listing and order_item.crop_listing.farmer_id == current_user.id]
        return {
            "id": reloaded_order.id,
            "customer_id": reloaded_order.customer_id,
            "status": derive_order_status([order_item.status for order_item in filtered_items]),
            "total_amount": sum(order_item.quantity * order_item.price_at_purchase for order_item in filtered_items),
            "items": filtered_items,
            "created_at": reloaded_order.created_at,
            "updated_at": reloaded_order.updated_at,
        }
    return reloaded_order

@router.patch("/orders/{id}", response_model=OrderResponse)
async def update_order_status(
    id: uuid.UUID,
    payload: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Allow customer order cancellation only; fulfillment updates are item-level."""
    target_status = payload.status.lower()
    if target_status != "cancelled":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order-level fulfillment updates are disabled. Use /api/v1/marketplace/order-items/{id}/status.",
        )

    result = await db.execute(
        select(Order)
        .where(Order.id == id)
        .options(selectinload(Order.items))
        .with_for_update()
    )
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found.")
    if current_user.role != "customer" or order.customer_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to cancel this order.")
    if order.status.lower() != "pending" or any(item.status.lower() != "pending" for item in order.items):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only fully pending orders can be cancelled at order level.")

    for item in order.items:
        await restore_item_stock_once(db, item, "cancelled")
        item.status = "cancelled"
        item.status_updated_at = datetime.utcnow()
    order.status = derive_order_status([item.status for item in order.items])
    await db.commit()

    reload_result = await db.execute(select(Order).where(Order.id == order.id).options(selectinload(Order.items)))
    return reload_result.scalars().first()
