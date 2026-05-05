import logging
import uuid
from datetime import datetime, timezone
from typing import Annotated, Sequence

import httpx
from fastapi import Depends

from config import settings
from data.entities.Offer import OFFER_STATUS_LABELS, Offer, OfferStatus
from data.entities.Order import Order, OrderStatus
from data.repositories.OfferRepo import OfferRepository, OfferRepositoryDep
from data.repositories.OrderRepo import OrderRepository, OrderRepositoryDep
from data.schemas.Offer import OfferCreate, OfferRead
from services.Exceptions import (
    AccessDeniedError,
    DriverNotActiveError,
    DuplicateOfferError,
    OfferAlreadyHandledError,
    OfferNotFoundError,
    OrderNotAcceptingOffersError,
    OrderNotFoundError,
)

logger = logging.getLogger(__name__)


class OfferService:
    def __init__(
        self,
        offer_repo: OfferRepository,
        order_repo: OrderRepository,
    ) -> None:
        self._offer_repo = offer_repo
        self._order_repo = order_repo

    # ── Entity → Schema ────────────────────────────────────────

    @staticmethod
    def to_read(offer: Offer) -> OfferRead:
        return OfferRead(
            id=offer.id,
            order_id=offer.order_id,
            driver_id=offer.driver_id,
            price=offer.price,
            delivery_date=offer.delivery_date,
            comment=offer.comment,
            status=offer.status,
            status_label=OFFER_STATUS_LABELS.get(
                OfferStatus(offer.status), "Неизвестен"
            ),
            created_at=offer.created_at,
            updated_at=offer.updated_at,
        )

    # ── Helpers ────────────────────────────────────────────────

    async def _get_order_or_404(self, order_id: uuid.UUID) -> Order:
        order = await self._order_repo.get_by_id_with_resource(order_id)
        if order is None:
            raise OrderNotFoundError()
        return order

    async def _get_offer_or_404(self, offer_id: uuid.UUID) -> Offer:
        offer = await self._offer_repo.get_by_id(offer_id)
        if offer is None:
            raise OfferNotFoundError()
        return offer

    # ── Queries ────────────────────────────────────────────────

    async def get_by_order(self, order_id: uuid.UUID) -> Sequence[Offer]:
        return await self._offer_repo.get_by_order(order_id)

    async def get_by_driver(self, driver_id: uuid.UUID) -> Sequence[Offer]:
        return await self._offer_repo.get_by_driver(driver_id)

    # ── Driver создаёт предложение ─────────────────────────────

    async def create(
        self, order_id: uuid.UUID, driver_id: uuid.UUID, data: OfferCreate
    ) -> Offer:
        order = await self._get_order_or_404(order_id)

        if order.order_status != OrderStatus.NEW:
            raise OrderNotAcceptingOffersError()

        # Проверяем статус водителя в Driver-сервисе
        await self._check_driver_active(driver_id)

        existing = await self._offer_repo.get_by_order_and_driver(order_id, driver_id)
        if existing is not None:
            raise DuplicateOfferError()

        offer = Offer(
            order_id=order_id,
            driver_id=driver_id,
            price=data.price,
            delivery_date=data.delivery_date,
            comment=data.comment,
            status=int(OfferStatus.PENDING),
        )
        return await self._offer_repo.create(offer)

    @staticmethod
    async def _check_driver_active(driver_id: uuid.UUID) -> None:
        url = f"{settings.DRIVER_SERVICE_URL}/api/v1/drivers/by-user/{driver_id}/status"
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(url)
            if resp.status_code == 404:
                raise DriverNotActiveError("Профиль водителя не найден")
            resp.raise_for_status()
            data = resp.json()
            # status 1 = ACTIVE
            if data.get("status") != 1:
                raise DriverNotActiveError("Водитель заблокирован")
        except httpx.HTTPError as exc:
            logger.error("Driver status check failed for %s: %s", driver_id, exc)
            raise DriverNotActiveError("Не удалось проверить статус водителя")

    # ── Клиент принимает предложение ───────────────────────────

    async def accept(self, offer_id: uuid.UUID, client_id: uuid.UUID) -> Offer:
        offer = await self._get_offer_or_404(offer_id)
        order = await self._get_order_or_404(offer.order_id)

        if order.client_id != client_id:
            raise AccessDeniedError("Вы не владелец этого заказа")

        if offer.offer_status != OfferStatus.PENDING:
            raise OfferAlreadyHandledError()

        if order.order_status != OrderStatus.NEW:
            raise OrderNotAcceptingOffersError()

        # Принимаем этот оффер
        now = datetime.now(timezone.utc).isoformat()
        offer.status = int(OfferStatus.ACCEPTED)
        offer.updated_at = now

        # Назначаем водителя и цену на заказ
        order.driver_id = offer.driver_id
        order.cost = offer.price
        order.delivery_date = offer.delivery_date
        order.status = int(OrderStatus.ACCEPTED)
        order.updated_at = now

        # Отклоняем все остальные pending-офферы
        pending = await self._offer_repo.get_pending_by_order(offer.order_id)
        for other in pending:
            if other.id != offer.id:
                other.status = int(OfferStatus.REJECTED)
                other.updated_at = now

        await self._offer_repo._session.flush()
        return offer

    # ── Клиент отклоняет конкретное предложение ────────────────

    async def reject(self, offer_id: uuid.UUID, client_id: uuid.UUID) -> Offer:
        offer = await self._get_offer_or_404(offer_id)
        order = await self._get_order_or_404(offer.order_id)

        if order.client_id != client_id:
            raise AccessDeniedError("Вы не владелец этого заказа")

        if offer.offer_status != OfferStatus.PENDING:
            raise OfferAlreadyHandledError()

        offer.status = int(OfferStatus.REJECTED)
        offer.updated_at = datetime.now(timezone.utc).isoformat()
        await self._offer_repo._session.flush()
        return offer

    # ── Водитель отзывает своё предложение ─────────────────────

    async def withdraw(self, offer_id: uuid.UUID, driver_id: uuid.UUID) -> Offer:
        offer = await self._get_offer_or_404(offer_id)

        if offer.driver_id != driver_id:
            raise AccessDeniedError("Это не ваше предложение")

        if offer.offer_status != OfferStatus.PENDING:
            raise OfferAlreadyHandledError()

        offer.status = int(OfferStatus.WITHDRAWN)
        offer.updated_at = datetime.now(timezone.utc).isoformat()
        await self._offer_repo._session.flush()
        return offer


def get_offer_service(
    offer_repo: OfferRepositoryDep,
    order_repo: OrderRepositoryDep,
) -> OfferService:
    return OfferService(offer_repo, order_repo)


OfferServiceDep = Annotated[OfferService, Depends(get_offer_service)]
