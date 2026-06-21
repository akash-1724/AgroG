import pytest
import uuid
import math
from datetime import date, datetime
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import event, select

from app.main import app
from app.core.database import get_db
from app.core.security import get_password_hash
from app.models.base import Base
from app.models.user import User, FarmerProfile
from app.models.marketplace import CropListing, ListingImage, Order, OrderItem
from app.models.review import Review
from app.models.intelligence import CropPriceRecord
from app.schemas.intelligence import WeatherData, WeatherResponse

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

# Register PostgreSQL functions for SQLite test database compatibility
@event.listens_for(engine.sync_engine, "connect")
def db_connect(dbapi_connection, connection_record):
    dbapi_connection.create_function("least", 2, min)
    dbapi_connection.create_function("greatest", 2, max)
    dbapi_connection.create_function("acos", 1, math.acos)
    dbapi_connection.create_function("cos", 1, math.cos)
    dbapi_connection.create_function("sin", 1, math.sin)
    dbapi_connection.create_function("radians", 1, math.radians)

@pytest.fixture(scope="session", autouse=True)
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="function")
async def db_session():
    # Setup test tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
        
    # Teardown test tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        try:
            yield db_session
            await db_session.commit()
        except Exception:
            await db_session.rollback()
            raise
            
    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

# 1. Health endpoint test
@pytest.mark.anyio
async def test_health_check(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

# 2. Auth flow & registration tests
@pytest.mark.anyio
async def test_auth_registration_and_login(client):
    # Register customer
    reg_data = {
        "email": "test_buyer@example.com",
        "password": "buyerpassword123",
        "full_name": "Test Buyer",
        "phone_number": "1234567890",
        "role": "customer"
    }
    reg_response = await client.post("/api/v1/auth/register", json=reg_data)
    assert reg_response.status_code == 201
    
    # Login (expects OAuth2 form data urlencoded)
    login_data = {
        "username": "test_buyer@example.com",
        "password": "buyerpassword123"
    }
    login_response = await client.post("/api/v1/auth/token", data=login_data)
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    
    # Query Profile
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    profile_response = await client.get("/api/v1/auth/me", headers=headers)
    assert profile_response.status_code == 200
    assert profile_response.json()["email"] == "test_buyer@example.com"
    
    # Logout/Token revocation
    logout_response = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": tokens["refresh_token"]},
        headers=headers
    )
    assert logout_response.status_code == 200

# 2b. Refresh Token Rotation, Reuse, and Logout tests
@pytest.mark.anyio
async def test_refresh_token_rotation_and_revocation(client):
    email = "rotation@example.com"
    pwd = "rotationpassword"
    reg_data = {
        "email": email,
        "password": pwd,
        "full_name": "Rotation Test",
        "role": "customer"
    }
    await client.post("/api/v1/auth/register", json=reg_data)
    
    login_response = await client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": pwd}
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    first_refresh = tokens["refresh_token"]

    # 1. First refresh should work and rotate
    refresh_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first_refresh}
    )
    assert refresh_res.status_code == 200
    rotated_tokens = refresh_res.json()
    second_refresh = rotated_tokens["refresh_token"]
    assert first_refresh != second_refresh

    # 2. Reuse of first refresh token should be blocked and trigger revocation
    reuse_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": first_refresh}
    )
    assert reuse_res.status_code == 401
    assert "Compromised session" in reuse_res.json()["detail"]

    # 3. Verify that the second refresh token is now also invalid
    stale_refresh_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": second_refresh}
    )
    assert stale_refresh_res.status_code == 401

    # 4. Verify logout with new login
    login_response_new = await client.post(
        "/api/v1/auth/token",
        data={"username": email, "password": pwd}
    )
    new_tokens = login_response_new.json()
    active_refresh = new_tokens["refresh_token"]

    # Logout
    logout_res = await client.post(
        "/api/v1/auth/logout",
        json={"refresh_token": active_refresh},
        headers={"Authorization": f"Bearer {new_tokens['access_token']}"}
    )
    assert logout_res.status_code == 200

    # Token should now be invalid
    post_logout_res = await client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": active_refresh}
    )
    assert post_logout_res.status_code == 401

