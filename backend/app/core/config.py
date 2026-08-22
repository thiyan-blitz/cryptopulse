import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    SECRET_KEY:str=os.getenv("SECRET_KEY")
    REFRESH_SECRET_KEY:str=os.getenv("REFRESH_SECRET_KEY","your-refresh-secre-key-change-in-prod")
    ALGORITHM:str="HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES:int=15
    REFRESH_TOKEN_EXPIRE_DAYS:int=7
    DATABASE_URL:str=os.getenv("DATABASE_URL")

    class Config:
        env_file=".env"

settings=Settings()