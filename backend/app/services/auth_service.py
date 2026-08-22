from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException,status

from app.models.User import User
from app.schemas.auth import SignupRequest
from app.auth.hashing import hash_password,verify_password
from app.services.create_wallet import create_wallet

async def Signup(db:AsyncSession,signup_data:SignupRequest):
    query=select(User).where((User.email==signup_data.email)|(User.username==signup_data.username))
    existing_user=(await db.execute(query)).scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered"
        )
    try:
        new_user=User(
            email=signup_data.email,
            username=signup_data.username,
            password=hash_password(signup_data.password)
        )
        db.add(new_user)
        await db.flush()

        await create_wallet(db,user_id=new_user.id)
    
        await db.commit()
        await db.refresh(new_user)

        return new_user
    except Exception as e:
        await db.rollback()
        raise e


async def authenticate_user(db:AsyncSession,username_or_email:str,password:str)->User:
    query=select(User).where((User.email==username_or_email)|(User.username==username_or_email))
    user=(await db.execute(query)).scalar_one_or_none()

    if not user or not verify_password(password,user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
