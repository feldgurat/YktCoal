"""Middleware аутентификации.

Перед каждым апдейтом определяет доменного пользователя по Telegram-id и
кладёт его в data["current_user"] (или None). Так хендлеры не дублируют
запрос к бэкенду, а просто принимают current_user как аргумент.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

from app.services.auth_service import AuthService


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        auth_service: AuthService | None = data.get("auth_service")
        from_user = getattr(event, "from_user", None)

        data["current_user"] = None
        if auth_service is not None and from_user is not None:
            data["current_user"] = await auth_service.identify(str(from_user.id))

        return await handler(event, data)
