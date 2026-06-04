import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlmodel import select

from data.Database import SessionDep
from data.entities.Order import Order, OrderStatus
from data.repositories.BaseRepo import BaseRepository


class OrderRepository(BaseRepository[Order]):
    async def get_by_user_id(self, user_id: uuid.UUID) -> Sequence[Order]:
        result = await self._session.exec(
            select(Order)
            .where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        return result.all()

    async def get_by_driver_id(self, driver_user_id: uuid.UUID) -> Sequence[Order]:
        result = await self._session.exec(
            select(Order)
            .where(Order.accepted_driver_id == driver_user_id)
            .order_by(Order.created_at.desc())
        )
        return result.all()

    async def get_available(self) -> Sequence[Order]:
        """Активные заказы со статусом NEW — доступны водителям для подачи Offer."""
        result = await self._session.exec(
            select(Order)
            .where(Order.status == OrderStatus.NEW)
            .order_by(Order.created_at.desc())
        )
        return result.all()


def get_order_repository(session: SessionDep) -> OrderRepository:
    return OrderRepository(session, Order)


OrderRepositoryDep = Annotated[OrderRepository, Depends(get_order_repository)]