# 3. RBAC validation
@pytest.mark.anyio
async def test_rbac_guard(client):
    # Register customer
    reg_buyer = {
        "email": "buyer@example.com",
        "password": "password123",
        "full_name": "Farmer Joe",
        "role": "customer"
    }
    await client.post("/api/v1/auth/register", json=reg_buyer)
    
    # Login
    login_res = await client.post("/api/v1/auth/token", data={"username": "buyer@example.com", "password": "password123"})
    token = login_res.json()["access_token"]
    
    # Try updating farm location (requires farmer role)
    headers = {"Authorization": f"Bearer {token}"}
    location_payload = {
        "latitude": 12.9716,
        "longitude": 77.5946,
        "address": "123 Green Valley Farm",
        "city": "Bengaluru",
        "location_visibility": True
    }
    response = await client.patch("/api/v1/farmers/me/location", json=location_payload, headers=headers)
    assert response.status_code == 403

# 4. Nearby Farmer Discovery Privacy Rounded Coordinate check
@pytest.mark.anyio
async def test_nearby_farmer_discovery(client):
    # Register farmer
    reg_farmer = {
        "email": "joe@example.com",
        "password": "joe_password_123",
        "full_name": "Joe Green",
        "role": "farmer",
        "farmer_details": {
            "farm_name": "Joe's Organic Farms",
            "latitude": 12.971593,
            "longitude": 77.594562,
            "address": "123 Farm Lane, Bangalore"
        }
    }
    await client.post("/api/v1/auth/register", json=reg_farmer)
    
    # Search nearby (Bengaluru coordinates)
    response = await client.get("/api/v1/farmers/nearby?lat=12.9716&lon=77.5946&radius=10")
    assert response.status_code == 200
    results = response.json()
    assert len(results) > 0
    
    # Latitude and longitude must be rounded to 2 decimal places to maintain privacy
    assert results[0]["latitude"] == 12.97
    assert results[0]["longitude"] == 77.59

# 5. Assistant Safety Warning interceptor
@pytest.mark.anyio
async def test_assistant_safety_filters(client):
    # Register & Login user
    reg_user = {
        "email": "user@example.com",
        "password": "userpassword123",
        "full_name": "Chatter",
        "role": "customer"
    }
    await client.post("/api/v1/auth/register", json=reg_user)
    login_res = await client.post("/api/v1/auth/token", data={"username": "user@example.com", "password": "userpassword123"})
    token = login_res.json()["access_token"]
    
    # Query assistant with toxic message
    headers = {"Authorization": f"Bearer {token}"}
    response = await client.post(
        "/api/v1/assistant/chat",
        json={"message": "What is the lethal dose of poison to kill crops?"},
        headers=headers
    )
    assert response.status_code == 200
    assert "toxic chemical" in response.json()["answer"]
    assert response.json()["provider_status"] == "safety_block"


async def register_and_login(client, email: str, role: str, farmer_details: dict | None = None):
    payload = {
        "email": email,
        "password": "password123",
        "full_name": email.split("@")[0].replace("_", " ").title(),
        "role": role,
    }
    if farmer_details:
        payload["farmer_details"] = farmer_details
    response = await client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    token_response = await client.post("/api/v1/auth/token", data={"username": email, "password": "password123"})
    assert token_response.status_code == 200
    token = token_response.json()["access_token"]
    profile = await client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert profile.status_code == 200
    return profile.json(), {"Authorization": f"Bearer {token}"}


async def create_farmer_listing(client, farmer_headers, quantity: int = 10):
    payload = {
        "title": "Fresh Test Tomatoes",
        "description": "Fresh tomatoes grown for test checkout flows.",
        "price_per_unit": 12.5,
        "unit": "kg",
        "available_quantity": quantity,
        "category": "Vegetables",
        "status": "active",
    }
    response = await client.post("/api/v1/marketplace/listings", json=payload, headers=farmer_headers)
    assert response.status_code == 201
    return response.json()


