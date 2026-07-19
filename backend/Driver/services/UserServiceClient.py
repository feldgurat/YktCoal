import logging
import uuid
from typing import Annotated

import httpx
from fastapi import Depends

from config import settings
from services.Exeptions import UserServiceError

logger = logging.getLogger(__name__)


class UserServiceClient:
    """
    HTTP-клиент к User-сервису. Используется для межсервисных вызовов,
    защищённых INTERNAL_SERVICE_KEY (НЕ telegram-ключом).
    """

    def __init__(self) -> None:
        self._base_url = settings.USER_SERVICE_URL.rstrip("/")
        self._timeout = httpx.Timeout(10.0)
        self._headers = {"X-Service-Key": settings.INTERNAL_SERVICE_KEY}

    async def add_driver_role(self, user_id: uuid.UUID) -> None:
        """Добавить пользователю роль 'driver' в User-сервисе."""
        url = f"{self._base_url}/api/v1/internal/users/{user_id}/roles/driver"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.post(url, headers=self._headers)
        except httpx.HTTPError as e:
            logger.exception("Failed to reach User-service at %s", url)
            raise UserServiceError(f"User-service недоступен: {e}") from None

        if resp.status_code >= 400:
            logger.warning("User-service returned %s for %s: %s", resp.status_code, url, resp.text)
            raise UserServiceError(
                f"User-service вернул {resp.status_code}",
                status_code=502,
            )

    async def remove_driver_role(self, user_id: uuid.UUID) -> None:
        url = f"{self._base_url}/api/v1/internal/users/{user_id}/roles/driver"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.delete(url, headers=self._headers)
        except httpx.HTTPError as e:
            logger.exception("Failed to reach User-service at %s", url)
            raise UserServiceError(f"User-service недоступен: {e}") from None

        if resp.status_code >= 400:
            logger.warning("User-service returned %s for %s: %s", resp.status_code, url, resp.text)
            raise UserServiceError(
                f"User-service вернул {resp.status_code}",
                status_code=502,
            )


def get_user_service_client() -> UserServiceClient:
    return UserServiceClient()


UserServiceClientDep = Annotated[UserServiceClient, Depends(get_user_service_client)]
