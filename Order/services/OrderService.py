import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated

from fastapi import Depends

from data.entities.Offer import Offer, OfferStatus
from data.entities.Order import Order, OrderStatus
from data.repositories.OfferRepo import OfferRepository, OfferRepositoryDep
from data.repositories.OrderRepo import OrderRepository, OrderRepositoryDep
from data.repositories.ResourceRepo import ResourceRepository, ResourceRepositoryDep
from data.schemas.Order import OrderCreate, OrderRead, OrderUpdate
from services.Exeptions import (
    OrderAccessDeniedError,
    OrderNotFoundError,
    OrderWrongStatusError,
    ResourceNotFoundError,
)


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        offer_repo: OfferRepository,
        resource_repo: ResourceRepository,
    ) -> None:
        self._orders = order_repo
        self._offers = offer_repo
        self._resources = resource_repo

    # ── Entity → Schema ────────────────────────────────────────

    @staticmethod
    def to_read(o: Order) -> OrderRead:
        return OrderRead(
            id=o.id,
            user_id=o.user_id,
            accepted_driver_id=o.accepted_driver_id,
            resource_id=o.resource_id,
            dest_address=o.dest_address,
            volume=o.volume,
            cost=o.cost,
            final_price=o.final_price,
            requested_delivery_date=o.requested_delivery_date,
            order_date=o.order_date,
            status=o.status,
            comment=o.comment,
            latitude=o.latitude,
            longitude=o.longitude,
            created_at=o.created_at,
            updated_at=o.updated_at,
        )

    # ── Queries ────────────────────────────────────────────────

    async def get(self, order_id: uuid.UUID) -> Order:
        o = await self._orders.get_by_id(order_id)
        if o is None:
            raise OrderNotFoundError()
        return o

    async def get_for_actor(
        self, actor_id: uuid.UUID, roles: list[str], order_id: uuid.UUID
    ) -> Order:
        order = await self.get(order_id)
        allowed = (
            actor_id == order.user_id
            or actor_id == order.accepted_driver_id
            or "admin" in roles
            or ("driver" in roles and order.status == OrderStatus.NEW)
        )
        if not allowed:
            raise OrderNotFoundError()
        return order

    async def list_my(self, user_id: uuid.UUID) -> Sequence[Order]:
        return await self._orders.get_by_user_id(user_id)

    async def list_driver_orders(self, driver_user_id: uuid.UUID) -> Sequence[Order]:
        return await self._orders.get_by_driver_id(driver_user_id)

    async def list_available(self) -> Sequence[Order]:
        """Заказы со статусом NEW — водители видят их для подачи Offer."""
        return await self._orders.get_available()

    async def list_all(self) -> Sequence[Order]:
        return await self._orders.get_all()

    # ── Create / Update ────────────────────────────────────────

    async def create(self, user_id: uuid.UUID, data: OrderCreate) -> Order:
        resource = await self._resources.get_by_id(data.resource_id)
        if resource is None:
            raise ResourceNotFoundError()

        cost = (data.volume * resource.price).quantize(Decimal("0.01"))
        o = Order(
            user_id=user_id,
            resource_id=data.resource_id,
            dest_address=data.dest_address,
            volume=data.volume,
            cost=cost,
            requested_delivery_date=data.requested_delivery_date,
            comment=data.comment,
            latitude=data.latitude,
            longitude=data.longitude,
            status=OrderStatus.NEW,
        )
        return await self._orders.create(o)

    async def update(self, user_id: uuid.UUID, order_id: uuid.UUID, data: OrderUpdate) -> Order:
        o = await self.get(order_id)
        if o.user_id != user_id:
            raise OrderAccessDeniedError("Можно редактировать только свои заказы")
        if o.status != OrderStatus.NEW:
            raise OrderWrongStatusError("Редактировать можно только новые заказы")

        resource_id = data.resource_id or o.resource_id
        resource = await self._resources.get_by_id(resource_id)
        if resource is None:
            raise ResourceNotFoundError()

        updated = await self._orders.update(order_id, data)
        if updated is None:
            raise OrderNotFoundError()

        updated.cost = (updated.volume * resource.price).quantize(Decimal("0.01"))
        await self._orders.flush()
        return updated

    # ── Status transitions ─────────────────────────────────────

    async def accept_offer(
        self, user_id: uuid.UUID, order_id: uuid.UUID, offer_id: uuid.UUID
    ) -> tuple[Order, Offer]:
        """
        Заказчик принимает один из встречных Offer.
        Order: NEW → ACCEPTED, проставляются accepted_driver_id и final_price.
        Этот Offer → ACCEPTED, остальные pending → REJECTED.
        """
        order = await self.get(order_id)
        if order.user_id != user_id:
            raise OrderAccessDeniedError("Принять предложение может только заказчик")
        if order.status != OrderStatus.NEW:
            raise OrderWrongStatusError("Принять предложение можно только для нового заказа")

        offer = await self._offers.get_by_id(offer_id)
        if offer is None or offer.order_id != order.id:
            raise OrderNotFoundError("Предложение не относится к этому заказу")
        if offer.status != OfferStatus.PENDING:
            raise OrderWrongStatusError("Это предложение уже не активно")

        now = datetime.now(UTC)

        # Приняли это предложение.
        offer.status = OfferStatus.ACCEPTED
        offer.updated_at = now

        # Остальные pending по этому заказу — Rejected.
        siblings = await self._offers.get_pending_for_order(order.id)
        for s in siblings:
            if s.id == offer.id:
                continue
            s.status = OfferStatus.REJECTED
            s.updated_at = now

        # Обновляем заказ.
        order.status = OrderStatus.ACCEPTED
        order.accepted_driver_id = offer.driver_user_id
        order.final_price = offer.price
        order.updated_at = now

        await self._orders.flush()
        return order, offer

    async def start(self, driver_user_id: uuid.UUID, order_id: uuid.UUID) -> Order:
        """Водитель начал выполнять заказ. ACCEPTED → IN_PROCESS."""
        order = await self.get(order_id)
        if order.accepted_driver_id != driver_user_id:
            raise OrderAccessDeniedError("Этот заказ назначен другому водителю")
        if order.status != OrderStatus.ACCEPTED:
            raise OrderWrongStatusError("Начать можно только заказ в статусе ACCEPTED")
        order.status = OrderStatus.IN_PROCESS
        order.updated_at = datetime.now(UTC)
        await self._orders.flush()
        return order

    async def complete(self, user_id: uuid.UUID, order_id: uuid.UUID) -> Order:
        """Заказчик подтверждает получение. IN_PROCESS → COMPLETED."""
        order = await self.get(order_id)
        if order.user_id != user_id:
            raise OrderAccessDeniedError("Подтвердить выполнение может только заказчик")
        if order.status != OrderStatus.IN_PROCESS:
            raise OrderWrongStatusError("Подтвердить выполнение можно только для заказа в работе")
        order.status = OrderStatus.COMPLETED
        order.updated_at = datetime.now(UTC)
        await self._orders.flush()
        return order

    async def cancel(self, user_id: uuid.UUID, order_id: uuid.UUID) -> Order:
        """
        Заказчик отменяет. Допустимо до тех пор, пока заказ не в IN_PROCESS.
        Активные Offer переходят в REJECTED.
        """
        order = await self.get(order_id)
        if order.user_id != user_id:
            raise OrderAccessDeniedError("Отменить заказ может только заказчик")
        if order.status not in (OrderStatus.NEW, OrderStatus.ACCEPTED):
            raise OrderWrongStatusError("Отменить можно только заказ в статусе NEW или ACCEPTED")

        now = datetime.now(UTC)
        for off in await self._offers.get_pending_for_order(order.id):
            off.status = OfferStatus.REJECTED
            off.updated_at = now

        order.status = OrderStatus.CANCELLED
        order.updated_at = now
        await self._orders.flush()
        return order

    async def driver_withdraw(self, driver_user_id: uuid.UUID, order_id: uuid.UUID) -> Order:
        """
        Водитель отказался от уже принятого заказа (Order=ACCEPTED, ещё не начал).
        Заказ возвращается в NEW, accepted_driver и final_price сбрасываются.
        Принятый Offer этого водителя → WITHDRAWN. Остальные старые Offer
        остаются REJECTED — заказчику нужно дождаться новых.
        """
        order = await self.get(order_id)
        if order.accepted_driver_id != driver_user_id:
            raise OrderAccessDeniedError("Этот заказ назначен другому водителю")
        if order.status != OrderStatus.ACCEPTED:
            raise OrderWrongStatusError(
                "Отказаться можно только до начала выполнения (статус ACCEPTED)"
            )

        # Находим accepted-offer этого водителя.
        all_offers = await self._offers.get_by_order_id(order.id)
        accepted = next(
            (
                o
                for o in all_offers
                if o.driver_user_id == driver_user_id and o.status == OfferStatus.ACCEPTED
            ),
            None,
        )
        now = datetime.now(UTC)
        if accepted is not None:
            accepted.status = OfferStatus.WITHDRAWN
            accepted.updated_at = now

        order.status = OrderStatus.NEW
        order.accepted_driver_id = None
        order.final_price = None
        order.updated_at = now
        await self._orders.flush()
        return order


def get_order_service(
    order_repo: OrderRepositoryDep,
    offer_repo: OfferRepositoryDep,
    resource_repo: ResourceRepositoryDep,
) -> OrderService:
    return OrderService(order_repo, offer_repo, resource_repo)


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
