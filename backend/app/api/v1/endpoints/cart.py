import uuid
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import RoleChecker
from app.core.database import get_db
from app.models.cart import Cart, CartItem
from app.models.marketplace import CropListing, Order, OrderItem
from app.models.user import User, FarmerProfile
from app.schemas.cart import CartCheckoutResponse, CartItemCreate, CartItemUpdate, CartResponse


router = APIRouter()
customer_guard = RoleChecker(allowed_roles=["customer"])


async def get_or_create_cart(db: AsyncSession, customer_id: uuid.UUID) -> Cart:
    result = await db.execute(
        select(Cart)
        .where(Cart.customer_id == customer_id)
        .options(selectinload(Cart.items).selectinload(CartItem.crop_listing).selectinload(CropListing.farmer).selectinload(FarmerProfile.user))
    )
    cart = result.scalars().first()
    if cart:
        return cart

    cart = Cart(customer_id=customer_id)
    db.add(cart)
    await db.flush()
    return cart


async def load_cart(db: AsyncSession, cart_id: uuid.UUID) -> Cart:
    result = await db.execute(
        select(Cart)
        .where(Cart.id == cart_id)
        .options(selectinload(Cart.items).selectinload(CartItem.crop_listing).selectinload(CropListing.farmer).selectinload(FarmerProfile.user))
    )
    return result.scalars().first()


def serialize_cart(cart: Cart) -> dict:
    items: List[dict] = []
    estimated_total = 0.0
    for item in cart.items:
        listing = item.crop_listing
        if not listing:
            continue
        farmer_profile = listing.farmer
        farmer_name = farmer_profile.user.full_name if farmer_profile and farmer_profile.user else "Unknown farmer"
        subtotal = float(listing.price_per_unit) * item.quantity
        estimated_total += subtotal
        items.append({
            "id": item.id,
            "crop_listing_id": listing.id,
            "title": listing.title,
            "farmer_id": listing.farmer_id,
            "farmer_name": farmer_name,
            "unit_price": float(listing.price_per_unit),
            "unit": listing.unit,
            "quantity": item.quantity,
            "available_quantity": listing.available_quantity,
            "status": listing.status,
            "image_urls": listing.image_urls,
            "subtotal": subtotal,
        })
    return {
        "id": cart.id,
        "customer_id": cart.customer_id,
        "items": items,
        "estimated_total": estimated_total,
        "created_at": cart.created_at,
        "updated_at": cart.updated_at,
    }


async def get_active_listing(db: AsyncSession, listing_id: uuid.UUID) -> CropListing:
    result = await db.execute(select(CropListing).where(CropListing.id == listing_id))
    listing = result.scalars().first()
    if not listing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Listing not found.")
    if listing.status != "active":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Listing is not active.")
    return listing


@router.get("", response_model=CartResponse)
@router.get("/", response_model=CartResponse, include_in_schema=False)
async def read_cart(current_user: User = Depends(customer_guard), db: AsyncSession = Depends(get_db)):
    cart = await get_or_create_cart(db, current_user.id)
    await db.commit()
    cart = await load_cart(db, cart.id)
    return serialize_cart(cart)


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_201_CREATED)
async def add_cart_item(payload: CartItemCreate, current_user: User = Depends(customer_guard), db: AsyncSession = Depends(get_db)):
    listing = await get_active_listing(db, payload.crop_listing_id)
    if payload.quantity > listing.available_quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Requested quantity exceeds available stock.")

    cart = await get_or_create_cart(db, current_user.id)
    existing_result = await db.execute(
        select(CartItem).where(CartItem.cart_id == cart.id, CartItem.crop_listing_id == payload.crop_listing_id)
    )
    item = existing_result.scalars().first()
    if item:
        new_quantity = item.quantity + payload.quantity
        if new_quantity > listing.available_quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart quantity exceeds available stock.")
        item.quantity = new_quantity
    else:
        db.add(CartItem(cart_id=cart.id, crop_listing_id=payload.crop_listing_id, quantity=payload.quantity))
    cart.updated_at = datetime.utcnow()
    await db.commit()
    cart = await load_cart(db, cart.id)
    return serialize_cart(cart)


@router.patch("/items/{id}", response_model=CartResponse)
async def update_cart_item(id: uuid.UUID, payload: CartItemUpdate, current_user: User = Depends(customer_guard), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CartItem).join(Cart).where(CartItem.id == id, Cart.customer_id == current_user.id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found.")
    listing = await get_active_listing(db, item.crop_listing_id)
    if payload.quantity > listing.available_quantity:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Requested quantity exceeds available stock.")
    item.quantity = payload.quantity
    cart_id = item.cart_id
    await db.commit()
    cart = await load_cart(db, cart_id)
    return serialize_cart(cart)


@router.delete("/items/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cart_item(id: uuid.UUID, current_user: User = Depends(customer_guard), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CartItem).join(Cart).where(CartItem.id == id, Cart.customer_id == current_user.id))
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found.")
    await db.delete(item)
    await db.commit()


@router.delete("/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(current_user: User = Depends(customer_guard), db: AsyncSession = Depends(get_db)):
    cart = await get_or_create_cart(db, current_user.id)
    cart = await load_cart(db, cart.id)
    for item in list(cart.items):
        await db.delete(item)
    await db.commit()


@router.post("/checkout", response_model=CartCheckoutResponse)
async def checkout_cart(current_user: User = Depends(customer_guard), db: AsyncSession = Depends(get_db)):
    cart = await get_or_create_cart(db, current_user.id)
    cart = await load_cart(db, cart.id)
    if not cart.items:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart is empty.")

    total = 0.0
    locked_items = []
    for item in list(cart.items):
        result = await db.execute(select(CropListing).where(CropListing.id == item.crop_listing_id).with_for_update())
        listing = result.scalars().first()
        if not listing or listing.status != "active":
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cart contains inactive or missing listing.")
        if item.quantity > listing.available_quantity:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Insufficient stock for '{listing.title}'.")
        locked_items.append((item, listing))

    order = Order(customer_id=current_user.id, status="pending", total_amount=0.0)
    db.add(order)
    await db.flush()

    for item, listing in locked_items:
        listing.available_quantity -= item.quantity
        if listing.available_quantity == 0:
            listing.status = "sold_out"
        total += float(listing.price_per_unit) * item.quantity
        db.add(OrderItem(order_id=order.id, crop_listing_id=listing.id, quantity=item.quantity, price_at_purchase=listing.price_per_unit, status="pending"))
        await db.delete(item)

    cart.items.clear()
    order.total_amount = total
    await db.commit()
    result = await db.execute(select(Order).where(Order.id == order.id).options(selectinload(Order.items)))
    return {"order": result.scalars().first(), "cart_cleared": True}
