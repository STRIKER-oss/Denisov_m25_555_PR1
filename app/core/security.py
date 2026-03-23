
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings
from app.core.errors import InvalidTokenError, TokenExpiredError


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int, role: str = "user") -> str:

    expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    expire_delta = timedelta(minutes=expire_minutes)
    

    now = datetime.now(timezone.utc)
    

    payload: Dict[str, Any] = {
        "sub": str(user_id),  # Subject (user identifier)
        "role": role,          # User role
        "iat": now,            # Issued at
        "exp": now + expire_delta,  # Expiration time
    }
    

    token = jwt.encode(
        claims=payload,
        key=settings.JWT_SECRET,
        algorithm=settings.JWT_ALG,
    )
    
    return token


def decode_access_token(token: str) -> Dict[str, Any]:

    try:
        payload = jwt.decode(
            token=token,
            key=settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
            options={"verify_exp": True},  
        )
        

        if "sub" not in payload:
            raise InvalidTokenError("Token missing subject claim")
        
        if "role" not in payload:
            raise InvalidTokenError("Token missing role claim")
        

        if "exp" in payload:
            exp_timestamp = payload["exp"]
            if isinstance(exp_timestamp, (int, float)):
                exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=timezone.utc)
                if exp_datetime < datetime.now(timezone.utc):
                    raise TokenExpiredError("Token has expired")
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token has expired")
    except jwt.JWTClaimsError as e:
        raise InvalidTokenError(f"Invalid token claims: {str(e)}")
    except jwt.JWTError as e:
        raise InvalidTokenError(f"Invalid token: {str(e)}")
    except Exception as e:
        raise InvalidTokenError(f"Token validation failed: {str(e)}")


def get_token_payload(token: str) -> Dict[str, Any]:

    try:
        # Decode without verification (for debugging)
        payload = jwt.get_unverified_claims(token)
        return payload
    except jwt.JWTError:
        return {}


def extract_user_id_from_token(token: str) -> int:

    payload = decode_access_token(token)
    
    sub = payload.get("sub")
    if not sub:
        raise InvalidTokenError("Token missing subject claim")
    
    try:
        user_id = int(sub)
        return user_id
    except (ValueError, TypeError):
        raise InvalidTokenError(f"Invalid user ID format in token: {sub}")


def extract_role_from_token(token: str) -> str:

    payload = decode_access_token(token)
    
    role = payload.get("role")
    if not role:
        raise InvalidTokenError("Token missing role claim")
    
    return role
