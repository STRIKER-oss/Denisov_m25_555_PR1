from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import User
from app.core.errors import NotFoundError

class UserRepository:
    """Репозиторий для операций с пользователями"""
    
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        result = await self._session.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_by_id_or_raise(self, user_id: int) -> User:
        user = await self.get_by_id(user_id)
        if not user:
            raise NotFoundError(f"Пользователь с id {user_id} не найден")
        return user
    
    async def create(self, email: str, password_hash: str, role: str = "user") -> User:
        user = User(email=email, password_hash=password_hash, role=role)
        self._session.add(user)
        await self._session.flush()
        await self._session.refresh(user)
        return user
    
    async def exists_by_email(self, email: str) -> bool:
        user = await self.get_by_email(email)
        return user is not None
    
    async def delete(self, user_id: int) -> None:
        user = await self.get_by_id_or_raise(user_id)
        await self._session.delete(user)
        await self._session.flush()
