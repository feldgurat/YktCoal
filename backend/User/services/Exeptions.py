from ykt_common.exceptions import (
    AppException,
    InvalidTokenError,
    InvalidTokenTypeError,
    TokenExpiredError,
    TokenRevokedError,
)

__all__ = [
    "AppException",
    "InvalidTokenError",
    "InvalidTokenTypeError",
    "TokenExpiredError",
    "TokenRevokedError",
    "OtpRateLimitError",
    "OtpInvalidError",
    "UserNotFoundError",
    "UserAlreadyExistsError",
    "InvalidRoleError",
]


class OtpRateLimitError(AppException):
    def __init__(self, message: str = "Попробуйте запросить код позже") -> None:
        super().__init__(message, status_code=429)


class OtpInvalidError(AppException):
    def __init__(self, message: str = "Неверный код") -> None:
        super().__init__(message, status_code=400)


class UserNotFoundError(AppException):
    def __init__(self, message: str = "Пользователь не найден") -> None:
        super().__init__(message, status_code=404)


class UserAlreadyExistsError(AppException):
    def __init__(self, message: str = "Пользователь с таким номером уже существует") -> None:
        super().__init__(message, status_code=409)


class InvalidRoleError(AppException):
    def __init__(self, message: str = "Неизвестная роль") -> None:
        super().__init__(message, status_code=400)
