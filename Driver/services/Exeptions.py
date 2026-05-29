class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


# ── Auth ───────────────────────────────────────────────────────


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


# ── Domain ─────────────────────────────────────────────────────


class ApplicationNotFoundError(AppException):
    def __init__(self, message: str = "Заявка не найдена") -> None:
        super().__init__(message, status_code=404)


class ApplicationAlreadyExistsError(AppException):
    def __init__(self, message: str = "У пользователя уже есть заявка на рассмотрении") -> None:
        super().__init__(message, status_code=409)


class ApplicationWrongStatusError(AppException):
    def __init__(self, message: str = "Действие недоступно для этого статуса заявки") -> None:
        super().__init__(message, status_code=409)


class DriverNotFoundError(AppException):
    def __init__(self, message: str = "Водитель не найден") -> None:
        super().__init__(message, status_code=404)


class DriverAlreadyExistsError(AppException):
    def __init__(self, message: str = "Пользователь уже является водителем") -> None:
        super().__init__(message, status_code=409)


class VehicleNotFoundError(AppException):
    def __init__(self, message: str = "Машина не найдена") -> None:
        super().__init__(message, status_code=404)


class VehicleAccessDeniedError(AppException):
    def __init__(self, message: str = "Эта машина принадлежит другому водителю") -> None:
        super().__init__(message, status_code=403)


# ── Uploads ────────────────────────────────────────────────────


class InvalidUploadError(AppException):
    def __init__(self, message: str = "Некорректный файл") -> None:
        super().__init__(message, status_code=400)


class FileNotFoundInStorageError(AppException):
    def __init__(self, message: str = "Файл не найден") -> None:
        super().__init__(message, status_code=404)


# ── External services ──────────────────────────────────────────


class UserServiceError(AppException):
    def __init__(
        self, message: str = "Ошибка обращения к User-сервису", status_code: int = 502
    ) -> None:
        super().__init__(message, status_code=status_code)
