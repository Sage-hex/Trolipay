from typing import Any


class AppError(Exception):
    def __init__(self, message: str, code: str = "APP_ERROR", details: Any | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details


class ValidationError(AppError):
    def __init__(self, message: str = "Validation failed", details: Any | None = None) -> None:
        super().__init__(message=message, code="VALIDATION_ERROR", details=details)


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found", details: Any | None = None) -> None:
        super().__init__(message=message, code="NOT_FOUND", details=details)


class AuthError(AppError):
    def __init__(self, message: str = "Authentication failed", details: Any | None = None) -> None:
        super().__init__(message=message, code="AUTH_ERROR", details=details)


class ConflictError(AppError):
    def __init__(self, message: str = "Conflict", details: Any | None = None) -> None:
        super().__init__(message=message, code="CONFLICT", details=details)


class ProviderError(AppError):
    def __init__(self, message: str = "Provider error", details: Any | None = None) -> None:
        super().__init__(message=message, code="PROVIDER_ERROR", details=details)
