"""Прикладной сервис водителя.

Действия водителя: смотреть доступные заказы, подавать/отзывать предложения,
выполнять назначенные заказы. Зависит от абстракций-шлюзов (DIP).
"""

from __future__ import annotations

from collections.abc import Sequence

from app.domain.commands import NewOffer
from app.domain.interfaces import OfferGateway, OrderGateway
from app.domain.models import Offer, Order


class DriverService:
    def __init__(self, orders: OrderGateway, offers: OfferGateway) -> None:
        self._orders = orders
        self._offers = offers

    async def available_orders(self) -> Sequence[Order]:
        return await self._orders.list_available()

    async def get_order(self, order_id: str) -> Order:
        return await self._orders.get(order_id)

    async def my_orders(self, user_id: str) -> Sequence[Order]:
        return await self._orders.list_by_driver(user_id)

    async def make_offer(self, user_id: str, command: NewOffer) -> Offer:
        return await self._offers.create(user_id, command)

    async def my_offers(self, user_id: str) -> Sequence[Offer]:
        return await self._offers.list_for_driver(user_id)

    async def withdraw_offer(self, user_id: str, offer_id: str) -> Offer:
        return await self._offers.withdraw(user_id, offer_id)

    async def start_order(self, user_id: str, order_id: str) -> Order:
        return await self._orders.start(user_id, order_id)

    async def withdraw_from_order(self, user_id: str, order_id: str) -> Order:
        return await self._orders.driver_withdraw(user_id, order_id)
