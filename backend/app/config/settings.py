"""Application settings and configuration"""
import os
from typing import List

class Settings:
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./financial_copilot.db")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # External APIs
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "AIzaSyCzL3_QfDj9PKBGGoycG8KqQWiuOEqnAnE")
    
    # CORS
    CORS_ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "*"  # Allow all origins for development
    ]
    
    # App Info
    APP_NAME: str = "AI Financial Co-Pilot"
    APP_DESCRIPTION: str = "Backend API for the AI-powered financial assistant"
    APP_VERSION: str = "1.0.0"

settings = Settings()
