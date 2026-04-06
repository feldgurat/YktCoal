class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class InvalidTokenError(AppException):
    def __init__(self, message: str = "Невалидный токен") -> None:
        super().__init__(message, status_code=401)


class InvalidTokenTypeError(AppException):
    def __init__(self, message: str = "Неверный тип токена") -> None:
        super().__init__(message, status_code=401)


class TokenExpiredError(AppException):
    def __init__(self, message: str = "Токен просрочен") -> None:
        super().__init__(message, status_code=401)


class TokenRevokedError(AppException):
    def __init__(self, message: str = "Токен отозван") -> None:
        super().__init__(message, status_code=401)


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
