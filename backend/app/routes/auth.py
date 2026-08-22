from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from jose import jwt, JWTError
from app.database.database import get_db
from app.schemas.auth import SignupRequest, UserResponse, TokenResponse, RefreshTokenRequest,LoginRequest
from app.services.auth_service import Signup, authenticate_user
from app.auth.jwt_handler import create_access_token, create_refresh_token
from app.core.config import settings
from app.models.User import User
from app.auth.dependencies import get_current_user
from app.services.binance_listener import latest_prices

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.get("/debug/prices")
async def debug_prices():
    return dict(list(latest_prices.items())[:5])

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_in: SignupRequest, db: AsyncSession = Depends(get_db)):
    return await Signup(db, user_in)

@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await authenticate_user(db, form_data.username, form_data.password)
    return TokenResponse(
        access_token=create_access_token(user_id=user.id),
        refresh_token=create_refresh_token(user_id=user.id)
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_tokens(body: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(body.refresh_token, settings.REFRESH_SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")
        
        if not user_id or token_type != "refresh":
            raise HTTPException(status_code=401, detail="Invalid refresh token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Expired or invalid refresh token")

    stmt = select(User).where(User.id == user_id)
    user = (await db.execute(stmt)).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return TokenResponse(
        access_token=create_access_token(user_id=user.id),
        refresh_token=create_refresh_token(user_id=user.id)
    )