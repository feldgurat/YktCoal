"""Реализация UserGateway поверх Telegram-эндпоинтов User-сервиса."""

from __future__ import annotations

from app.domain.commands import RegisterUser
from app.domain.models import User
from app.infrastructure.api import mappers
from app.infrastructure.api.client import ApiClient

_PREFIX = "/api/v1/telegram"


class UserApiGateway:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    async def find_by_telegram_id(self, telegram_user_id: str) -> User | None:
        data = await self._client.request("GET", f"{_PREFIX}/by-tg-id/{telegram_user_id}")
        return mappers.to_user(data) if data else None

    async def find_by_phone(self, phone: str) -> User | None:
        data = await self._client.request("GET", f"{_PREFIX}/by-phone/{phone}")
        return mappers.to_user(data) if data else None

    async def register(self, command: RegisterUser) -> User:
        data = await self._client.request(
            "POST", f"{_PREFIX}/register", json=mappers.register_payload(command)
        )
        return mappers.to_user(data)

    async def link_telegram(self, telegram_user_id: str, phone: str) -> User:
        data = await self._client.request(
            "POST",
            f"{_PREFIX}/link",
            json={"telegram_user_id": telegram_user_id, "phone": phone},
        )
        return mappers.to_user(data)
