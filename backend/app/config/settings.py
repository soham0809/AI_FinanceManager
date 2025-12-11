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
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 1 month validity for refresh tokens
    
    # External APIs
    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    
    # CORS
    CORS_ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://192.168.0.102:3000",
        "http://192.168.0.102:8080",
        "http://192.168.56.1:3000",
        "http://192.168.56.1:8080",
        "http://192.168.10.1:3000",
        "http://192.168.10.1:8080",
        "*"  # Allow all origins for development
    ]
    
    # App Info
    APP_NAME: str = "AI Financial Co-Pilot"
    APP_DESCRIPTION: str = "Backend API for the AI-powered financial assistant"
    APP_VERSION: str = "1.0.0"

settings = Settings()
