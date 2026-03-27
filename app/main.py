from contextlib import asynccontextmanager
from typing import AsyncGenerator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes_auth import router as auth_router
from app.api.routes_chat import router as chat_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Создание таблиц"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

def create_app() -> FastAPI:
    """настройка FastAPI"""
    app = FastAPI(
        title=settings.APP_NAME,
        version="0.1.0",
        description="API для работы с LLM",
        docs_url="/docs" if settings.ENV != "production" else None,
        redoc_url="/redoc" if settings.ENV != "production" else None,
        lifespan=lifespan,
    )
    
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
    app.include_router(chat_router, prefix="/api/chat", tags=["chat"])
    
    @app.get("/health", tags=["health"])
    async def health_check() -> dict:
        return {
            "status": "healthy",
            "app_name": settings.APP_NAME,
            "environment": settings.ENV,
            "openrouter_configured": bool(settings.OPENROUTER_API_KEY),
            "database": settings.SQLITE_PATH,
        }
    
    return app


app = create_app()
