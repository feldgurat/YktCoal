"""Базовый асинхронный HTTP-клиент для Telegram-эндпоинтов бэкенда.

Единственная обязанность (SRP): выполнить запрос, подставить сервисный
заголовок и превратить HTTP-ответ/ошибку в данные или доменное исключение.
Никакой бизнес-логики здесь нет.
"""

from __future__ import annotations

from typing import Any

import httpx

from app.domain.exceptions import ApiError, GatewayError


class ApiClient:
    def __init__(self, base_url: str, service_key: str, timeout: float = 10.0) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url.rstrip("/"),
            headers={"X-Service-Key": service_key},
            timeout=timeout,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: Any | None = None,
    ) -> Any:
        try:
            response = await self._client.request(method, path, params=params, json=json)
        except httpx.HTTPError as exc:  # сеть/таймаут
            raise GatewayError(f"Сервис недоступен: {exc}") from exc

        if response.is_success:
            if response.status_code == 204 or not response.content:
                return None
            return response.json()

        # Бэкенд отдаёт ошибки в формате {"detail": "..."}.
        detail = "Произошла ошибка"
        try:
            payload = response.json()
            if isinstance(payload, dict):
                detail = str(payload.get("detail", detail))
        except ValueError:
            detail = response.text or detail

        if 500 <= response.status_code:
            raise GatewayError(detail)
        raise ApiError(detail, response.status_code)
