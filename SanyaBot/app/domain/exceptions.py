"""Доменные исключения.

Слои инфраструктуры/сервисов выбрасывают эти типы, а слой представления
(хендлеры) переводит их в понятные пользователю сообщения. Так бизнес-логика
не зависит от способа доставки сообщений.
"""
from __future__ import annotations


class BotError(Exception):
    """Базовое исключение бота."""


class GatewayError(BotError):
    """Ошибка обращения к бэкенду (сеть, 5xx и т.п.)."""


class ApiError(BotError):
    """Бэкенд вернул осмысленную ошибку (4xx) с текстом для пользователя."""

    def __init__(self, message: str, status_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class UserNotRegisteredError(BotError):
    """Текущий Telegram-пользователь ещё не зарегистрирован в системе."""


class AccessDeniedError(BotError):
    """Недостаточно прав для действия (например, не водитель)."""
