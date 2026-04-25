import uuid
from typing import Annotated, Sequence

from fastapi import Depends
from sqlmodel import select
from sqlalchemy.orm import selectinload

from data.Database import SessionDep
from data.entities.Order import Order
from data.entities.Resource import Resource
from data.repositories.BaseRepo import BaseRepository


class OrderRepository(BaseRepository[Order]):

    def _base_query(self):
        return select(Order).options(selectinload(Order.resource))

    async def get_by_id_with_resource(self, order_id: uuid.UUID) -> Order | None:
        result = await self._session.exec(
            self._base_query().where(Order.id == order_id)
        )
        return result.one_or_none()

    async def get_all_with_resource(self) -> Sequence[Order]:
        result = await self._session.exec(self._base_query())
        return result.all()

    async def get_by_client(self, client_id: uuid.UUID) -> Sequence[Order]:
        result = await self._session.exec(
            self._base_query().where(Order.client_id == client_id)
        )
        return result.all()

    async def get_by_driver(self, driver_id: uuid.UUID) -> Sequence[Order]:
        result = await self._session.exec(
            self._base_query().where(Order.driver_id == driver_id)
        )
        return result.all()

    async def get_by_status(self, status: int) -> Sequence[Order]:
        result = await self._session.exec(
            self._base_query().where(Order.status == status)
        )
        return result.all()

    async def get_available(self) -> Sequence[Order]:
        """Заказы в статусе NEW без назначенного водителя."""
        from data.entities.Order import OrderStatus

        result = await self._session.exec(
            self._base_query()
            .where(Order.status == int(OrderStatus.NEW))
            .where(Order.driver_id == None)
        )
        return result.all()


def get_order_repository(session: SessionDep) -> OrderRepository:
    return OrderRepository(session, Order)


OrderRepositoryDep = Annotated[OrderRepository, Depends(get_order_repository)]
