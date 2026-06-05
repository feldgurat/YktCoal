"""Прикладной сервис аутентификации/регистрации через Telegram.

Зависит только от абстракции UserGateway (DIP). Содержит правила: телефон
из Telegram уже подтверждён, поэтому OTP не нужен; если пользователь с таким
телефоном уже есть — привязываем tg_id, иначе создаём нового.
"""

from __future__ import annotations

from app.domain.commands import RegisterUser
from app.domain.interfaces import UserGateway
from app.domain.models import User
from app.domain.phone import normalize_phone


class AuthService:
    def __init__(self, users: UserGateway) -> None:
        self._users = users

    async def identify(self, telegram_user_id: str) -> User | None:
        """Возвращает пользователя по Telegram-id или None, если не знаем его."""
        return await self._users.find_by_telegram_id(telegram_user_id)

    async def complete_onboarding(
        self,
        telegram_user_id: str,
        raw_phone: str,
        name: str,
        address: str | None = None,
    ) -> User:
        """Завершает вход по подтверждённому телефону.

        Если телефон уже в системе (регистрация через веб) — привязывает к нему
        Telegram. Иначе регистрирует нового пользователя.
        """
        phone = normalize_phone(raw_phone)

        existing = await self._users.find_by_phone(phone)
        if existing is not None:
            if existing.telegram_user_id == telegram_user_id:
                return existing
            return await self._users.link_telegram(telegram_user_id, phone)

        return await self._users.register(
            RegisterUser(
                telegram_user_id=telegram_user_id,
                phone=phone,
                name=name,
                address=address,
            )
        )

    async def phone_belongs_to_known_user(self, raw_phone: str) -> bool:
        """Есть ли уже аккаунт с таким телефоном (тогда имя спрашивать не нужно)."""
        phone = normalize_phone(raw_phone)
        return await self._users.find_by_phone(phone) is not None
