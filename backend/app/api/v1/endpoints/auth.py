import uuid
import httpx
from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.models.user import User, FarmerProfile
from app.models.auth import RefreshToken
from app.schemas.user import UserCreate, UserResponse, TokenResponse, UserLogin, GoogleLogin

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user (Customer or Farmer) in the database."""
    # Enforce role boundaries
    if user_in.role.lower() == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Public registration of Admin accounts is prohibited."
        )

    # Check if user already exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user with this email already exists in the system.",
        )
    
    # Create the user object
    hashed_password = get_password_hash(user_in.password)
    new_user = User(
        email=user_in.email,
        password_hash=hashed_password,
        full_name=user_in.full_name,
        phone_number=user_in.phone_number,
        role=user_in.role.lower()
    )
    
    db.add(new_user)
    await db.flush() # Populate the ID
    
    # If the user is registering as a farmer, initialize their farmer profile
    if new_user.role == "farmer":
        farm_name = "New Farm"
        lat = 0.0
        lon = 0.0
        addr = "TBD"
        desc = ""
        
        if user_in.farmer_details:
            farm_name = user_in.farmer_details.farm_name
            lat = user_in.farmer_details.latitude
            lon = user_in.farmer_details.longitude
            addr = user_in.farmer_details.address
            desc = user_in.farmer_details.description or ""
            
        new_profile = FarmerProfile(
            user_id=new_user.id,
            farm_name=farm_name,
            latitude=lat,
            longitude=lon,
            address=addr,
            description=desc
        )
        db.add(new_profile)
    
    await db.commit()
    await db.refresh(new_user)
    return new_user

@router.post("/token", response_model=TokenResponse)
async def login(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """OAuth2 compatible token login, retrieve access and refresh token."""
    # Query user by email
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalars().first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(subject=user.id, role=user.role)
    refresh_token = create_refresh_token(subject=user.id)
    
    # Save refresh token in database
    db_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(db_token)
    await db.commit()
    
    # Securely set refresh token as HttpOnly cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60 # 7 days
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/token-json", response_model=TokenResponse)
async def login_json(
    response: Response,
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """JSON-body login alternative for clients that do not use URL-encoded form posts."""
    result = await db.execute(select(User).where(User.email == credentials.email))
    user = result.scalars().first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect email or password"
        )
    
    access_token = create_access_token(subject=user.id, role=user.role)
    refresh_token = create_refresh_token(subject=user.id)
    
    # Save refresh token in database
    db_token = RefreshToken(
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=7)
    )
    db.add(db_token)
    await db.commit()
    
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/google", response_model=TokenResponse)
async def google_login(
    response: Response,
    payload: GoogleLogin,
    db: AsyncSession = Depends(get_db)
):
    """Google OAuth token login. Verifies ID token with Google APIs, auto-registers new users."""
    async with httpx.AsyncClient() as client:
        try:
            google_res = await client.get(
                f"https://oauth2.googleapis.com/tokeninfo?id_token={payload.id_token}",
                timeout=5.0
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to contact Google OAuth verification server"
            )
            
    if google_res.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid Google OAuth ID token"
        )
        
    google_data = google_res.json()
    email = google_data.get("email")
    full_name = google_data.get("name", "Google User")
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email address not verified or provided by Google"
        )
        
    # Check if user already exists
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalars().first()
    
    if not user:
        # Auto-register as customer
        # Set a secure random password since this is an OAuth user
        random_pwd = uuid.uuid4().hex
        user = User(
            email=email,
            password_hash=get_password_hash(random_pwd),
            full_name=full_name,
            role="customer"
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        
    access_token = create_access_token(subject=user.id, role=user.role)
    refresh_token = create_refresh_token(subject=user.id)
    
    # HttpOnly Cookie for refresh token
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="strict",
        max_age=7 * 24 * 60 * 60
    )
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

