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


# ── Resource ──────────────────────────────────────────────────


class ResourceNotFoundError(AppException):
    def __init__(self, message: str = "Тип ресурса не найден") -> None:
        super().__init__(message, status_code=404)


class ResourceAlreadyExistsError(AppException):
    def __init__(self, message: str = "Ресурс с таким названием уже существует") -> None:
        super().__init__(message, status_code=409)


# ── Order ─────────────────────────────────────────────────────


class OrderNotFoundError(AppException):
    def __init__(self, message: str = "Заказ не найден") -> None:
        super().__init__(message, status_code=404)


class OrderAccessDeniedError(AppException):
    def __init__(self, message: str = "Нет прав на это действие с заказом") -> None:
        super().__init__(message, status_code=403)


class OrderWrongStatusError(AppException):
    def __init__(self, message: str = "Действие недоступно для текущего статуса заказа") -> None:
        super().__init__(message, status_code=409)


# ── Offer ─────────────────────────────────────────────────────


class OfferNotFoundError(AppException):
    def __init__(self, message: str = "Предложение не найдено") -> None:
        super().__init__(message, status_code=404)


class OfferAccessDeniedError(AppException):
    def __init__(self, message: str = "Нет прав на это действие с предложением") -> None:
        super().__init__(message, status_code=403)


class OfferWrongStatusError(AppException):
    def __init__(
        self, message: str = "Действие недоступно для текущего статуса предложения"
    ) -> None:
        super().__init__(message, status_code=409)


class OfferAlreadyExistsError(AppException):
    def __init__(self, message: str = "У вас уже есть активное предложение на этот заказ") -> None:
        super().__init__(message, status_code=409)
