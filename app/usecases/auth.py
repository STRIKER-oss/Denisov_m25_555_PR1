from app.core.errors import ConflictError, UnauthorizedError, NotFoundError
from app.core.security import hash_password, verify_password, create_access_token
from app.repositories.users import UserRepository
from app.schemas.user import UserPublic

class AuthUseCases:
    """аутентификация"""
    
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repo = user_repository
    
    async def register(self, email: str, password: str) -> UserPublic:
        if await self._user_repo.exists_by_email(email):
            raise ConflictError("Email уже зарегистрирован")
        
        password_hash = hash_password(password)
        user = await self._user_repo.create(email=email, password_hash=password_hash, role="user")
        
        return UserPublic(id=user.id, email=user.email, role=user.role)
    
    async def login(self, email: str, password: str) -> str:
        user = await self._user_repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise UnauthorizedError("Неверный email или пароль")
        
        return create_access_token(user.id, user.role)
    
    async def get_profile(self, user_id: int) -> UserPublic:
        user = await self._user_repo.get_by_id(user_id)
        if not user:
            raise NotFoundError("Пользователь не найден")
        
        return UserPublic(id=user.id, email=user.email, role=user.role)
    
    async def is_email_available(self, email: str) -> bool:
        user = await self._user_repo.get_by_email(email)
        return user is None
