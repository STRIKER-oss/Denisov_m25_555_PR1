from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Настройки приложения"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    APP_NAME: str = Field(default="llm-p", description="Название приложения")
    ENV: str = Field(default="local", description="Окружение: local, development, production")
    
    JWT_SECRET: str = Field(..., min_length=32, description="Секретный ключ для JWT")
    JWT_ALG: str = Field(default="HS256", description="Алгоритм JWT")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, ge=1, le=1440, description="Время жизни токена")

    SQLITE_PATH: str = Field(default="./app.db", description="Путь к файлу SQLite")
    
    OPENROUTER_API_KEY: str = Field(..., description="API ключ OpenRouter")
    OPENROUTER_BASE_URL: str = Field(default="https://openrouter.ai/api/v1", description="Базовый URL OpenRouter API")
    OPENROUTER_MODEL: str = Field(default="stepfun/step-3.5-flash:free", description="Модель LLM по умолчанию")
    OPENROUTER_SITE_URL: Optional[str] = Field(default=None, description="URL сайта для OpenRouter")
    OPENROUTER_APP_NAME: Optional[str] = Field(default=None, description="Название приложения для OpenRouter")
    
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="Разрешённые источники"
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
