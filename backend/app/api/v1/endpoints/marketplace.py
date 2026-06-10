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
    OrderCreate, OrderResponse, OrderStatusUpdate
)

router = APIRouter()

# Instantiate role guards
farmer_guard = RoleChecker(allowed_roles=["farmer", "admin"])

@router.get("/", response_model=List[CropListingResponse])
async def read_listings(
    search: Optional[str] = Query(None, description="Search term in listing titles or description"),
    category: Optional[str] = Query(None, description="Optional unit/category filter"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve public active crop listings with search filters and pagination."""
    query = select(CropListing).where(CropListing.available_quantity > 0)
    
    if search:
        query = query.where(
            (CropListing.title.ilike(f"%{search}%")) | 
            (CropListing.description.ilike(f"%{search}%"))
        )
        
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
    if not current_user.farmer_profile:
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
        image_urls=payload.image_urls
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
            
        if listing.available_quantity < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for '{listing.title}'. Available: {listing.available_quantity}, Requested: {item.quantity}"
            )
            
        # Deduct quantity
        listing.available_quantity -= item.quantity
        
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
    await db.refresh(new_order)
    return new_order

@router.get("/orders", response_model=List[OrderResponse])
async def list_orders(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List orders. Admin sees all, Farmer sees items from their shop, Customer sees their orders."""
    if current_user.role == "admin":
        result = await db.execute(select(Order))
        return result.scalars().all()
        
    elif current_user.role == "farmer":
        # Select orders that contain at least one item belonging to this farmer's crop listings
        query = select(Order).join(OrderItem).join(CropListing).where(
            CropListing.farmer_id == current_user.id
        ).distinct()
        result = await db.execute(query)
        return result.scalars().all()
        
    else:
        # Customer sees their own orders
        result = await db.execute(select(Order).where(Order.customer_id == current_user.id))
        return result.scalars().all()

@router.get("/orders/{id}", response_model=OrderResponse)
async def read_order(
    id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Retrieve details of a single order."""
    result = await db.execute(select(Order).where(Order.id == id))
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found."
        )
        
    # Check permissions (Customer who placed it, Farmer selling, or Admin)
    if current_user.role != "admin" and order.customer_id != current_user.id:
        # Check if the farmer sells any item in this order
        farmer_item = False
        for item in order.items:
            if item.crop_listing.farmer_id == current_user.id:
                farmer_item = True
                break
        if not farmer_item:
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
    """Update order status. Farmers or Admins can ship/complete; Customers can cancel pending."""
    result = await db.execute(select(Order).where(Order.id == id).with_for_update())
    order = result.scalars().first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found."
        )
        
    target_status = payload.status.lower()
    
    if target_status not in ["pending", "shipped", "completed", "cancelled"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid target status."
        )
        
    # Permissions check
    if current_user.role == "admin":
        order.status = target_status
    elif current_user.role == "farmer":
        # Check if the farmer owns items in this order
        owns_items = any(item.crop_listing.farmer_id == current_user.id for item in order.items)
        if not owns_items:
            raise HTTPException(status_code=403, detail="Not authorized to update this order.")
            
        # Farmer can ship, complete, or cancel
        order.status = target_status
    else:
        # Customer can only cancel their own order if it is still pending
        if order.customer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not authorized.")
        if target_status != "cancelled":
            raise HTTPException(status_code=400, detail="Customers can only cancel orders.")
        if order.status != "pending":
            raise HTTPException(status_code=400, detail="Only pending orders can be cancelled.")
        
        # Restore stock if cancelled
        for item in order.items:
            item.crop_listing.available_quantity += item.quantity
            
        order.status = "cancelled"
        
    await db.commit()
    await db.refresh(order)
    return order

