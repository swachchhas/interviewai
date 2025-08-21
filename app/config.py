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

    # Available AI models (default + fallbacks)
    MODELS = [
        "tngtech/deepseek-r1t2-chimera:free",
        "openai/gpt-oss-20b:free",
        "deepseek/deepseek-r1:free"
        "deepseek/deepseek-chat-v3-0324:free"
    ]

    @classmethod
    def get_current_api_key(cls):
        if cls.API_KEYS:
            return cls.API_KEYS[cls.CURRENT_KEY_INDEX % len(cls.API_KEYS)]
        return None

    @classmethod
    def switch_api_key(cls):
        if cls.API_KEYS:
            cls.CURRENT_KEY_INDEX = (cls.CURRENT_KEY_INDEX + 1) % len(cls.API_KEYS)
            return cls.get_current_api_key()
        return None

    @classmethod
    def get_model(cls, index=0):
        """Return the model at the given index, looping around."""
        return cls.MODELS[index % len(cls.MODELS)]
