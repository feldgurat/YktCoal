import uuid
from typing import Annotated

from fastapi import Depends
from sqlmodel import select

from data.Database import SessionDep
from data.entities.Driver import Driver
from data.repositories.BaseRepo import BaseRepository


class DriverRepository(BaseRepository[Driver]):

    async def get_by_user_id(self, user_id: uuid.UUID) -> Driver | None:
        result = await self._session.exec(
            select(Driver).where(Driver.user_id == user_id)
        )
        return result.one_or_none()


def get_driver_repository(session: SessionDep) -> DriverRepository:
    return DriverRepository(session, Driver)


DriverRepositoryDep = Annotated[DriverRepository, Depends(get_driver_repository)]
