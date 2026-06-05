"""Прикладной сервис заказчика (покупателя угля).

Объединяет действия пользователя-заказчика над каталогом, заказами и
полученными предложениями. Зависит от абстракций-шлюзов (DIP).
"""

from __future__ import annotations

from collections.abc import Sequence

from app.domain.commands import NewOrder
from app.domain.interfaces import OfferGateway, OrderGateway, ResourceGateway
from app.domain.models import Offer, Order, Resource


class CustomerService:
    def __init__(
        self,
        resources: ResourceGateway,
        orders: OrderGateway,
        offers: OfferGateway,
    ) -> None:
        self._resources = resources
        self._orders = orders
        self._offers = offers

    async def list_resources(self) -> Sequence[Resource]:
        return await self._resources.list_active()

    async def create_order(self, user_id: str, command: NewOrder) -> Order:
        return await self._orders.create(user_id, command)

    async def my_orders(self, user_id: str) -> Sequence[Order]:
        return await self._orders.list_by_user(user_id)

    async def get_order(self, order_id: str) -> Order:
        return await self._orders.get(order_id)

    async def offers_for_order(self, user_id: str, order_id: str) -> Sequence[Offer]:
        return await self._offers.list_for_order(user_id, order_id)

    async def accept_offer(self, user_id: str, order_id: str, offer_id: str) -> Order:
        return await self._orders.accept_offer(user_id, order_id, offer_id)

    async def complete_order(self, user_id: str, order_id: str) -> Order:
        return await self._orders.complete(user_id, order_id)

    async def cancel_order(self, user_id: str, order_id: str) -> Order:
        return await self._orders.cancel(user_id, order_id)
