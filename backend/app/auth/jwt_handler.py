from jose import jwt,JWTError
from typing import Any,Optional
from datetime import datetime,timedelta,timezone
from app.core.config import settings

def create_access_token(user_id:str,expires_delta:Optional[timedelta]=None):
    expire=datetime.now(timezone.utc)+(expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    payload={
        "exp":expire,
        "sub":str(user_id),
        "type":"access"
    }
    return jwt.encode(payload,settings.SECRET_KEY,algorithm=settings.ALGORITHM)

def create_refresh_token(user_id:str|Any,expires_delta:Optional[timedelta]=None)->str:
    expire=datetime.now(timezone.utc)+(expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))
    payload={
        "exp":expire,
        "sub":str(user_id),
        "type":"refresh"
        }
    return jwt.encode(payload,settings.REFRESH_SECRET_KEY,algorithm=settings.ALGORITHM)


