"""Реализации ResourceGateway, OrderGateway, OfferGateway поверх Order-сервиса.

Три отдельных класса (по одному на контекст) разделяют ответственность и
дают узкие интерфейсы потребителям (SRP + ISP). Все используют общий
ApiClient — то есть один HTTP-пул соединений.
"""

from __future__ import annotations

from collections.abc import Sequence

from app.domain.commands import NewOffer, NewOrder
from app.domain.models import Offer, Order, Resource
from app.infrastructure.api import mappers
from app.infrastructure.api.client import ApiClient

_PREFIX = "/api/v1/telegram"


class ResourceApiGateway:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    async def list_active(self) -> Sequence[Resource]:
        data = await self._client.request("GET", f"{_PREFIX}/resources")
        return [mappers.to_resource(x) for x in data]


class OrderApiGateway:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    async def create(self, user_id: str, command: NewOrder) -> Order:
        data = await self._client.request(
            "POST",
            f"{_PREFIX}/orders",
            json=mappers.order_create_payload(user_id, command),
        )
        return mappers.to_order(data)

    async def get(self, user_id: str, roles: Sequence[str], order_id: str) -> Order:
        data = await self._client.request(
            "GET",
            f"{_PREFIX}/orders/{order_id}",
            params={"user_id": user_id, "roles": list(roles)},
        )
        return mappers.to_order(data)

    async def list_by_user(self, user_id: str) -> Sequence[Order]:
        data = await self._client.request("GET", f"{_PREFIX}/orders/by-user/{user_id}")
        return [mappers.to_order(x) for x in data]

    async def list_by_driver(self, user_id: str) -> Sequence[Order]:
        data = await self._client.request("GET", f"{_PREFIX}/orders/by-driver/{user_id}")
        return [mappers.to_order(x) for x in data]

    async def list_available(self) -> Sequence[Order]:
        data = await self._client.request("GET", f"{_PREFIX}/orders/available")
        return [mappers.to_order(x) for x in data]

    async def accept_offer(self, user_id: str, order_id: str, offer_id: str) -> Order:
        data = await self._client.request(
            "POST",
            f"{_PREFIX}/orders/{order_id}/accept-offer",
            json={"user_id": user_id, "order_id": order_id, "offer_id": offer_id},
        )
        return mappers.to_order(data)

    async def _action(self, action: str, user_id: str, order_id: str) -> Order:
        data = await self._client.request(
            "POST",
            f"{_PREFIX}/orders/{order_id}/{action}",
            json={"user_id": user_id},
        )
        return mappers.to_order(data)

    async def start(self, user_id: str, order_id: str) -> Order:
        return await self._action("start", user_id, order_id)

    async def complete(self, user_id: str, order_id: str) -> Order:
        return await self._action("complete", user_id, order_id)

    async def cancel(self, user_id: str, order_id: str) -> Order:
        return await self._action("cancel", user_id, order_id)

    async def driver_withdraw(self, user_id: str, order_id: str) -> Order:
        return await self._action("driver-withdraw", user_id, order_id)


class OfferApiGateway:
    def __init__(self, client: ApiClient) -> None:
        self._client = client

    async def list_for_order(self, user_id: str, order_id: str) -> Sequence[Offer]:
        data = await self._client.request(
            "GET", f"{_PREFIX}/orders/{order_id}/offers", params={"user_id": user_id}
        )
        return [mappers.to_offer(x) for x in data]

    async def list_for_driver(self, user_id: str) -> Sequence[Offer]:
        data = await self._client.request("GET", f"{_PREFIX}/offers/by-driver/{user_id}")
        return [mappers.to_offer(x) for x in data]

    async def create(self, user_id: str, command: NewOffer) -> Offer:
        data = await self._client.request(
            "POST",
            f"{_PREFIX}/offers",
            json=mappers.offer_create_payload(user_id, command),
        )
        return mappers.to_offer(data)

    async def withdraw(self, user_id: str, offer_id: str) -> Offer:
        data = await self._client.request(
            "POST", f"{_PREFIX}/offers/{offer_id}/withdraw", json={"user_id": user_id}
        )
        return mappers.to_offer(data)

    async def reject(self, user_id: str, order_id: str, offer_id: str) -> Offer:
        data = await self._client.request(
            "POST",
            f"{_PREFIX}/orders/{order_id}/offers/{offer_id}/reject",
            json={"user_id": user_id},
        )
        return mappers.to_offer(data)
