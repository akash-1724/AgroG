import argparse
import asyncio
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.educational import EducationalArticle
from app.models.marketplace import CropListing
from app.models.user import FarmerProfile, User


SAMPLE_PASSWORD = "AgroGuideDemo123!"

IMAGE_URLS = {
    "tomatoes": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=1200&q=80",
    "wheat": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?auto=format&fit=crop&w=1200&q=80",
    "potatoes": "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=1200&q=80",
    "carrots": "https://images.unsplash.com/photo-1582515073490-39981397c445?auto=format&fit=crop&w=1200&q=80",
    "seedlings": "https://images.unsplash.com/photo-1501004318641-b39e6451bec6?auto=format&fit=crop&w=1200&q=80",
    "farm": "https://images.unsplash.com/photo-1464226184884-fa280b87c399?auto=format&fit=crop&w=1200&q=80",
    "fields": "https://images.unsplash.com/photo-1523741543316-beb7fc7023d8?auto=format&fit=crop&w=1200&q=80",
}

FARMERS = [
    {
        "email": "farmer.ravi@sample.agroguide.local",
        "full_name": "Ravi Kumar",
        "phone_number": "+91-90000-10001",
        "profile": {
            "farm_name": "Green Valley Organics",
            "latitude": 12.9716,
            "longitude": 77.5946,
            "address": "Hesaraghatta Road, Bengaluru, Karnataka",
            "city": "Bengaluru",
            "district": "Bengaluru Urban",
            "state": "Karnataka",
            "description": "Organic vegetable farm specializing in tomatoes, carrots, and seasonal greens.",
            "rating": 4.8,
        },
        "listings": [
            {
                "title": "Organic Roma Tomatoes",
                "description": "Fresh hand-picked Roma tomatoes grown using compost and drip irrigation.",
                "price_per_unit": 42.0,
                "unit": "kg",
                "available_quantity": 180,
                "image_urls": IMAGE_URLS["tomatoes"],
                "category": "Vegetables",
            },
            {
                "title": "Premium Red Carrots",
                "description": "Crunchy winter carrots suitable for retail, juicing, and food processing.",
                "price_per_unit": 35.0,
                "unit": "kg",
                "available_quantity": 220,
                "image_urls": IMAGE_URLS["carrots"],
                "category": "Vegetables",
            },
        ],
    },
    {
        "email": "farmer.meera@sample.agroguide.local",
        "full_name": "Meera Patil",
        "phone_number": "+91-90000-10002",
        "profile": {
            "farm_name": "Sunrise Grain Collective",
            "latitude": 18.5204,
            "longitude": 73.8567,
            "address": "Mulshi Road, Pune, Maharashtra",
            "city": "Pune",
            "district": "Pune",
            "state": "Maharashtra",
            "description": "Family-run grain producer offering wheat, pulses, and hardy field crops.",
            "rating": 4.7,
        },
        "listings": [
            {
                "title": "Stone-Milled Wheat Grain",
                "description": "Cleaned wheat grain from low-input cultivation, ready for milling or wholesale.",
                "price_per_unit": 28.0,
                "unit": "kg",
                "available_quantity": 1200,
                "image_urls": IMAGE_URLS["wheat"],
                "category": "Grains",
            },
            {
                "title": "Table Potatoes",
                "description": "Medium-size potatoes graded for kitchens, restaurants, and local stores.",
                "price_per_unit": 24.0,
                "unit": "kg",
                "available_quantity": 600,
                "image_urls": IMAGE_URLS["potatoes"],
                "category": "Vegetables",
            },
        ],
    },
    {
        "email": "farmer.ananya@sample.agroguide.local",
        "full_name": "Ananya Singh",
        "phone_number": "+91-90000-10003",
        "profile": {
            "farm_name": "Riverbend Seedlings",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "address": "Najafgarh Farm Belt, New Delhi",
            "city": "New Delhi",
            "district": "South West Delhi",
            "state": "Delhi",
            "description": "Nursery and demonstration farm for vegetable seedlings and advisory trials.",
            "rating": 4.6,
        },
        "listings": [
            {
                "title": "Mixed Vegetable Seedlings Tray",
                "description": "Healthy seedlings for tomato, chilli, brinjal, and seasonal kitchen garden crops.",
                "price_per_unit": 120.0,
                "unit": "tray",
                "available_quantity": 90,
                "image_urls": IMAGE_URLS["seedlings"],
                "category": "Seedlings",
            },
            {
                "title": "Farm Visit Advisory Slot",
                "description": "Guided on-farm advisory visit for soil preparation, nursery setup, and pest checks.",
                "price_per_unit": 750.0,
                "unit": "slot",
                "available_quantity": 12,
                "image_urls": IMAGE_URLS["farm"],
                "category": "Services",
            },
        ],
    },
]

