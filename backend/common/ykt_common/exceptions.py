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
