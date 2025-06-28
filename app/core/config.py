from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Application settings
    APP_NAME: str = "Universal URL Shortener"
    VERSION: str = "1.0.0"
    
    # URL settings
    BASE_URL: str = os.getenv("VERCEL_URL", f"http://{HOST}:{PORT}")
    SHORT_CODE_LENGTH: int = 6
    
    # Storage settings
    STORAGE_FILE: str = "/tmp/urls.json" if os.getenv("VERCEL") else "urls.json"
    
    # Security settings
    ALLOWED_HOSTS: list = ["*"]
    
    # Feature flags
    ENABLE_ANALYTICS: bool = True
    ENABLE_QR_CODES: bool = True
    ENABLE_CUSTOM_DOMAINS: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
