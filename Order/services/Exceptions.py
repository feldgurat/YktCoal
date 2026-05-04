class AppException(Exception):
    def __init__(self, message: str, status_code: int = 400) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class OrderNotFoundError(AppException):
    def __init__(self, message: str = "Заказ не найден") -> None:
        super().__init__(message, status_code=404)


class ResourceNotFoundError(AppException):
    def __init__(self, message: str = "Ресурс не найден") -> None:
        super().__init__(message, status_code=404)


class OfferNotFoundError(AppException):
    def __init__(self, message: str = "Предложение не найдено") -> None:
        super().__init__(message, status_code=404)


class InvalidStatusTransitionError(AppException):
    def __init__(self, message: str = "Недопустимый переход статуса") -> None:
        super().__init__(message, status_code=422)


class AccessDeniedError(AppException):
    def __init__(self, message: str = "Нет доступа") -> None:
        super().__init__(message, status_code=403)


class InvalidTokenError(AppException):
    def __init__(self, message: str = "Невалидный токен") -> None:
        super().__init__(message, status_code=401)


class TokenExpiredError(AppException):
    def __init__(self, message: str = "Токен просрочен") -> None:
        super().__init__(message, status_code=401)


class DuplicateOfferError(AppException):
    def __init__(self, message: str = "Вы уже отправили предложение на этот заказ") -> None:
        super().__init__(message, status_code=409)


class OrderNotAcceptingOffersError(AppException):
    def __init__(self, message: str = "Заказ не принимает предложения") -> None:
        super().__init__(message, status_code=422)


class OfferAlreadyHandledError(AppException):
    def __init__(self, message: str = "Предложение уже обработано") -> None:
        super().__init__(message, status_code=422)
