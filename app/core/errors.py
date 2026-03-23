

from typing import Any, Dict, Optional


class AppError(Exception):

    def __init__(
        self, 
        message: str, 
        details: Optional[Dict[str, Any]] = None
    ) -> None:

        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - Details: {self.details}"
        return self.message


class ConflictError(AppError):

    def __init__(
        self, 
        message: str = "Resource already exists", 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, details)


class UnauthorizedError(AppError):

    def __init__(
        self, 
        message: str = "Invalid credentials", 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, details)


class ForbiddenError(AppError):

    def __init__(
        self, 
        message: str = "Insufficient permissions", 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, details)


class NotFoundError(AppError):
 
    def __init__(
        self, 
        message: str = "Resource not found", 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, details)


class ValidationError(AppError):

    def __init__(
        self, 
        message: str = "Validation failed", 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, details)


class ExternalServiceError(AppError):
 
    def __init__(
        self, 
        message: str = "External service error", 
        details: Optional[Dict[str, Any]] = None,
        status_code: Optional[int] = None
    ) -> None:

        self.status_code = status_code
        if status_code:
            details = details or {}
            details["status_code"] = status_code
        super().__init__(message, details)


class TokenExpiredError(UnauthorizedError):

    def __init__(
        self, 
        message: str = "Token has expired", 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, details)


class InvalidTokenError(UnauthorizedError):

    
    def __init__(
        self, 
        message: str = "Invalid token", 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        super().__init__(message, details)


class DatabaseError(AppError):

    def __init__(
        self, 
        message: str = "Database error", 
        details: Optional[Dict[str, Any]] = None,
        original_error: Optional[Exception] = None
    ) -> None:

        self.original_error = original_error
        if original_error:
            details = details or {}
            details["original_error"] = str(original_error)
        super().__init__(message, details)


class RateLimitError(AppError):

    def __init__(
        self, 
        message: str = "Rate limit exceeded", 
        details: Optional[Dict[str, Any]] = None,
        retry_after: Optional[int] = None
    ) -> None:
        
        self.retry_after = retry_after
        if retry_after:
            details = details or {}
            details["retry_after"] = retry_after
        super().__init__(message, details)


EXCEPTION_STATUS_MAP = {
    ConflictError: 409,
    UnauthorizedError: 401,
    ForbiddenError: 403,
    NotFoundError: 404,
    ValidationError: 422,
    ExternalServiceError: 502,
    TokenExpiredError: 401,
    InvalidTokenError: 401,
    DatabaseError: 500,
    RateLimitError: 429,
}
