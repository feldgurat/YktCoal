class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class DriverNotFoundError(AppException):
    def __init__(self, message: str = "Профиль водителя не найден") -> None:
        super().__init__(message, status_code=404)


class DriverBlockedError(AppException):
    def __init__(self, message: str = "Водитель заблокирован") -> None:
        super().__init__(message, status_code=403)


class ApplicationNotFoundError(AppException):
    def __init__(self, message: str = "Заявка не найдена") -> None:
        super().__init__(message, status_code=404)


class ApplicationAlreadyExistsError(AppException):
    def __init__(self, message: str = "У вас уже есть активная заявка") -> None:
        super().__init__(message, status_code=409)


class ApplicationAlreadyHandledError(AppException):
    def __init__(self, message: str = "Заявка уже обработана") -> None:
        super().__init__(message, status_code=422)


class AlreadyDriverError(AppException):
    def __init__(self, message: str = "Вы уже являетесь водителем") -> None:
        super().__init__(message, status_code=409)


class UserServiceError(AppException):
    def __init__(self, message: str = "Ошибка связи с User-сервисом") -> None:
        super().__init__(message, status_code=502)


class AccessDeniedError(AppException):
    def __init__(self, message: str = "Нет доступа") -> None:
        super().__init__(message, status_code=403)