@pytest.mark.anyio
async def test_cart_add_update_remove_clear_and_checkout(client, db_session):
    _, farmer_headers = await register_and_login(
        client,
        "cart_farmer@example.com",
        "farmer",
        {"farm_name": "Cart Farm", "latitude": 12.9, "longitude": 77.5, "address": "Cart Farm Road"},
    )
    _, customer_headers = await register_and_login(client, "cart_customer@example.com", "customer")
    listing = await create_farmer_listing(client, farmer_headers, quantity=5)

    response = await client.post(
        "/api/v1/cart/items",
        json={"crop_listing_id": listing["id"], "quantity": 2},
        headers=customer_headers,
    )
    assert response.status_code == 201
    cart = response.json()
    assert cart["items"][0]["quantity"] == 2
    assert cart["estimated_total"] == 25.0

    item_id = cart["items"][0]["id"]
    response = await client.patch(f"/api/v1/cart/items/{item_id}", json={"quantity": 3}, headers=customer_headers)
    assert response.status_code == 200
    assert response.json()["items"][0]["quantity"] == 3

    overstock = await client.patch(f"/api/v1/cart/items/{item_id}", json={"quantity": 99}, headers=customer_headers)
    assert overstock.status_code == 400

    _, other_customer_headers = await register_and_login(client, "cart_other@example.com", "customer")
    blocked = await client.patch(f"/api/v1/cart/items/{item_id}", json={"quantity": 1}, headers=other_customer_headers)
    assert blocked.status_code == 404

    direct_order = await client.post(
        "/api/v1/marketplace/orders",
        json={"items": [{"crop_listing_id": listing["id"], "quantity": 1}]},
        headers=customer_headers,
    )
    assert direct_order.status_code == 400
    assert "cart checkout" in direct_order.json()["detail"]

    empty_checkout = await client.post("/api/v1/cart/checkout", headers=other_customer_headers)
    assert empty_checkout.status_code == 400

    removed = await client.delete(f"/api/v1/cart/items/{item_id}", headers=customer_headers)
    assert removed.status_code == 204

    await client.post("/api/v1/cart/items", json={"crop_listing_id": listing["id"], "quantity": 2}, headers=customer_headers)
    checkout = await client.post("/api/v1/cart/checkout", headers=customer_headers)
    assert checkout.status_code == 200
    assert checkout.json()["cart_cleared"] is True

    empty_cart = await client.get("/api/v1/cart", headers=customer_headers)
    assert empty_cart.status_code == 200
    assert empty_cart.json()["items"] == []

    result = await db_session.execute(select(CropListing).where(CropListing.id == uuid.UUID(listing["id"])))
    assert result.scalars().first().available_quantity == 3


@pytest.mark.anyio
async def test_public_farmer_profile_filters_private_coordinates_and_inactive_listings(client):
    farmer, farmer_headers = await register_and_login(
        client,
        "profile_farmer@example.com",
        "farmer",
        {"farm_name": "Profile Farm", "latitude": 12.9, "longitude": 77.5, "address": "Profile Farm Road"},
    )
    active = await create_farmer_listing(client, farmer_headers, quantity=4)
    inactive_payload = {
        "title": "Inactive Test Crop",
        "description": "This listing should not be public on profile.",
        "price_per_unit": 9,
        "unit": "kg",
        "available_quantity": 1,
        "category": "Vegetables",
        "status": "inactive",
    }
    inactive = await client.post("/api/v1/marketplace/listings", json=inactive_payload, headers=farmer_headers)
    assert inactive.status_code == 201

    response = await client.get(f"/api/v1/farmers/{farmer['id']}/public")
    assert response.status_code == 200
    profile = response.json()
    assert "latitude" not in profile
    assert "longitude" not in profile
    assert profile["farm_name"] == "Profile Farm"
    assert [item["id"] for item in profile["active_listings"]] == [active["id"]]


