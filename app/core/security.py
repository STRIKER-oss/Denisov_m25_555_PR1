from datetime import datetime, timedelta, timezone
from typing import Any, Dict
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
from app.core.errors import InvalidTokenError, TokenExpiredError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, role: str = "user") -> str:
    expire_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    now = datetime.now(timezone.utc)
    
    payload: Dict[str, Any] = {
        "sub": str(user_id),
        "role": role,
        "iat": now,
        "exp": now + expire_delta,
    }
    
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)


def decode_access_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG],
            options={"verify_exp": True}
        )
        
        if "sub" not in payload or "role" not in payload:
            raise InvalidTokenError("Некорректный формат токена")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Срок действия токена истёк")
    except jwt.JWTError as e:
        raise InvalidTokenError(f"Неверный токен: {str(e)}")


def extract_user_id_from_token(token: str) -> int:
    payload = decode_access_token(token)
    try:
        return int(payload.get("sub"))
    except (ValueError, TypeError):
        raise InvalidTokenError("Неверный формат ID пользователя в токене")
