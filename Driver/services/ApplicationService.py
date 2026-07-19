import uuid
from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends

from data.entities.Application import Application
from data.entities.ApplicationStatus import ApplicationStatus
from data.entities.Driver import Driver
from data.entities.Vehicle import Vehicle
from data.repositories.ApplicationRepo import ApplicationRepository, ApplicationRepositoryDep
from data.repositories.DriverRepo import DriverRepository, DriverRepositoryDep
from data.repositories.VehicleRepo import VehicleRepository, VehicleRepositoryDep
from data.schemas.Application import ApplicationCreate, ApplicationRead
from services.Exeptions import (
    ApplicationAlreadyExistsError,
    ApplicationNotFoundError,
    ApplicationWrongStatusError,
    DriverAlreadyExistsError,
)
from services.UserServiceClient import UserServiceClient, UserServiceClientDep


class ApplicationService:
    def __init__(
        self,
        app_repo: ApplicationRepository,
        driver_repo: DriverRepository,
        vehicle_repo: VehicleRepository,
        user_client: UserServiceClient,
    ) -> None:
        self._app_repo = app_repo
        self._driver_repo = driver_repo
        self._vehicle_repo = vehicle_repo
        self._user_client = user_client

    # ── Entity → Schema ────────────────────────────────────────

    @staticmethod
    def to_read(app: Application) -> ApplicationRead:
        return ApplicationRead(
            id=app.id,
            user_id=app.user_id,
            status=app.status,
            license_url=app.license_url,
            passport=app.passport,
            vehicles_snapshot=app.vehicles_snapshot,
            submission_date=app.submission_date,
            reviewed_at=app.reviewed_at,
            reviewed_by=app.reviewed_by,
            rejection_reason=app.rejection_reason,
            created_at=app.created_at,
            updated_at=app.updated_at,
        )

    # ── CRUD ───────────────────────────────────────────────────

    async def submit(self, user_id: uuid.UUID, data: ApplicationCreate) -> Application:
        # Пользователь уже водитель → новую заявку не нужно.
        existing_driver = await self._driver_repo.get_by_user_id(user_id)
        if existing_driver is not None:
            raise DriverAlreadyExistsError()

        # Уже есть pending-заявка → запрещаем дубли.
        pending = await self._app_repo.get_pending_by_user_id(user_id)
        if pending is not None:
            raise ApplicationAlreadyExistsError()

        app = Application(
            user_id=user_id,
            status=ApplicationStatus.PENDING,
            license_url=data.license_url,
            passport=data.passport,
            vehicles_snapshot=[v.model_dump() for v in data.vehicles],
        )
        return await self._app_repo.create(app)

    async def get(self, app_id: uuid.UUID) -> Application:
        app = await self._app_repo.get_by_id(app_id)
        if app is None:
            raise ApplicationNotFoundError()
        return app

    async def get_my(self, user_id: uuid.UUID) -> Sequence[Application]:
        return await self._app_repo.get_by_user_id(user_id)

    async def get_pending(self) -> Sequence[Application]:
        return await self._app_repo.get_by_status(ApplicationStatus.PENDING)

    async def get_all(self) -> Sequence[Application]:
        return await self._app_repo.get_all()

    # ── Approve / Reject ───────────────────────────────────────

    async def approve(self, app_id: uuid.UUID, admin_user_id: uuid.UUID) -> Application:
        app = await self.get(app_id)
        if app.status != ApplicationStatus.PENDING:
            raise ApplicationWrongStatusError(
                f"Одобрить можно только pending-заявку, текущий статус: {app.status}"
            )

        # На всякий случай — вдруг пользователь стал водителем как-то ещё.
        existing_driver = await self._driver_repo.get_by_user_id(app.user_id)
        if existing_driver is not None:
            raise DriverAlreadyExistsError()

        # 1. Создаём Driver.
        driver = Driver(user_id=app.user_id, application_id=app.id)
        await self._driver_repo.create(driver)

        # 2. Разворачиваем снепшот машин в реальные Vehicle.
        for v in app.vehicles_snapshot:
            vehicle = Vehicle(
                driver_id=driver.id,
                brand=v["brand"],
                model=v["model"],
                reg_number=v["reg_number"],
                registration_docs=v["registration_docs"],
                insurance=v["insurance"],
                capacity=int(v["capacity"]),
            )
            await self._vehicle_repo.create(vehicle)

        # 3. Обновляем заявку.
        app.status = ApplicationStatus.APPROVED
        app.reviewed_at = datetime.now(UTC)
        app.reviewed_by = admin_user_id
        await self._app_repo.flush()

        # 4. Идём в User-сервис добавить роль 'driver'.
        # Это последний шаг: если упадёт — данные в Driver-сервисе уже консистентны,
        # роль можно добавить вручную через /api/v1/internal/users/{id}/roles/driver.
        # Если успех — commit всей транзакции произойдёт в зависимости get_session().
        await self._user_client.add_driver_role(app.user_id)

        return app

    async def reject(self, app_id: uuid.UUID, admin_user_id: uuid.UUID, reason: str) -> Application:
        app = await self.get(app_id)
        if app.status != ApplicationStatus.PENDING:
            raise ApplicationWrongStatusError(
                f"Отклонить можно только pending-заявку, текущий статус: {app.status}"
            )

        app.status = ApplicationStatus.REJECTED
        app.reviewed_at = datetime.now(UTC)
        app.reviewed_by = admin_user_id
        app.rejection_reason = reason
        await self._app_repo.flush()
        return app


def get_application_service(
    app_repo: ApplicationRepositoryDep,
    driver_repo: DriverRepositoryDep,
    vehicle_repo: VehicleRepositoryDep,
    user_client: UserServiceClientDep,
) -> ApplicationService:
    return ApplicationService(app_repo, driver_repo, vehicle_repo, user_client)


ApplicationServiceDep = Annotated[ApplicationService, Depends(get_application_service)]
