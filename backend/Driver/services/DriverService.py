import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends

from data.entities.Driver import Driver
from data.repositories.DriverRepo import DriverRepository, DriverRepositoryDep
from data.schemas.Driver import DriverRead
from services.Exceptions import DriverNotFoundError


class DriverService:
    def __init__(self, repo: DriverRepository) -> None:
        self._repo = repo

    @staticmethod
    def to_read(d: Driver) -> DriverRead:
        return DriverRead(
            id=d.id,
            user_id=d.user_id,
            application_id=d.application_id,
            is_active=d.is_active,
            created_at=d.created_at,
            updated_at=d.updated_at,
        )

    async def get_by_user_id(self, user_id: uuid.UUID) -> Driver:
        d = await self._repo.get_by_user_id(user_id)
        if d is None:
            raise DriverNotFoundError()
        return d

    async def get_by_user_id_or_none(self, user_id: uuid.UUID) -> Driver | None:
        return await self._repo.get_by_user_id(user_id)

    async def get_all(self) -> Sequence[Driver]:
        return await self._repo.get_all()


def get_driver_service(repo: DriverRepositoryDep) -> DriverService:
    return DriverService(repo)


DriverServiceDep = Annotated[DriverService, Depends(get_driver_service)]
