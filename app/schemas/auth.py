

from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):

    
    email: EmailStr = Field(
        ...,
        description="User's email address",
        example="user@example.com"
    )
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="User's password (min 8 characters, max 128)",
        example="SecurePass123!"
    )
    
    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        if not any(char.isupper() for char in v):
            raise ValueError("Password must contain at least one uppercase letter")
        
        if not any(char.islower() for char in v):
            raise ValueError("Password must contain at least one lowercase letter")
        
        if not any(char.isdigit() for char in v):
            raise ValueError("Password must contain at least one digit")
        
        if not any(not char.isalnum() for char in v):
            raise ValueError("Password must contain at least one special character")
        
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }


class TokenResponse(BaseModel):
    
    
    access_token: str = Field(
        ...,
        description="JWT access token for authentication",
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    )
    
    token_type: str = Field(
        default="bearer",
        description="Token type for OAuth2 Bearer authentication",
        example="bearer"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class LoginRequest(BaseModel):

    
    username: EmailStr = Field(
        ...,
        description="User's email address (field named 'username' for OAuth2 compatibility)",
        example="user@example.com"
    )
    
    password: str = Field(
        ...,
        min_length=1,
        description="User's password",
        example="SecurePass123!"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "user@example.com",
                "password": "SecurePass123!"
            }
        }


class UserInfo(BaseModel):

    id: int = Field(..., description="User ID", example=1)
    email: EmailStr = Field(..., description="User's email", example="user@example.com")
    role: str = Field(..., description="User's role", example="user")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "user@example.com",
                "role": "user"
            }
        }


class AuthErrorResponse(BaseModel):

    
    detail: str = Field(
        ...,
        description="Error description",
        example="Invalid credentials"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "detail": "Invalid credentials"
            }
        }
