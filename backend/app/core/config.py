from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "Elite Bus Prediction"
    JWT_SECRET_KEY: str = "fallback_secret_for_development_only_12345"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ENVIRONMENT: str = "production"
    
    class Config:
        env_file = ".env"

settings = Settings()
