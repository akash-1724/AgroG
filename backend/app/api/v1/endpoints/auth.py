import uuid
import httpx
from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.deps import get_current_user, RoleChecker
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token, decode_token
from app.models.user import User, FarmerProfile
from app.models.auth import RefreshToken
from app.schemas.user import UserCreate, UserResponse, TokenResponse, UserLogin, GoogleLogin, TokenRefreshRequest

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

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    payload: TokenRefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """Renew user access tokens using a valid refresh token."""
    try:
        decoded = decode_token(payload.refresh_token, is_refresh=True)
        user_id = decoded.get("sub")
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

    # Check database status and revocation flags
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == payload.refresh_token,
            RefreshToken.is_revoked == False
        )
    )
    db_token = result.scalars().first()
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid or has been revoked."
        )

    if db_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired."
        )

    user_result = await db.execute(select(User).where(User.id == db_token.user_id))
    user = user_result.scalars().first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found."
        )

    new_access_token = create_access_token(subject=user.id, role=user.role)
    
    return {
        "access_token": new_access_token,
        "refresh_token": payload.refresh_token,
        "token_type": "bearer"
    }

@router.post("/logout")
async def logout(
    payload: TokenRefreshRequest,
    response: Response,
    db: AsyncSession = Depends(get_db)
):
    """Revoke user refresh tokens and clear auth cookies."""
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == payload.refresh_token)
    )
    db_token = result.scalars().first()
    if db_token:
        db_token.is_revoked = True
        await db.commit()

    response.delete_cookie(key="refresh_token")
    return {"detail": "Successfully logged out."}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve details of the currently authenticated user."""
    return current_user

@router.get("/farmer-only-test")
async def farmer_only_test(current_user: User = Depends(RoleChecker(allowed_roles=["farmer", "admin"]))):
    """Endpoint restricted to users possessing the farmer or admin role."""
    return {
        "status": "authorized",
        "message": f"Hello Farmer {current_user.full_name}, you have accessed a role-protected resource."
    }

@router.get("/admin-only-test")
async def admin_only_test(current_user: User = Depends(RoleChecker(allowed_roles=["admin"]))):
    """Endpoint restricted to users possessing the admin role."""
    return {
        "status": "authorized",
        "message": f"Hello Admin {current_user.full_name}, you have accessed a role-protected resource."
    }

