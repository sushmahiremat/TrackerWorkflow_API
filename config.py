from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database Configuration
    database_url: str = "postgresql://postgres:123@localhost:5432/TrackerWorkflow"
    
    # Alternative individual database settings
    db_host: str = "localhost"
    db_port: str = "5432"
    db_name: str = "TrackerWorkflow"
    db_user: str = "postgres"
    db_password: str = "123"
    
    # JWT Configuration
    secret_key: str = "uygduweydwudywugcgmjkiuytcxzszdsiutuytytrthfd"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google OAuth settings
    google_client_id: str = ""
    google_client_secret: str = ""
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env file

settings = Settings() 