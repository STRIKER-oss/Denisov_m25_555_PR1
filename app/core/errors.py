from typing import Any, Dict, Optional


class AppError(Exception):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ConflictError(AppError):
    pass


class UnauthorizedError(AppError):
    pass


class ForbiddenError(AppError):
    pass


class NotFoundError(AppError):
    pass


class ValidationError(AppError):
    pass


class ExternalServiceError(AppError):
    pass


class TokenExpiredError(UnauthorizedError):
    pass


class InvalidTokenError(UnauthorizedError):
    pass
