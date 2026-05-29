import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends

from data.entities.Vehicle import Vehicle
from data.repositories.DriverRepo import DriverRepository, DriverRepositoryDep
from data.repositories.VehicleRepo import VehicleRepository, VehicleRepositoryDep
from data.schemas.Vehicle import VehicleCreate, VehicleRead, VehicleUpdate
from services.Exeptions import DriverNotFoundError, VehicleAccessDeniedError, VehicleNotFoundError


class VehicleService:
    def __init__(self, repo: VehicleRepository, driver_repo: DriverRepository) -> None:
        self._repo = repo
        self._driver_repo = driver_repo

    @staticmethod
    def to_read(v: Vehicle) -> VehicleRead:
        return VehicleRead(
            id=v.id,
            driver_id=v.driver_id,
            brand=v.brand,
            model=v.model,
            reg_number=v.reg_number,
            registration_docs=v.registration_docs,
            insurance=v.insurance,
            capacity=v.capacity,
            created_at=v.created_at,
            updated_at=v.updated_at,
        )

    async def list_for_user(self, user_id: uuid.UUID) -> Sequence[Vehicle]:
        driver = await self._driver_repo.get_by_user_id(user_id)
        if driver is None:
            raise DriverNotFoundError()
        return await self._repo.get_by_driver_id(driver.id)

    async def create_for_user(self, user_id: uuid.UUID, data: VehicleCreate) -> Vehicle:
        driver = await self._driver_repo.get_by_user_id(user_id)
        if driver is None:
            raise DriverNotFoundError()
        v = Vehicle(driver_id=driver.id, **data.model_dump())
        return await self._repo.create(v)

    async def update_for_user(
        self, user_id: uuid.UUID, vehicle_id: uuid.UUID, data: VehicleUpdate
    ) -> Vehicle:
        driver = await self._driver_repo.get_by_user_id(user_id)
        if driver is None:
            raise DriverNotFoundError()

        v = await self._repo.get_by_id(vehicle_id)
        if v is None:
            raise VehicleNotFoundError()
        if v.driver_id != driver.id:
            raise VehicleAccessDeniedError()

        updated = await self._repo.update(vehicle_id, data)
        if updated is None:
            raise VehicleNotFoundError()
        return updated

    async def delete_for_user(self, user_id: uuid.UUID, vehicle_id: uuid.UUID) -> bool:
        driver = await self._driver_repo.get_by_user_id(user_id)
        if driver is None:
            raise DriverNotFoundError()

        v = await self._repo.get_by_id(vehicle_id)
        if v is None:
            raise VehicleNotFoundError()
        if v.driver_id != driver.id:
            raise VehicleAccessDeniedError()

        return await self._repo.delete(vehicle_id)


def get_vehicle_service(
    repo: VehicleRepositoryDep, driver_repo: DriverRepositoryDep
) -> VehicleService:
    return VehicleService(repo, driver_repo)


VehicleServiceDep = Annotated[VehicleService, Depends(get_vehicle_service)]
