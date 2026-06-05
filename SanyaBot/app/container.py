"""Композиционный корень (Composition Root).

Здесь — и только здесь — собираются конкретные реализации: HTTP-клиенты,
шлюзы, сервисы. Остальной код зависит от абстракций. Это единственное место,
которое «знает» обо всех слоях, что и требует чистая архитектура.
"""
from __future__ import annotations

from dataclasses import dataclass

from app.config import Settings
from app.infrastructure.api.client import ApiClient
from app.infrastructure.api.order_gateway import (
    OfferApiGateway,
    OrderApiGateway,
    ResourceApiGateway,
)
from app.infrastructure.api.user_gateway import UserApiGateway
from app.services.auth_service import AuthService
from app.services.customer_service import CustomerService
from app.services.driver_service import DriverService


@dataclass(slots=True)
class Container:
    """Хранит собранные сервисы и владеет жизненным циклом HTTP-клиентов."""

    auth_service: AuthService
    customer_service: CustomerService
    driver_service: DriverService

    _clients: tuple[ApiClient, ...]

    @classmethod
    def build(cls, settings: Settings) -> "Container":
        user_client = ApiClient(
            base_url=settings.USER_SERVICE_URL,
            service_key=settings.INTERNAL_TELEGRAM_SERVICE_KEY,
            timeout=settings.HTTP_TIMEOUT_SECONDS,
        )
        order_client = ApiClient(
            base_url=settings.ORDER_SERVICE_URL,
            service_key=settings.INTERNAL_TELEGRAM_SERVICE_KEY,
            timeout=settings.HTTP_TIMEOUT_SECONDS,
        )

        users = UserApiGateway(user_client)
        resources = ResourceApiGateway(order_client)
        orders = OrderApiGateway(order_client)
        offers = OfferApiGateway(order_client)

        return cls(
            auth_service=AuthService(users),
            customer_service=CustomerService(resources, orders, offers),
            driver_service=DriverService(orders, offers),
            _clients=(user_client, order_client),
        )

    async def aclose(self) -> None:
        for client in self._clients:
            await client.aclose()

    def as_workflow_data(self) -> dict[str, object]:
        """Сервисы, которые aiogram внедрит в хендлеры по имени аргумента."""
        return {
            "auth_service": self.auth_service,
            "customer_service": self.customer_service,
            "driver_service": self.driver_service,
        }
