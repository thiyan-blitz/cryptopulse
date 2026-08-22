from pydantic import BaseModel,EmailStr,ConfigDict,Field
import uuid
class SignupRequest(BaseModel):
    username:str=Field(min_length=3,max_length=30)
    email:EmailStr
    password:str=Field(min_length=8)

class LoginRequest(BaseModel):
    username_email:str
    password:str

class TokenResponse(BaseModel):
    access_token:str
    refresh_token:str
    token_type:str="bearer"

class UserResponse(BaseModel):
    model_config=ConfigDict(from_attributes=True)

    id:uuid.UUID
    username:str
    email:EmailStr

class RefreshTokenRequest(BaseModel):
    refresh_token:str



