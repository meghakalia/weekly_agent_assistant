import os
from typing import List

class Settings:
    # API Configuration
    API_TITLE = "Inventory Management API"
    API_VERSION = "1.0.0"
    
    # CORS Settings
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # Add your production frontend URL here
        # "https://your-frontend-domain.com"
    ]
    
    # File Upload Settings
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/jpg", "image/png", "image/webp"]
    
    # AI/ML Settings (for future integration)
    AI_MODEL_PATH = os.getenv("AI_MODEL_PATH", "")
    AI_API_KEY = os.getenv("AI_API_KEY", "")
    
    # Database Settings (for future use)
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./inventory.db")

settings = Settings()
