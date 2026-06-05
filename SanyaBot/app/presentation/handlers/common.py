"""Централизованная обработка ошибок слоя представления.

Регистрируется на уровне диспетчера, поэтому перехватывает исключения из
всех роутеров и переводит доменные ошибки в понятные пользователю сообщения.
"""

from __future__ import annotations

import logging

from aiogram import Dispatcher
from aiogram.types import ErrorEvent

from app.domain.exceptions import ApiError, BotError, GatewayError

logger = logging.getLogger(__name__)


async def _reply(event: ErrorEvent, text: str) -> None:
    update = event.update
    if update.message:
        await update.message.answer(text)
    elif update.callback_query:
        await update.callback_query.answer(text, show_alert=True)


async def on_error(event: ErrorEvent) -> bool:
    exc = event.exception
    if isinstance(exc, ApiError):
        await _reply(event, f"\u26a0\ufe0f {exc.message}")
        return True
    if isinstance(exc, GatewayError):
        await _reply(event, "\U0001f50c Сервис временно недоступен. Попробуйте позже.")
        return True
    if isinstance(exc, BotError):
        await _reply(event, f"\u26a0\ufe0f {exc}")
        return True

    logger.exception("Необработанная ошибка", exc_info=exc)
    await _reply(event, "Произошла непредвиденная ошибка. Попробуйте позже.")
    return True


def register_error_handler(dispatcher: Dispatcher) -> None:
    dispatcher.errors.register(on_error)