@pytest.mark.anyio
async def test_reviews_eligibility_duplicates_aggregation_and_admin_delete(client, db_session):
    farmer, farmer_headers = await register_and_login(
        client,
        "review_farmer@example.com",
        "farmer",
        {"farm_name": "Review Farm", "latitude": 12.9, "longitude": 77.5, "address": "Review Farm Road"},
    )
    _, customer_headers = await register_and_login(client, "review_customer@example.com", "customer")
    admin = User(
        email="review_admin@example.com",
        password_hash=get_password_hash("password123"),
        full_name="Review Admin",
        role="admin",
    )
    db_session.add(admin)
    await db_session.commit()
    admin_login = await client.post("/api/v1/auth/token", data={"username": "review_admin@example.com", "password": "password123"})
    assert admin_login.status_code == 200
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
    listing = await create_farmer_listing(client, farmer_headers, quantity=6)

    await client.post("/api/v1/cart/items", json={"crop_listing_id": listing["id"], "quantity": 1}, headers=customer_headers)
    checkout = await client.post("/api/v1/cart/checkout", headers=customer_headers)
    assert checkout.status_code == 200
    order = checkout.json()["order"]

    premature_review_payload = {
        "rating": 4,
        "comment": "Good produce and smooth pickup.",
        "listing_id": listing["id"],
        "order_item_id": order["items"][0]["id"],
    }
    premature = await client.post("/api/v1/reviews", json=premature_review_payload, headers=customer_headers)
    assert premature.status_code == 403

    result = await db_session.execute(select(OrderItem).where(OrderItem.id == uuid.UUID(order["items"][0]["id"])))
    db_item = result.scalars().first()
    db_item.status = "completed"
    await db_session.commit()

    review_payload = premature_review_payload
    response = await client.post("/api/v1/reviews", json=review_payload, headers=customer_headers)
    assert response.status_code == 201
    review = response.json()

    duplicate = await client.post("/api/v1/reviews", json=review_payload, headers=customer_headers)
    assert duplicate.status_code == 400

    farmer_self_review = await client.post("/api/v1/reviews", json=review_payload, headers=farmer_headers)
    assert farmer_self_review.status_code == 403

    listing_reviews = await client.get(f"/api/v1/reviews/listings/{listing['id']}")
    assert listing_reviews.status_code == 200
    assert len(listing_reviews.json()) == 1

    profile = await client.get(f"/api/v1/farmers/{farmer['id']}/public")
    assert profile.status_code == 200
    assert profile.json()["average_rating"] == 4.0
    assert profile.json()["review_count"] == 1

    deleted = await client.delete(f"/api/v1/reviews/{review['id']}", headers=admin_headers)
    assert deleted.status_code == 204
    count = await db_session.execute(select(Review))
    assert count.scalars().all() == []


@pytest.mark.anyio
async def test_weather_current_success_normalization(client, monkeypatch):
    class StubWeatherProvider:
        async def get_current_weather(self, latitude: float, longitude: float):
            return WeatherResponse(
                available=True,
                provider="test-weather",
                provider_status="available",
                weather=WeatherData(
                    temperature=28.5,
                    humidity=61.0,
                    precipitation=0.2,
                    rainfall=0.1,
                    forecast_window="current",
                    latitude=latitude,
                    longitude=longitude,
                    timestamp=datetime(2026, 6, 19, 12, 0, 0),
                    provider="test-weather",
                    provider_status="available",
                ),
            )

    monkeypatch.setattr("app.api.v1.endpoints.weather.get_weather_provider", lambda: StubWeatherProvider())

    response = await client.get("/api/v1/weather/current?lat=12.97&lon=77.59")

    assert response.status_code == 200
    body = response.json()
    assert body["available"] is True
    assert body["provider_status"] == "available"
    assert body["weather"]["temperature"] == 28.5
    assert body["weather"]["rainfall"] == 0.1
    assert body["weather"]["latitude"] == 12.97
    assert body["weather"]["longitude"] == 77.59


@pytest.mark.anyio
async def test_weather_current_unavailable_response(client, monkeypatch):
    class StubWeatherProvider:
        async def get_current_weather(self, latitude: float, longitude: float):
            return WeatherResponse(
                available=False,
                provider="test-weather",
                provider_status="unavailable",
                warning="provider down",
            )

    monkeypatch.setattr("app.api.v1.endpoints.weather.get_weather_provider", lambda: StubWeatherProvider())

    response = await client.get("/api/v1/weather/current?lat=12.97&lon=77.59")

    assert response.status_code == 200
    body = response.json()
    assert body["available"] is False
    assert body["weather"] is None
    assert body["provider_status"] == "unavailable"
    assert body["warning"] == "provider down"


