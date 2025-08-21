from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database Configuration - Updated to match working credentials
    database_url: str = "postgresql://postgres:123@localhost:5432/TrackerWorkflow"
    
    # Alternative individual database settings
    db_host: str = "localhost"
    db_port: str = "5432"
    db_name: str = "TrackerWorkflow"
    db_user: str = "postgres"
    db_password: str = "123"
    
    # JWT Configuration
    secret_key: str = "your-secret-key-here-make-it-long-and-random"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google OAuth settings - Popup mode (no redirect URI needed)
    google_client_id: str = "129237008005-gi3c2jogmsb5kuuiag664305f7vgh30c.apps.googleusercontent.com"
    google_client_secret: str = "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"
    # No redirect_uri needed for popup mode
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env file

settings = Settings() 