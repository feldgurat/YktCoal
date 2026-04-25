import uuid
from datetime import datetime, timezone
from typing import Annotated, Sequence

from fastapi import Depends

from data.entities.Order import ALLOWED_TRANSITIONS, STATUS_LABELS, Order, OrderStatus
from data.repositories.OrderRepo import OrderRepository, OrderRepositoryDep
from data.repositories.ResourceRepo import ResourceRepository, ResourceRepositoryDep
from data.schemas.Order import OrderCreate, OrderRead, OrderUpdate
from data.schemas.Resource import ResourceRead
from services.Exceptions import (
    AccessDeniedError,
    InvalidStatusTransitionError,
    OrderNotFoundError,
    ResourceNotFoundError,
)


class OrderService:
    def __init__(
        self,
        order_repo: OrderRepository,
        resource_repo: ResourceRepository,
    ) -> None:
        self._order_repo = order_repo
        self._resource_repo = resource_repo

    # ── Entity → Schema ────────────────────────────────────────

    @staticmethod
    def to_read(order: Order) -> OrderRead:
        resource_read = None
        if order.resource is not None:
            resource_read = ResourceRead(
                id=order.resource.id,
                name=order.resource.name,
                unit=order.resource.unit,
                price_per_unit=order.resource.price_per_unit,
                is_active=order.resource.is_active,
            )

        return OrderRead(
            id=order.id,
            client_id=order.client_id,
            driver_id=order.driver_id,
            dest_address=order.dest_address,
            latitude=order.latitude,
            longitude=order.longitude,
            resource=resource_read,
            volume=order.volume,
            cost=order.cost,
            delivery_date=order.delivery_date,
            comment=order.comment,
            status=order.status,
            status_label=STATUS_LABELS.get(
                OrderStatus(order.status), "Неизвестен"
            ),
            created_at=order.created_at,
            updated_at=order.updated_at,
        )

    # ── Queries ────────────────────────────────────────────────

    async def get(self, order_id: uuid.UUID) -> Order:
        order = await self._order_repo.get_by_id_with_resource(order_id)
        if order is None:
            raise OrderNotFoundError()
        return order

    async def get_all(self) -> Sequence[Order]:
        return await self._order_repo.get_all_with_resource()

    async def get_by_client(self, client_id: uuid.UUID) -> Sequence[Order]:
        return await self._order_repo.get_by_client(client_id)

    async def get_by_driver(self, driver_id: uuid.UUID) -> Sequence[Order]:
        return await self._order_repo.get_by_driver(driver_id)

    async def get_by_status(self, status: int) -> Sequence[Order]:
        return await self._order_repo.get_by_status(status)

    async def get_available(self) -> Sequence[Order]:
        return await self._order_repo.get_available()

    # ── Create ─────────────────────────────────────────────────

    async def create(self, client_id: uuid.UUID, data: OrderCreate) -> Order:
        resource = await self._resource_repo.get_by_id(data.resource_id)
        if resource is None:
            raise ResourceNotFoundError()

        cost = int(data.volume * resource.price_per_unit)

        order = Order(
            client_id=client_id,
            dest_address=data.dest_address,
            latitude=data.latitude,
            longitude=data.longitude,
            resource_id=data.resource_id,
            volume=data.volume,
            cost=cost,
            delivery_date=data.delivery_date,
            comment=data.comment,
            status=int(OrderStatus.NEW),
        )
        created = await self._order_repo.create(order)

        return await self.get(created.id)

    # ── Update ─────────────────────────────────────────────────

    async def update(
        self, order_id: uuid.UUID, data: OrderUpdate, requester_id: uuid.UUID
    ) -> Order:
        order = await self.get(order_id)

        if order.client_id != requester_id:
            raise AccessDeniedError()

        if order.order_status not in (OrderStatus.NEW,):
            raise InvalidStatusTransitionError(
                "Редактировать можно только заказ в статусе «Новый»"
            )

        order.updated_at = datetime.now(timezone.utc).isoformat()
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(order, field, value)

        # Пересчитать стоимость если изменился объём
        if data.volume is not None and order.resource is not None:
            order.cost = int(data.volume * order.resource.price_per_unit)

        await self._order_repo._session.flush()
        return await self.get(order_id)

    # ── Status transitions ─────────────────────────────────────

    async def change_status(self, order_id: uuid.UUID, new_status: int) -> Order:
        order = await self.get(order_id)
        target = OrderStatus(new_status)

        if not order.can_transition_to(target):
            current_label = STATUS_LABELS.get(order.order_status, "?")
            target_label = STATUS_LABELS.get(target, "?")
            raise InvalidStatusTransitionError(
                f"Нельзя перевести из «{current_label}» в «{target_label}»"
            )

        order.status = int(target)
        order.updated_at = datetime.now(timezone.utc).isoformat()
        await self._order_repo._session.flush()
        return await self.get(order_id)

    async def assign_driver(
        self, order_id: uuid.UUID, driver_id: uuid.UUID
    ) -> Order:
        order = await self.get(order_id)

        if order.order_status != OrderStatus.NEW:
            raise InvalidStatusTransitionError(
                "Назначить водителя можно только для нового заказа"
            )

        order.driver_id = driver_id
        order.status = int(OrderStatus.ACCEPTED)
        order.updated_at = datetime.now(timezone.utc).isoformat()
        await self._order_repo._session.flush()
        return await self.get(order_id)

    # ── Cancel (client) ────────────────────────────────────────

    async def cancel(self, order_id: uuid.UUID, requester_id: uuid.UUID) -> Order:
        order = await self.get(order_id)

        if order.client_id != requester_id:
            raise AccessDeniedError()

        if not order.can_transition_to(OrderStatus.CANCELLED):
            raise InvalidStatusTransitionError("Этот заказ нельзя отменить")

        order.status = int(OrderStatus.CANCELLED)
        order.updated_at = datetime.now(timezone.utc).isoformat()
        await self._order_repo._session.flush()
        return await self.get(order_id)


def get_order_service(
    order_repo: OrderRepositoryDep,
    resource_repo: ResourceRepositoryDep,
) -> OrderService:
    return OrderService(order_repo, resource_repo)


OrderServiceDep = Annotated[OrderService, Depends(get_order_service)]
