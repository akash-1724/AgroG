import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import RoleChecker, get_current_user
from app.core.database import get_db
from app.models.marketplace import CropListing, Order, OrderItem
from app.models.review import Review
from app.models.user import User
from app.schemas.reviews import ReviewCreate, ReviewResponse


router = APIRouter()
customer_guard = RoleChecker(allowed_roles=["customer"])
admin_guard = RoleChecker(allowed_roles=["admin"])


async def rating_summary(db: AsyncSession, *, farmer_id: Optional[uuid.UUID] = None, listing_id: Optional[uuid.UUID] = None) -> dict:
    query = select(func.avg(Review.rating), func.count(Review.id))
    if farmer_id:
        query = query.where(Review.farmer_id == farmer_id)
    if listing_id:
        query = query.where(Review.listing_id == listing_id)
    result = await db.execute(query)
    avg, count = result.one()
    return {"average_rating": round(float(avg), 2) if avg is not None else None, "review_count": int(count or 0)}


def serialize_review(review: Review) -> dict:
    return {
        "id": review.id,
        "customer_id": review.customer_id,
        "farmer_id": review.farmer_id,
        "listing_id": review.listing_id,
        "order_id": review.order_id,
        "order_item_id": review.order_item_id,
        "rating": review.rating,
        "comment": review.comment,
        "target_type": review.target_type,
        "reviewer_name": review.customer.full_name if review.customer else None,
        "created_at": review.created_at,
        "updated_at": review.updated_at,
    }


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_review(payload: ReviewCreate, current_user: User = Depends(customer_guard), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(OrderItem)
        .join(Order)
        .join(CropListing, CropListing.id == OrderItem.crop_listing_id)
        .where(
            OrderItem.id == payload.order_item_id,
            Order.customer_id == current_user.id,
            OrderItem.status == "completed",
            CropListing.id == payload.listing_id,
        )
        .options(selectinload(OrderItem.order), selectinload(OrderItem.crop_listing))
    )
    order_item = result.scalars().first()
    if not order_item or not order_item.crop_listing:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Review requires a completed purchased item.")

    listing = order_item.crop_listing
    if listing.farmer_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Farmers cannot review their own listings.")

    duplicate = await db.execute(
        select(Review).where(
            Review.customer_id == current_user.id,
            Review.order_item_id == payload.order_item_id,
            Review.listing_id == payload.listing_id,
        )
    )
    if duplicate.scalars().first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This purchased item has already been reviewed.")

    review = Review(
        customer_id=current_user.id,
        farmer_id=listing.farmer_id,
        listing_id=listing.id,
        order_id=order_item.order_id,
        order_item_id=order_item.id,
        rating=payload.rating,
        comment=payload.comment,
        target_type=payload.target_type,
    )
    db.add(review)
    await db.commit()
    result = await db.execute(select(Review).where(Review.id == review.id).options(selectinload(Review.customer)))
    return serialize_review(result.scalars().first())


@router.get("/farmers/{farmer_id}", response_model=list[ReviewResponse])
async def list_farmer_reviews(farmer_id: uuid.UUID, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Review).where(Review.farmer_id == farmer_id).options(selectinload(Review.customer)).order_by(Review.created_at.desc()).offset(offset).limit(limit)
    )
    return [serialize_review(review) for review in result.scalars().all()]


@router.get("/listings/{listing_id}", response_model=list[ReviewResponse])
async def list_listing_reviews(listing_id: uuid.UUID, limit: int = Query(20, ge=1, le=100), offset: int = Query(0, ge=0), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Review).where(Review.listing_id == listing_id).options(selectinload(Review.customer)).order_by(Review.created_at.desc()).offset(offset).limit(limit)
    )
    return [serialize_review(review) for review in result.scalars().all()]


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(id: uuid.UUID, current_user: User = Depends(admin_guard), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Review).where(Review.id == id))
    review = result.scalars().first()
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found.")
    await db.delete(review)
    await db.commit()
