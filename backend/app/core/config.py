from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
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
    OPENAI_API_KEY: str = Field(default="")

    # Cloudinary Integration
    CLOUDINARY_URL: str = Field(default="")

    # Sentry DSN
    SENTRY_DSN: str = Field(default="")

settings = Settings()
