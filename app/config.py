# app/config.py
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Read API keys from .env and split into a list
API_KEYS = os.getenv("API_KEYS", "")
API_KEYS = [k.strip() for k in API_KEYS.split(",") if k.strip()]

# Current key index
CURRENT_KEY_INDEX = int(os.getenv("CURRENT_KEY_INDEX", 0))


class Config:
    # Secret key for Flask sessions
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-change-me")

    # API keys support
    API_KEYS = API_KEYS
    CURRENT_KEY_INDEX = CURRENT_KEY_INDEX

    # Upload settings
    MAX_CONTENT_LENGTH = 4 * 1024 * 1024  # 4 MB
    ALLOWED_EXTENSIONS = {"pdf", "docx"}

    @classmethod
    def get_current_api_key(cls):
        """Return the currently active API key."""
        if cls.API_KEYS:
            return cls.API_KEYS[cls.CURRENT_KEY_INDEX % len(cls.API_KEYS)]
        return None

    @classmethod
    def switch_api_key(cls):
        """Switch to the next API key in the list (round-robin)."""
        if cls.API_KEYS:
            cls.CURRENT_KEY_INDEX = (cls.CURRENT_KEY_INDEX + 1) % len(cls.API_KEYS)
            return cls.get_current_api_key()
        return None
