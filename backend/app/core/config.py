from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, model_validator

BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_ROOT = Path(__file__).resolve().parents[3]

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(PROJECT_ROOT / ".env", BACKEND_DIR / ".env", ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    PROJECT_NAME: str = "AgroGuide"
    API_V1_STR: str = "/api/v1"
    
    # Database Settings
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/agroguide"
    )
    
    # Redis Settings
    REDIS_URL: str = Field(default="redis://localhost:6379/0")

    # CORS Settings
    BACKEND_CORS_ORIGINS: list[str] = Field(default=["http://localhost:3000"])

    # Security Settings
    ENVIRONMENT: str = Field(default="development")
    JWT_SECRET: str = Field(default="super-secret-change-me-in-production-12345")
    JWT_REFRESH_SECRET: str = Field(default="another-super-secret-refresh-key-98765")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Google OAuth
    GOOGLE_CLIENT_ID: str = Field(default="")
    GOOGLE_CLIENT_SECRET: str = Field(default="")

    # ML Service Settings
    ML_SERVICE_URL: str = Field(default="http://localhost:8001")
    GEMINI_API_KEY: str = Field(default="")

    # Cloudinary Integration
    CLOUDINARY_URL: str = Field(default="")
    MAX_LISTING_IMAGE_UPLOAD_MB: int = Field(default=5)
    LISTING_IMAGE_ALLOWED_MIME_TYPES: list[str] = Field(default=["image/jpeg", "image/png", "image/webp"])
    LISTING_IMAGE_ALLOWED_EXTENSIONS: list[str] = Field(default=[".jpg", ".jpeg", ".png", ".webp"])

    @model_validator(mode="after")
    def reject_production_default_secrets(self):
        if self.ENVIRONMENT.lower() in {"production", "prod"}:
            default_secrets = {
                "super-secret-change-me-in-production-12345",
                "another-super-secret-refresh-key-98765",
            }
            if self.JWT_SECRET in default_secrets or self.JWT_REFRESH_SECRET in default_secrets:
                raise ValueError("Production JWT secrets must be configured with non-default values.")
        return self

settings = Settings()
