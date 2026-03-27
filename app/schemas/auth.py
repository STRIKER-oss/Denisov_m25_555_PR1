from pydantic import BaseModel, EmailStr, Field, field_validator

class RegisterRequest(BaseModel):
    """Запрос на регистрацию пользователя"""
    
    email: EmailStr = Field(..., description="Email пользователя", example="user@example.com")
    password: str = Field(..., min_length=8, max_length=128, description="Пароль", example="SecurePass123!")
  
    @field_validator("password")
    @classmethod
    
    def validate_password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Пароль должен быть не короче 8 символов")
        if not any(c.isupper() for c in v):
            raise ValueError("Пароль должен содержать заглавную букву")
        if not any(c.islower() for c in v):
            raise ValueError("Пароль должен содержать строчную букву")
        if not any(c.isdigit() for c in v):
            raise ValueError("Пароль должен содержать цифру")
        return v


class TokenResponse(BaseModel):   
    access_token: str = Field(..., description="JWT токен доступа")
    token_type: str = Field(default="bearer", description="Тип токена")
