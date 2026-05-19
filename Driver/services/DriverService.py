import uuid
from typing import Annotated, Sequence

from fastapi import Depends

from data.entities.Driver import DRIVER_STATUS_LABELS, Driver, DriverStatus
from data.repositories.DriverRepo import DriverRepository, DriverRepositoryDep
from data.schemas.Driver import DriverRead, DriverStatusRead, DriverUpdate
from services.Exceptions import AccessDeniedError, DriverNotFoundError


class DriverService:
    def __init__(self, repo: DriverRepository) -> None:
        self._repo = repo

    @staticmethod
    def to_read(driver: Driver) -> DriverRead:
        return DriverRead(
            id=driver.id,
            user_id=driver.user_id,
            vehicle_brand=driver.vehicle_brand,
            vehicle_model=driver.vehicle_model,
            vehicle_plate=driver.vehicle_plate,
            vehicle_capacity_tons=driver.vehicle_capacity_tons,
            license_url=driver.license_url,
            insurance_url=driver.insurance_url,
            rating=driver.rating,
            total_reviews=driver.total_reviews,
            status=driver.status,
            status_label=DRIVER_STATUS_LABELS.get(
                DriverStatus(driver.status), "Неизвестен"
            ),
            created_at=driver.created_at,
            updated_at=driver.updated_at,
        )

    @staticmethod
    def to_status_read(driver: Driver) -> DriverStatusRead:
        return DriverStatusRead(
            user_id=driver.user_id,
            status=driver.status,
            status_label=DRIVER_STATUS_LABELS.get(
                DriverStatus(driver.status), "Неизвестен"
            ),
        )

    async def get_by_user(self, user_id: uuid.UUID) -> Driver:
        driver = await self._repo.get_by_user_id(user_id)
        if driver is None:
            raise DriverNotFoundError()
        return driver

    async def get(self, driver_id: uuid.UUID) -> Driver:
        driver = await self._repo.get_by_id(driver_id)
        if driver is None:
            raise DriverNotFoundError()
        return driver

    async def get_all(self) -> Sequence[Driver]:
        return await self._repo.get_all()

    async def update(
        self, user_id: uuid.UUID, data: DriverUpdate
    ) -> Driver:
        driver = await self.get_by_user(user_id)
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(driver, field, value)
        await self._repo._session.flush()
        return driver

    async def block(self, driver_id: uuid.UUID) -> Driver:
        driver = await self.get(driver_id)
        driver.status = int(DriverStatus.BLOCKED)
        await self._repo._session.flush()
        return driver

    async def unblock(self, driver_id: uuid.UUID) -> Driver:
        driver = await self.get(driver_id)
        driver.status = int(DriverStatus.ACTIVE)
        await self._repo._session.flush()
        return driver


def get_driver_service(repo: DriverRepositoryDep) -> DriverService:
    return DriverService(repo)


DriverServiceDep = Annotated[DriverService, Depends(get_driver_service)]
