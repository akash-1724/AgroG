import pytest
import uuid
import math
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import event

from app.main import app
from app.core.database import get_db
from app.models.base import Base
from app.models.user import User

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
