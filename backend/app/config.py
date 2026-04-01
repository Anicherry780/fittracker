import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "FitTracker API"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # Database
    DATABASE_URL: str = ""

    # JWT
    JWT_SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440

    # Cloudflare R2
    R2_ACCOUNT_ID: str = ""
    R2_ACCESS_KEY_ID: str = ""
    R2_SECRET_ACCESS_KEY: str = ""
    R2_BUCKET_NAME: str = "fittracker"
    R2_PUBLIC_URL: str = ""

    # AWS Bedrock
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION: str = "us-east-1"
    BEDROCK_MODEL_ID: str = "us.anthropic.claude-3-haiku-20240307-v1:0"

    # Email (Resend)
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = "FitTracker <onboarding@resend.dev>"

    # Frontend
    FRONTEND_URL: str = "https://fit.anirudhdev.com"

    class Config:
        env_file = ".env"


# Create settings once at module load — env vars are available at this point
_settings = Settings()


def get_settings() -> Settings:
    return _settings
