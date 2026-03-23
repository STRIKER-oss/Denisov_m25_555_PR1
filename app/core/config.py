
from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra environment variables
    )

    APP_NAME: str = Field(
        default="llm-p",
        description="Application name"
    )
    
    ENV: str = Field(
        default="local",
        description="Environment: local, development, production"
    )

    JWT_SECRET: str = Field(
        ...,
        min_length=32,
        description="Secret key for JWT token signing (required, min 32 chars)"
    )
    
    JWT_ALG: str = Field(
        default="HS256",
        description="JWT signing algorithm"
    )
    
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=60,
        ge=1,
        le=1440,
        description="Access token expiration in minutes (1-1440)"
    )

    SQLITE_PATH: str = Field(
        default="./app.db",
        description="SQLite database file path"
    )

    OPENROUTER_API_KEY: str = Field(
        ...,
        description="OpenRouter API key (required)"
    )
    
    OPENROUTER_BASE_URL: str = Field(
        default="https://openrouter.ai/api/v1",
        description="OpenRouter API base URL"
    )
    
    OPENROUTER_MODEL: str = Field(
        default="stepfun/step-3.5-flash:free",
        description="Default model for LLM interactions"
    )
    
    OPENROUTER_SITE_URL: Optional[str] = Field(
        default=None,
        description="Site URL for OpenRouter requests (used as referer)"
    )
    
    OPENROUTER_APP_NAME: Optional[str] = Field(
        default=None,
        description="Application name for OpenRouter requests (used as title)"
    )

    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Allowed origins for CORS"
    )
    
    @property
    def DATABASE_URL(self) -> str:
        return f"sqlite+aiosqlite:///{self.SQLITE_PATH}"
    
    @property
    def OPENROUTER_HEADERS(self) -> dict:
        headers = {
            "Authorization": f"Bearer {self.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }
        
        if self.OPENROUTER_SITE_URL:
            headers["HTTP-Referer"] = self.OPENROUTER_SITE_URL
        
        if self.OPENROUTER_APP_NAME:
            headers["X-Title"] = self.OPENROUTER_APP_NAME
        
        return headers


settings = Settings()
