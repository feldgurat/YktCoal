import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends

from data.entities.Offer import Offer
from data.entities.OfferStatus import OfferStatus
from data.entities.OrderStatus import OrderStatus
from data.repositories.OfferRepo import OfferRepository, OfferRepositoryDep
from data.repositories.OrderRepo import OrderRepository, OrderRepositoryDep
from data.schemas.Offer import OfferCreate, OfferRead
from services.Exeptions import (
    OfferAccessDeniedError,
    OfferAlreadyExistsError,
    OfferNotFoundError,
    OfferWrongStatusError,
    OrderNotFoundError,
    OrderWrongStatusError,
)


class OfferService:
    def __init__(
        self, offer_repo: OfferRepository, order_repo: OrderRepository
    ) -> None:
        self._offers = offer_repo
        self._orders = order_repo

    @staticmethod
    def to_read(o: Offer) -> OfferRead:
        return OfferRead(
            id=o.id,
            order_id=o.order_id,
            driver_user_id=o.driver_user_id,
            price=o.price,
            comment=o.comment,
            delivery_date=o.delivery_date,
            status=o.status,
            created_at=o.created_at,
            updated_at=o.updated_at,
        )

    # ── Queries ────────────────────────────────────────────────

    async def list_for_order(
        self, requester_user_id: uuid.UUID, order_id: uuid.UUID
    ) -> Sequence[Offer]:
        """Все Offer на заказ. Видеть может только заказчик."""
        order = await self._orders.get_by_id(order_id)
        if order is None:
            raise OrderNotFoundError()
        if order.user_id != requester_user_id:
            raise OfferAccessDeniedError("Предложения видны только заказчику")
        return await self._offers.get_by_order_id(order_id)

    async def list_for_driver(self, driver_user_id: uuid.UUID) -> Sequence[Offer]:
        return await self._offers.get_by_driver_id(driver_user_id)

    # ── Create / Withdraw ──────────────────────────────────────

    async def create(self, driver_user_id: uuid.UUID, data: OfferCreate) -> Offer:
        order = await self._orders.get_by_id(data.order_id)
        if order is None:
            raise OrderNotFoundError()
        if order.status != OrderStatus.NEW:
            raise OrderWrongStatusError(
                "Подавать предложения можно только на новые заказы"
            )
        if order.user_id == driver_user_id:
            raise OfferAccessDeniedError(
                "Нельзя подать предложение на собственный заказ"
            )

        # Запрещаем дубли активных предложений от одного водителя на один заказ.
        existing = await self._offers.get_existing_pending(order.id, driver_user_id)
        if existing is not None:
            raise OfferAlreadyExistsError()

        offer = Offer(
            order_id=data.order_id,
            driver_user_id=driver_user_id,
            price=data.price,
            comment=data.comment,
            delivery_date=data.delivery_date,
            status=OfferStatus.PENDING,
        )
        return await self._offers.create(offer)

    async def withdraw(self, driver_user_id: uuid.UUID, offer_id: uuid.UUID) -> Offer:
        """Водитель отзывает своё ещё не принятое предложение. PENDING → WITHDRAWN."""
        offer = await self._offers.get_by_id(offer_id)
        if offer is None:
            raise OfferNotFoundError()
        if offer.driver_user_id != driver_user_id:
            raise OfferAccessDeniedError("Это не ваше предложение")
        if offer.status != OfferStatus.PENDING:
            raise OfferWrongStatusError("Отозвать можно только активное предложение")

        offer.status = OfferStatus.WITHDRAWN
        offer.updated_at = datetime.now(UTC)
        await self._offers.flush()
        return offer


def get_offer_service(
    offer_repo: OfferRepositoryDep, order_repo: OrderRepositoryDep
) -> OfferService:
    return OfferService(offer_repo, order_repo)


OfferServiceDep = Annotated[OfferService, Depends(get_offer_service)]
