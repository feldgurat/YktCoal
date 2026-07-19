import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlmodel import select

from data.Database import SessionDep
from data.entities.Vehicle import Vehicle
from data.repositories.BaseRepo import BaseRepository


class VehicleRepository(BaseRepository[Vehicle]):
    async def get_by_driver_id(self, driver_id: uuid.UUID) -> Sequence[Vehicle]:
        result = await self._session.exec(select(Vehicle).where(Vehicle.driver_id == driver_id))
        return result.all()


def get_vehicle_repository(session: SessionDep) -> VehicleRepository:
    return VehicleRepository(session, Vehicle)


VehicleRepositoryDep = Annotated[VehicleRepository, Depends(get_vehicle_repository)]
