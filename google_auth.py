import requests
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from google.auth.exceptions import GoogleAuthError
from schemas import GoogleUserInfo
from config import settings
import logging
import time

logger = logging.getLogger(__name__)

# Simple cache for verified tokens to avoid repeated verification
_token_cache = {}

class GoogleAuthService:
    def __init__(self):
        self.client_id = settings.google_client_id
        self.client_secret = settings.google_client_secret

    async def verify_google_token(self, id_token_str: str) -> GoogleUserInfo:
        """
        Verify Google ID token and extract user information
        """
        try:
            # Check cache first
            if id_token_str in _token_cache:
                logger.info("Token found in cache, skipping verification")
                return _token_cache[id_token_str]
            
            start_time = time.time()
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                google_requests.Request(),
                self.client_id
            )
            verification_time = time.time() - start_time
            logger.info(f"Google token verification completed in {verification_time:.2f}s")
            
            user_info = GoogleUserInfo(
                sub=idinfo['sub'],
                email=idinfo['email'],
                name=idinfo.get('name', ''),
                picture=idinfo.get('picture', ''),
                given_name=idinfo.get('given_name'),
                family_name=idinfo.get('family_name')
            )
            
            # Cache the verified token (cache for 5 minutes)
            _token_cache[id_token_str] = user_info
            # Clean up old tokens periodically
            if len(_token_cache) > 100:  # Keep cache size manageable
                _token_cache.clear()
            
            return user_info
        except GoogleAuthError as e:
            logger.error(f"Google token verification failed: {e}")
            raise ValueError("Invalid Google token")
        except Exception as e:
            logger.error(f"Unexpected error during Google token verification: {e}")
            raise ValueError("Token verification failed")

    def get_google_auth_url(self) -> str:
        """
        Generate Google OAuth URL for frontend (not needed for web applications)
        This is kept for compatibility but web apps don't use redirect URIs
        """
        base_url = "https://accounts.google.com/o/oauth2/v2/auth"
        params = {
            "client_id": self.client_id,
            "redirect_uri": settings.google_redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
            "prompt": "consent"
        }
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{base_url}?{query_string}"

google_auth_service = GoogleAuthService()
