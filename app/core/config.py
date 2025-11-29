import sys
from pydantic_settings import BaseSettings
from pydantic import ValidationError

class Settings(BaseSettings):
    SUPABASE_URL: str
    SUPABASE_KEY: str

    class Config:
        env_file = ".env"
        extra = "ignore"

try:
    settings = Settings()
except ValidationError as e:
    print(f"CRITICAL ERROR: Configuration validation failed. Missing required environment variables: {e}")
    sys.exit(1)
