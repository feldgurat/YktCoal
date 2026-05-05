import logging
import uuid
from datetime import datetime, timezone
from typing import Annotated, Sequence

import httpx
from fastapi import Depends

from config import settings
from data.entities.Application import (
    APPLICATION_STATUS_LABELS,
    Application,
    ApplicationStatus,
)
from data.entities.Driver import Driver, DriverStatus
from data.repositories.ApplicationRepo import (
    ApplicationRepository,
    ApplicationRepositoryDep,
)
from data.repositories.DriverRepo import DriverRepository, DriverRepositoryDep
from data.schemas.Application import ApplicationCreate, ApplicationRead
from services.Exceptions import (
    AlreadyDriverError,
    ApplicationAlreadyExistsError,
    ApplicationAlreadyHandledError,
    ApplicationNotFoundError,
    UserServiceError,
)

logger = logging.getLogger(__name__)


class ApplicationService:
    def __init__(
        self,
        app_repo: ApplicationRepository,
        driver_repo: DriverRepository,
    ) -> None:
        self._app_repo = app_repo
        self._driver_repo = driver_repo

    @staticmethod
    def to_read(app: Application) -> ApplicationRead:
        return ApplicationRead(
            id=app.id,
            user_id=app.user_id,
            vehicle_brand=app.vehicle_brand,
            vehicle_model=app.vehicle_model,
            vehicle_plate=app.vehicle_plate,
            vehicle_capacity_tons=app.vehicle_capacity_tons,
            license_url=app.license_url,
            insurance_url=app.insurance_url,
            comment=app.comment,
            reject_reason=app.reject_reason,
            status=app.status,
            status_label=APPLICATION_STATUS_LABELS.get(
                ApplicationStatus(app.status), "Неизвестен"
            ),
            created_at=app.created_at,
            updated_at=app.updated_at,
        )

    # ── Queries ────────────────────────────────────────────────

    async def get(self, app_id: uuid.UUID) -> Application:
        app = await self._app_repo.get_by_id(app_id)
        if app is None:
            raise ApplicationNotFoundError()
        return app

    async def get_pending(self) -> Sequence[Application]:
        return await self._app_repo.get_pending()

    async def get_all(self) -> Sequence[Application]:
        return await self._app_repo.get_all()

    async def get_by_user(self, user_id: uuid.UUID) -> Sequence[Application]:
        return await self._app_repo.get_by_user(user_id)

    # ── Пользователь подаёт заявку ─────────────────────────────

    async def create(
        self, user_id: uuid.UUID, data: ApplicationCreate
    ) -> Application:
        # Уже водитель?
        existing_driver = await self._driver_repo.get_by_user_id(user_id)
        if existing_driver is not None:
            raise AlreadyDriverError()

        # Уже есть pending-заявка?
        existing_app = await self._app_repo.get_pending_by_user(user_id)
        if existing_app is not None:
            raise ApplicationAlreadyExistsError()

        app = Application(
            user_id=user_id,
            vehicle_brand=data.vehicle_brand,
            vehicle_model=data.vehicle_model,
            vehicle_plate=data.vehicle_plate,
            vehicle_capacity_tons=data.vehicle_capacity_tons,
            license_url=data.license_url,
            insurance_url=data.insurance_url,
            comment=data.comment,
        )
        return await self._app_repo.create(app)

    # ── Админ одобряет заявку ──────────────────────────────────

    async def approve(self, app_id: uuid.UUID) -> Application:
        app = await self.get(app_id)

        if app.application_status != ApplicationStatus.PENDING:
            raise ApplicationAlreadyHandledError()

        now = datetime.now(timezone.utc).isoformat()

        # Создаём профиль водителя
        driver = Driver(
            user_id=app.user_id,
            vehicle_brand=app.vehicle_brand,
            vehicle_model=app.vehicle_model,
            vehicle_plate=app.vehicle_plate,
            vehicle_capacity_tons=app.vehicle_capacity_tons,
            license_url=app.license_url,
            insurance_url=app.insurance_url,
            status=int(DriverStatus.ACTIVE),
        )
        await self._driver_repo.create(driver)

        # Добавляем роль DRIVER в User-сервисе
        await self._add_driver_role(app.user_id)

        app.status = int(ApplicationStatus.APPROVED)
        app.updated_at = now
        await self._app_repo._session.flush()
        return app

    # ── Админ отклоняет заявку ─────────────────────────────────

    async def reject(self, app_id: uuid.UUID, reason: str) -> Application:
        app = await self.get(app_id)

        if app.application_status != ApplicationStatus.PENDING:
            raise ApplicationAlreadyHandledError()

        app.status = int(ApplicationStatus.REJECTED)
        app.reject_reason = reason
        app.updated_at = datetime.now(timezone.utc).isoformat()
        await self._app_repo._session.flush()
        return app

    # ── HTTP-вызов в User ──────────────────────────────────────

    @staticmethod
    async def _add_driver_role(user_id: uuid.UUID) -> None:
        url = (
            f"{settings.USER_SERVICE_URL}"
            f"/api/v1/internal/users/{user_id}/roles/driver"
        )
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.post(
                    url,
                    headers={"X-Service-Key": settings.INTERNAL_SERVICE_KEY},
                )
                resp.raise_for_status()
        except httpx.HTTPError as exc:
            logger.error("Failed to add driver role for %s: %s", user_id, exc)
            raise UserServiceError(
                f"Не удалось добавить роль водителя: {exc}"
            )


def get_application_service(
    app_repo: ApplicationRepositoryDep,
    driver_repo: DriverRepositoryDep,
) -> ApplicationService:
    return ApplicationService(app_repo, driver_repo)


ApplicationServiceDep = Annotated[
    ApplicationService, Depends(get_application_service)
]
