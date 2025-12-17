from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # Database Configuration
    # Priority: DATABASE_URL env var > individual settings > fallback
    database_url: Optional[str] = None
    
    # Alternative individual database settings (used if DATABASE_URL not set)
    db_host: str = "trackerworkflow-db.cxuqcquo86g2.us-west-2.rds.amazonaws.com"
    db_port: str = "5432"
    db_name: str = "TrackerWorkflow"
    db_user: str = "postgres"
    db_password: str = "w1p.z|qj9VV!b|OiPaaRn|4W.P69"
    
    # JWT Configuration
    secret_key: str = "uygduweydwudywugcgmjkiuytcxzszdsiutuytytrthfd"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Google OAuth settings (REQUIRED for Google login to work)
    # Set these in .env file for local dev or App Runner environment variables
    google_client_id: str = "129237008005-gi3c2jogmsb5kuuiag664305f7vgh30c.apps.googleusercontent.com"
    google_client_secret: str = "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"  # Get from Google Cloud Console
    google_redirect_uri: str = "https://y55dfkjshm.us-west-2.awsapprunner.com/auth/google/callback"
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env file

settings = Settings() 