ARTICLES = [
    {
        "title": "How to Read Soil N-P-K Reports Before Planting",
        "slug": "read-soil-npk-reports-before-planting",
        "summary": "A practical guide to interpreting nitrogen, phosphorus, potassium, and pH values before choosing a crop.",
        "content": "Start with pH, then compare nitrogen, phosphorus, and potassium against the crop requirement. Use local weather and irrigation availability before final crop selection.",
        "category": "Soil Health",
        "tags": ["soil", "npk", "planning"],
        "crop_tags": ["wheat", "tomato", "rice"],
        "media_url": IMAGE_URLS["fields"],
        "language": "en",
        "status": "published",
    },
    {
        "title": "Safe Fertilizer Use for Small Farms",
        "slug": "safe-fertilizer-use-small-farms",
        "summary": "Simple safety checks for storing, mixing, and applying fertilizer without overuse.",
        "content": "Avoid applying fertilizer before heavy rain, store bags away from moisture, and keep records of every application. Always follow label instructions and local extension advice.",
        "category": "Fertilizer",
        "tags": ["fertilizer", "safety", "nutrients"],
        "crop_tags": ["vegetables", "grains"],
        "media_url": IMAGE_URLS["farm"],
        "language": "en",
        "status": "published",
    },
    {
        "title": "Leaf Photo Tips for Better Disease Diagnosis",
        "slug": "leaf-photo-tips-disease-diagnosis",
        "summary": "How to capture leaf images that are easier for diagnostic tools and agronomists to interpret.",
        "content": "Photograph both healthy and affected leaves in natural light. Keep the leaf in focus, avoid shadows, and include the top and underside when possible.",
        "category": "Plant Health",
        "tags": ["disease", "diagnosis", "leaf"],
        "crop_tags": ["tomato", "potato", "vegetables"],
        "media_url": IMAGE_URLS["seedlings"],
        "language": "en",
        "status": "published",
    },
]


def iter_image_urls() -> list[str]:
    urls = set(IMAGE_URLS.values())
    for farmer in FARMERS:
        for listing in farmer["listings"]:
            urls.update(str(listing["image_urls"]).split(","))
    for article in ARTICLES:
        urls.add(str(article["media_url"]))
    return sorted(url.strip() for url in urls if url.strip())


async def check_image_urls() -> bool:
    all_ok = True
    async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
        for url in iter_image_urls():
            try:
                response = await client.get(url)
                content_type = response.headers.get("content-type", "")
                ok = response.status_code < 400 and content_type.startswith("image/")
            except httpx.HTTPError:
                ok = False
                response = None
                content_type = ""

            status_code = response.status_code if response is not None else "ERR"
            print(f"{status_code} {content_type or 'unknown'} {url}")
            all_ok = all_ok and ok
    return all_ok


async def upsert_user(session: AsyncSession, payload: dict[str, Any], role: str) -> User:
    result = await session.execute(select(User).where(User.email == payload["email"]))
    user = result.scalars().first()

    if not user:
        user = User(email=payload["email"], password_hash=get_password_hash(SAMPLE_PASSWORD))
        session.add(user)

    user.full_name = payload["full_name"]
    user.phone_number = payload.get("phone_number")
    user.role = role
    user.password_hash = get_password_hash(SAMPLE_PASSWORD)
    await session.flush()
    return user


async def upsert_farmer_profile(session: AsyncSession, user: User, profile_payload: dict[str, Any]) -> None:
    result = await session.execute(select(FarmerProfile).where(FarmerProfile.user_id == user.id))
    profile = result.scalars().first()

    if not profile:
        profile = FarmerProfile(user_id=user.id)
        session.add(profile)

    for key, value in profile_payload.items():
        setattr(profile, key, value)


async def upsert_listing(session: AsyncSession, farmer_id: Any, payload: dict[str, Any]) -> None:
    result = await session.execute(
        select(CropListing).where(
            CropListing.farmer_id == farmer_id,
            CropListing.title == payload["title"],
        )
    )
    listing = result.scalars().first()

    if not listing:
        listing = CropListing(farmer_id=farmer_id, title=payload["title"])
        session.add(listing)

    for key, value in payload.items():
        setattr(listing, key, value)
    listing.status = "active"


async def upsert_article(session: AsyncSession, author_id: Any, payload: dict[str, Any]) -> None:
    result = await session.execute(select(EducationalArticle).where(EducationalArticle.slug == payload["slug"]))
    article = result.scalars().first()

    if not article:
        article = EducationalArticle(author_id=author_id, slug=payload["slug"])
        session.add(article)

    article.author_id = author_id
    for key, value in payload.items():
        setattr(article, key, value)


async def seed_sample_data() -> None:
    async with SessionLocal() as session:
        admin = await upsert_user(
            session,
            {
                "email": "admin@sample.agroguide.local",
                "full_name": "Sample Admin",
                "phone_number": "+91-90000-10000",
            },
            "admin",
        )
        await upsert_user(
            session,
            {
                "email": "buyer@sample.agroguide.local",
                "full_name": "Sample Buyer",
                "phone_number": "+91-90000-10009",
            },
            "customer",
        )

        for farmer_payload in FARMERS:
            farmer = await upsert_user(session, farmer_payload, "farmer")
            await upsert_farmer_profile(session, farmer, farmer_payload["profile"])
            for listing_payload in farmer_payload["listings"]:
                await upsert_listing(session, farmer.id, listing_payload)

        for article_payload in ARTICLES:
            await upsert_article(session, admin.id, article_payload)

        await session.commit()

    print("Seeded sample users, farmers, listings, and educational articles.")
    print(f"Sample password for all seeded users: {SAMPLE_PASSWORD}")


async def main() -> int:
    parser = argparse.ArgumentParser(description="Seed AgroGuide sample data.")
    parser.add_argument("--check-images-only", action="store_true", help="Only validate remote sample image URLs.")
    parser.add_argument("--skip-image-check", action="store_true", help="Seed without validating image URLs first.")
    args = parser.parse_args()

    if not args.skip_image_check:
        images_ok = await check_image_urls()
        if not images_ok:
            print("One or more sample image URLs failed validation.")
            return 1

    if args.check_images_only:
        return 0

    await seed_sample_data()
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