@pytest.mark.anyio
async def test_weather_aware_crop_recommendation_uses_weather(client, monkeypatch):
    async def fake_crop_prediction(payload):
        assert payload.temperature == 29.0
        assert payload.humidity == 65.0
        assert payload.rainfall == 10.0
        return ([{"crop": "rice"}], "demo", "", "")

    class StubWeatherProvider:
        async def get_current_weather(self, latitude: float, longitude: float):
            return WeatherResponse(
                available=True,
                provider="test-weather",
                provider_status="available",
                weather=WeatherData(
                    temperature=29.0,
                    humidity=65.0,
                    precipitation=1.5,
                    rainfall=None,
                    forecast_window="current",
                    latitude=latitude,
                    longitude=longitude,
                    timestamp=datetime(2026, 6, 19, 12, 0, 0),
                    provider="test-weather",
                    provider_status="available",
                ),
            )

    monkeypatch.setattr("app.api.v1.endpoints.recommendations._fetch_crop_recommendations", fake_crop_prediction)
    monkeypatch.setattr("app.api.v1.endpoints.recommendations.get_weather_provider", lambda: StubWeatherProvider())

    response = await client.post(
        "/api/v1/recommendations/crop/weather-aware",
        json={
            "nitrogen": 90,
            "phosphorus": 40,
            "potassium": 40,
            "ph": 6.5,
            "temperature": 25,
            "humidity": 50,
            "rainfall": 20,
            "latitude": 12.97,
            "longitude": 77.59,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["used_weather"] is True
    assert body["provider_status"] == "available"
    assert body["recommended_crops"] == ["rice"]
    assert body["weather"]["precipitation"] == 1.5


@pytest.mark.anyio
async def test_weather_aware_crop_recommendation_falls_back_when_weather_unavailable(client, monkeypatch):
    async def fake_crop_prediction(payload):
        assert payload.temperature == 25
        assert payload.humidity == 50
        assert payload.rainfall == 20
        return (["maize"], "demo", "", "")

    class StubWeatherProvider:
        async def get_current_weather(self, latitude: float, longitude: float):
            return WeatherResponse(
                available=False,
                provider="test-weather",
                provider_status="unavailable",
                warning="provider down",
            )

    monkeypatch.setattr("app.api.v1.endpoints.recommendations._fetch_crop_recommendations", fake_crop_prediction)
    monkeypatch.setattr("app.api.v1.endpoints.recommendations.get_weather_provider", lambda: StubWeatherProvider())

    response = await client.post(
        "/api/v1/recommendations/crop/weather-aware",
        json={
            "nitrogen": 90,
            "phosphorus": 40,
            "potassium": 40,
            "ph": 6.5,
            "temperature": 25,
            "humidity": 50,
            "rainfall": 20,
            "latitude": 12.97,
            "longitude": 77.59,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["used_weather"] is False
    assert body["provider_status"] == "unavailable"
    assert body["weather"] is None
    assert body["weather_warning"] == "provider down"
    assert body["recommended_crops"] == ["maize"]


@pytest.mark.anyio
async def test_weather_aware_crop_recommendation_uses_farmer_profile_location(client, monkeypatch):
    _, farmer_headers = await register_and_login(
        client,
        "weather_farmer@example.com",
        "farmer",
        {"farm_name": "Weather Farm", "latitude": 11.11, "longitude": 22.22, "address": "Weather Road"},
    )

    async def fake_crop_prediction(payload):
        return (["wheat"], "demo", "", "")

    class StubWeatherProvider:
        async def get_current_weather(self, latitude: float, longitude: float):
            assert latitude == 11.11
            assert longitude == 22.22
            return WeatherResponse(
                available=True,
                provider="test-weather",
                provider_status="available",
                weather=WeatherData(
                    temperature=21.0,
                    humidity=55.0,
                    precipitation=0.0,
                    rainfall=0.0,
                    forecast_window="current",
                    latitude=latitude,
                    longitude=longitude,
                    timestamp=datetime(2026, 6, 19, 12, 0, 0),
                    provider="test-weather",
                    provider_status="available",
                ),
            )

    monkeypatch.setattr("app.api.v1.endpoints.recommendations._fetch_crop_recommendations", fake_crop_prediction)
    monkeypatch.setattr("app.api.v1.endpoints.recommendations.get_weather_provider", lambda: StubWeatherProvider())

    response = await client.post(
        "/api/v1/recommendations/crop/weather-aware",
        json={
            "nitrogen": 75,
            "phosphorus": 35,
            "potassium": 30,
            "ph": 6.8,
            "temperature": 25,
            "humidity": 50,
            "rainfall": 20,
        },
        headers=farmer_headers,
    )

    assert response.status_code == 200
    body = response.json()
    assert body["used_weather"] is True
    assert body["weather"]["latitude"] == 11.11
    assert body["weather"]["longitude"] == 22.22


@pytest.mark.anyio
async def test_price_catalog_and_trends_include_sample_labels(client, db_session):
    db_session.add_all([
        CropPriceRecord(
            crop_name="Tomato",
            market="Bengaluru Mandi",
            district="Bengaluru Urban",
            state="Karnataka",
            min_price=900,
            max_price=1300,
            modal_price=1100,
            unit="quintal",
            recorded_date=date(2026, 6, 18),
            source="Test Sample Prices",
            is_sample=True,
        ),
        CropPriceRecord(
            crop_name="Wheat",
            market="Indore Mandi",
            district="Indore",
            state="Madhya Pradesh",
            min_price=2200,
            max_price=2480,
            modal_price=2350,
            unit="quintal",
            recorded_date=date(2026, 6, 18),
            source="Test Sample Prices",
            is_sample=True,
        ),
    ])
    await db_session.commit()

    catalog = await client.get("/api/v1/prices/crops")
    assert catalog.status_code == 200
    catalog_body = catalog.json()
    assert catalog_body["provider_status"] == "available"
    assert catalog_body["disclaimer"]
    assert {item["crop_name"] for item in catalog_body["crops"]} == {"Tomato", "Wheat"}

    trends = await client.get("/api/v1/prices/trends?crop=Tomato&state=Karnataka")
    assert trends.status_code == 200
    trends_body = trends.json()
    assert trends_body["provider_status"] == "available"
    assert trends_body["is_sample"] is True
    assert trends_body["records"][0]["crop_name"] == "Tomato"
    assert trends_body["records"][0]["source"] == "Test Sample Prices"


@pytest.mark.anyio
async def test_price_trends_no_data_response(client):
    response = await client.get("/api/v1/prices/trends?crop=Dragonfruit")

    assert response.status_code == 200
    body = response.json()
    assert body["provider_status"] == "no_data"
    assert body["records"] == []
    assert body["is_sample"] is False


@pytest.mark.anyio
async def test_recommendation_history_persistence_ownership_and_delete(client, monkeypatch):
    _, owner_headers = await register_and_login(client, "history_owner@example.com", "customer")
    _, other_headers = await register_and_login(client, "history_other@example.com", "customer")

    async def fake_crop_prediction(payload):
        return (["rice"], "demo", "", "")

    monkeypatch.setattr("app.api.v1.endpoints.recommendations._fetch_crop_recommendations", fake_crop_prediction)

    created = await client.post(
        "/api/v1/recommendations/crop/weather-aware",
        json={
            "nitrogen": 90,
            "phosphorus": 40,
            "potassium": 40,
            "ph": 6.5,
            "temperature": 25,
            "humidity": 50,
            "rainfall": 20,
            "use_profile_location": False,
        },
        headers=owner_headers,
    )
    assert created.status_code == 200

    listing = await client.get("/api/v1/recommendations/history", headers=owner_headers)
    assert listing.status_code == 200
    history_items = listing.json()
    assert len(history_items) == 1
    assert history_items[0]["recommendation_type"] == "crop"
    assert history_items[0]["used_weather"] is False

    history_id = history_items[0]["id"]
    detail = await client.get(f"/api/v1/recommendations/history/{history_id}", headers=owner_headers)
    assert detail.status_code == 200
    detail_body = detail.json()
    assert detail_body["input_payload"]["nitrogen"] == 90
    assert detail_body["result_payload"]["recommended_crops"] == ["rice"]

    blocked_detail = await client.get(f"/api/v1/recommendations/history/{history_id}", headers=other_headers)
    assert blocked_detail.status_code == 404

    blocked_delete = await client.delete(f"/api/v1/recommendations/history/{history_id}", headers=other_headers)
    assert blocked_delete.status_code == 404

    deleted = await client.delete(f"/api/v1/recommendations/history/{history_id}", headers=owner_headers)
    assert deleted.status_code == 204

    after_delete = await client.get("/api/v1/recommendations/history", headers=owner_headers)
    assert after_delete.status_code == 200
    assert after_delete.json() == []


@pytest.mark.anyio
async def test_admin_analytics_overview_real_data_and_rbac(client, db_session):
    _, customer_headers = await register_and_login(client, "analytics_customer@example.com", "customer")
    _, farmer_headers = await register_and_login(
        client,
        "analytics_farmer@example.com",
        "farmer",
        {"farm_name": "Analytics Farm", "latitude": 12.9, "longitude": 77.5, "address": "Analytics Road"},
    )
    admin = User(email="analytics_admin@example.com", password_hash=get_password_hash("password123"), full_name="Analytics Admin", role="admin")
    db_session.add(admin)
    await db_session.commit()
    admin_login = await client.post("/api/v1/auth/token", data={"username": "analytics_admin@example.com", "password": "password123"})
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
    listing = await create_farmer_listing(client, farmer_headers, quantity=4)
    await client.post("/api/v1/cart/items", json={"crop_listing_id": listing["id"], "quantity": 2}, headers=customer_headers)
    await client.post("/api/v1/cart/checkout", headers=customer_headers)

    blocked = await client.get("/api/v1/admin/analytics/overview", headers=customer_headers)
    assert blocked.status_code == 403

    response = await client.get("/api/v1/admin/analytics/overview", headers=admin_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["users"]["total"] >= 3
    assert body["users"]["by_role"]["admin"] >= 1
    assert body["listings"]["total"] == 1
    assert body["orders"]["total"] == 1
    assert body["orders"]["gross_value"] == 25.0


@pytest.mark.anyio
async def test_listing_image_upload_validation_ownership_and_admin_override(client, db_session, monkeypatch):
    class StubStorageProvider:
        async def upload_listing_image(self, file, content):
            return {"secure_url": "https://cdn.example.com/listing.png", "public_id": "listing/test"}

    monkeypatch.setattr("app.api.v1.endpoints.marketplace.get_storage_provider", lambda: StubStorageProvider())
    _, farmer_headers = await register_and_login(
        client,
        "image_farmer@example.com",
        "farmer",
        {"farm_name": "Image Farm", "latitude": 12.9, "longitude": 77.5, "address": "Image Road"},
    )
    _, other_farmer_headers = await register_and_login(
        client,
        "image_other@example.com",
        "farmer",
        {"farm_name": "Other Image Farm", "latitude": 12.8, "longitude": 77.4, "address": "Other Road"},
    )
    admin = User(email="image_admin@example.com", password_hash=get_password_hash("password123"), full_name="Image Admin", role="admin")
    db_session.add(admin)
    await db_session.commit()
    admin_login = await client.post("/api/v1/auth/token", data={"username": "image_admin@example.com", "password": "password123"})
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}
    listing = await create_farmer_listing(client, farmer_headers, quantity=3)

    invalid = await client.post(
        f"/api/v1/marketplace/listings/{listing['id']}/images",
        files={"file": ("bad.txt", b"not image", "text/plain")},
        headers=farmer_headers,
    )
    assert invalid.status_code == 400

    blocked = await client.post(
        f"/api/v1/marketplace/listings/{listing['id']}/images",
        files={"file": ("crop.png", b"image bytes", "image/png")},
        headers=other_farmer_headers,
    )
    assert blocked.status_code == 403

    uploaded = await client.post(
        f"/api/v1/marketplace/listings/{listing['id']}/images",
        files={"file": ("crop.png", b"image bytes", "image/png")},
        headers=farmer_headers,
    )
    assert uploaded.status_code == 201
    image = uploaded.json()["image"]
    assert image["image_url"] == "https://cdn.example.com/listing.png"
    assert image["is_primary"] is True

    detail = await client.get(f"/api/v1/marketplace/listings/{listing['id']}")
    assert detail.status_code == 200
    assert detail.json()["primary_image_url"] == "https://cdn.example.com/listing.png"

    deleted = await client.delete(f"/api/v1/marketplace/listings/{listing['id']}/images/{image['id']}", headers=farmer_headers)
    assert deleted.status_code == 204

    admin_uploaded = await client.post(
        f"/api/v1/marketplace/listings/{listing['id']}/images",
        files={"file": ("admin.png", b"image bytes", "image/png")},
        headers=admin_headers,
    )
    assert admin_uploaded.status_code == 201


@pytest.mark.anyio
async def test_listing_image_upload_missing_storage_config(client, monkeypatch):
    def missing_provider():
        from fastapi import HTTPException
        raise HTTPException(status_code=503, detail="Listing image storage is not configured.")

    monkeypatch.setattr("app.api.v1.endpoints.marketplace.get_storage_provider", missing_provider)
    _, farmer_headers = await register_and_login(
        client,
        "missing_storage_farmer@example.com",
        "farmer",
        {"farm_name": "No Storage Farm", "latitude": 12.9, "longitude": 77.5, "address": "No Storage Road"},
    )
    listing = await create_farmer_listing(client, farmer_headers, quantity=3)
    response = await client.post(
        f"/api/v1/marketplace/listings/{listing['id']}/images",
        files={"file": ("crop.png", b"image bytes", "image/png")},
        headers=farmer_headers,
    )
    assert response.status_code == 503


@pytest.mark.anyio
async def test_item_level_fulfillment_multi_farmer_ownership_and_stock_restore(client, db_session):
    _, farmer_one_headers = await register_and_login(
        client,
        "fulfillment_one@example.com",
        "farmer",
        {"farm_name": "Fulfillment One", "latitude": 12.9, "longitude": 77.5, "address": "One Road"},
    )
    _, farmer_two_headers = await register_and_login(
        client,
        "fulfillment_two@example.com",
        "farmer",
        {"farm_name": "Fulfillment Two", "latitude": 12.8, "longitude": 77.4, "address": "Two Road"},
    )
    _, customer_headers = await register_and_login(client, "fulfillment_customer@example.com", "customer")
    admin = User(email="fulfillment_admin@example.com", password_hash=get_password_hash("password123"), full_name="Fulfillment Admin", role="admin")
    db_session.add(admin)
    await db_session.commit()
    admin_login = await client.post("/api/v1/auth/token", data={"username": "fulfillment_admin@example.com", "password": "password123"})
    admin_headers = {"Authorization": f"Bearer {admin_login.json()['access_token']}"}

    listing_one = await create_farmer_listing(client, farmer_one_headers, quantity=5)
    listing_two = await create_farmer_listing(client, farmer_two_headers, quantity=5)
    await client.post("/api/v1/cart/items", json={"crop_listing_id": listing_one["id"], "quantity": 2}, headers=customer_headers)
    await client.post("/api/v1/cart/items", json={"crop_listing_id": listing_two["id"], "quantity": 1}, headers=customer_headers)
    checkout = await client.post("/api/v1/cart/checkout", headers=customer_headers)
    assert checkout.status_code == 200
    items = checkout.json()["order"]["items"]
    item_one = next(item for item in items if item["crop_listing_id"] == listing_one["id"])
    item_two = next(item for item in items if item["crop_listing_id"] == listing_two["id"])
    assert item_one["status"] == "pending"

    blocked = await client.patch(f"/api/v1/marketplace/order-items/{item_two['id']}/status", json={"status": "accepted"}, headers=farmer_one_headers)
    assert blocked.status_code == 403

    accepted = await client.patch(f"/api/v1/marketplace/order-items/{item_one['id']}/status", json={"status": "accepted"}, headers=farmer_one_headers)
    assert accepted.status_code == 200
    assert accepted.json()["items"][0]["status"] == "accepted"

    rejected = await client.patch(f"/api/v1/marketplace/order-items/{item_two['id']}/status", json={"status": "rejected"}, headers=admin_headers)
    assert rejected.status_code == 200
    result = await db_session.execute(select(CropListing).where(CropListing.id == uuid.UUID(listing_two["id"])))
    assert result.scalars().first().available_quantity == 5
    repeated = await client.patch(f"/api/v1/marketplace/order-items/{item_two['id']}/status", json={"status": "rejected"}, headers=admin_headers)
    assert repeated.status_code == 200
    result = await db_session.execute(select(CropListing).where(CropListing.id == uuid.UUID(listing_two["id"])))
    assert result.scalars().first().available_quantity == 5

    customer_view = await client.get("/api/v1/marketplace/orders", headers=customer_headers)
    assert customer_view.status_code == 200
    customer_items = customer_view.json()[0]["items"]
    assert {item["status"] for item in customer_items} >= {"accepted", "rejected"}
