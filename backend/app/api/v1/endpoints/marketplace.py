import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete

from app.core.database import get_db
from app.api.deps import get_current_user, RoleChecker
from app.models.user import User
from app.models.marketplace import CropListing, Order, OrderItem
from app.schemas.marketplace import (
    CropListingCreate, CropListingUpdate, CropListingResponse,
    OrderCreate, OrderResponse, OrderStatusUpdate, FarmerOrderResponse
)

router = APIRouter()

# Instantiate role guards
farmer_guard = RoleChecker(allowed_roles=["farmer", "admin"])

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
    return result.scalars().all()

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
    return new_listing

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
    return listing

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
    return listing

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
    db: AsyncSession = Depends(get_db)
):
    """Place a new order in the marketplace (Customers only)."""
    # Create the base order first
    new_order = Order(
        customer_id=current_user.id,
        status="pending",
        total_amount=0.0
    )
    db.add(new_order)
    await db.flush() # Populate the ID

    total_amount = 0.0
    order_items = []

    for item in payload.items:
        # Fetch crop listing and lock it for update to prevent race conditions in quantity stock
        result = await db.execute(
            select(CropListing).where(CropListing.id == item.crop_listing_id).with_for_update()
        )
        listing = result.scalars().first()
        
        if not listing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Crop listing {item.crop_listing_id} not found."
            )
            
        if listing.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Crop listing '{listing.title}' is not active/available."
            )
            
        if listing.available_quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for '{listing.title}'. Available: {listing.available_quantity}, Requested: {item.quantity}"
            )
            
        # Deduct quantity
        listing.available_quantity -= item.quantity
        if listing.available_quantity == 0:
            listing.status = "sold_out"
        
        # Calculate item cost
        item_cost = float(listing.price_per_unit) * item.quantity
        total_amount += item_cost
        
        order_item = OrderItem(
            order_id=new_order.id,
            crop_listing_id=listing.id,
            quantity=item.quantity,
            price_at_purchase=listing.price_per_unit
        )
        db.add(order_item)
        order_items.append(order_item)
        
    new_order.total_amount = total_amount
    await db.commit()
    
    # Eagerly load items for response serialization
    from sqlalchemy.orm import selectinload
    res = await db.execute(
        select(Order)
        .where(Order.id == new_order.id)
        .options(selectinload(Order.items))
    )
    return res.scalars().first()

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
                "status": order.status,
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
            "status": order.status,
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

@router.patch("/orders/{id}", response_model=OrderResponse)
async def update_order_status(
    id: uuid.UUID,
    payload: OrderStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update order status with state-machine verification."""
    from sqlalchemy.orm import selectinload
    result = await db.execute(
        select(Order)
        .where(Order.id == id)
        .options(selectinload(Order.items))
        .with_for_update()
    )
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found."
        )
        
    current_status = order.status.lower()
    target_status = payload.status.lower()
    
    # State Machine Transitions check
    if current_status == target_status:
        return order
        
    if current_status in ["completed", "rejected", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot transition order from terminal state '{current_status}'"
        )
        
    # Allowed transition matrix
    allowed_transitions = {
        "pending": ["accepted", "rejected", "cancelled"],
        "accepted": ["ready", "cancelled"],
        "ready": ["completed", "cancelled"]
    }
    
    if target_status not in allowed_transitions.get(current_status, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid transition from '{current_status}' to '{target_status}'"
        )
        
    # Permissions check
    if current_user.role == "admin":
        pass
    elif current_user.role == "farmer":
        owns_items = False
        has_other_farmer_items = False
        for item in order.items:
            res_cl = await db.execute(select(CropListing).where(CropListing.id == item.crop_listing_id))
            cl = res_cl.scalars().first()
            if cl and cl.farmer_id == current_user.id:
                owns_items = True
            else:
                has_other_farmer_items = True
        if not owns_items:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this order."
            )
        if has_other_farmer_items:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Farmers cannot update multi-farmer order status."
            )
        # Farmer cannot cancel order unless they reject it, but can accept/ready/complete/reject
        if target_status == "cancelled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Farmers cannot cancel customer orders; they must reject them instead."
            )
    else: # Customer
        if order.customer_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to modify this order."
            )
        if target_status != "cancelled":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customers can only transition orders to 'cancelled'."
            )
            
    # If transitioning to rejected or cancelled, restore listing stock
    if target_status in ["rejected", "cancelled"]:
        for item in order.items:
            # Query the crop listing and lock it to update stock
            l_res = await db.execute(
                select(CropListing).where(CropListing.id == item.crop_listing_id).with_for_update()
            )
            listing = l_res.scalars().first()
            if listing:
                listing.available_quantity += item.quantity
                if listing.status == "sold_out":
                    listing.status = "active"
                    
    order.status = target_status
    await db.commit()
    
    # Reload order to return eager items
    res_reload = await db.execute(
        select(Order)
        .where(Order.id == order.id)
        .options(selectinload(Order.items))
    )
    reloaded_order = res_reload.scalars().first()
    
    if current_user.role == "farmer":
        filtered_items = []
        total_farmer_amount = 0.0
        for item in reloaded_order.items:
            res_cl = await db.execute(select(CropListing).where(CropListing.id == item.crop_listing_id))
            cl = res_cl.scalars().first()
            if cl and cl.farmer_id == current_user.id:
                item.crop_listing = cl
                filtered_items.append(item)
                total_farmer_amount += item.quantity * item.price_at_purchase
        return {
            "id": reloaded_order.id,
            "customer_id": reloaded_order.customer_id,
            "status": reloaded_order.status,
            "total_amount": total_farmer_amount,
            "items": filtered_items,
            "created_at": reloaded_order.created_at,
            "updated_at": reloaded_order.updated_at
        }
        
    return reloaded_order
