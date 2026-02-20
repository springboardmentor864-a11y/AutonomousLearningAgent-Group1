import os
from functools import lru_cache
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load .env
load_dotenv()


class Settings(BaseSettings):
    # Yahoo Finance does NOT require API key
    YAHOO_FINANCE_BASE_URL: str = "https://query1.finance.yahoo.com"

    # JWT / Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"


@lru_cache
def get_settings():
    return Settings()
