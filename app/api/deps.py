from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.errors import InvalidTokenError, TokenExpiredError
from app.core.security import extract_user_id_from_token
from app.db.models import User
from app.db.session import get_db
from app.repositories.chat_messages import ChatMessageRepository
from app.repositories.users import UserRepository
from app.services.openrouter_client import OpenRouterClient, openrouter_client
from app.usecases.auth import AuthUseCases
from app.usecases.chat import ChatUseCases


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/auth/login",
    scheme_name="JWT Authentication",
    description="Введите JWT токен, полученный при входе"
)


async def get_current_user_id(token: str = Depends(oauth2_scheme)) -> int:
    try:
        return extract_user_id_from_token(token)
    except (InvalidTokenError, TokenExpiredError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    user_id: int = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
) -> User:
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


get_db_session = get_db


async def get_user_repository(db: AsyncSession = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


async def get_chat_message_repository(db: AsyncSession = Depends(get_db)) -> ChatMessageRepository:
    return ChatMessageRepository(db)


async def get_openrouter_client() -> OpenRouterClient:
    return openrouter_client


async def get_auth_usecases(
    user_repo: UserRepository = Depends(get_user_repository)
) -> AuthUseCases:
    return AuthUseCases(user_repo)


async def get_chat_usecases(
    chat_repo: ChatMessageRepository = Depends(get_chat_message_repository),
    openrouter_client: OpenRouterClient = Depends(get_openrouter_client)
) -> ChatUseCases:
    return ChatUseCases(chat_repo, openrouter_client)
