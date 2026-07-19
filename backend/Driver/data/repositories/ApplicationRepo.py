import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from sqlmodel import select

from data.Database import SessionDep
from data.entities.Application import Application
from data.entities.ApplicationStatus import ApplicationStatus
from data.repositories.BaseRepo import BaseRepository


class ApplicationRepository(BaseRepository[Application]):
    async def get_by_user_id(self, user_id: uuid.UUID) -> Sequence[Application]:
        result = await self._session.exec(
            select(Application)
            .where(Application.user_id == user_id)
            .order_by(Application.submission_date.desc())
        )
        return result.all()

    async def get_pending_by_user_id(self, user_id: uuid.UUID) -> Application | None:
        result = await self._session.exec(
            select(Application).where(
                Application.user_id == user_id,
                Application.status == ApplicationStatus.PENDING,
            )
        )
        return result.first()

    async def get_by_status(self, status: ApplicationStatus) -> Sequence[Application]:
        result = await self._session.exec(
            select(Application)
            .where(Application.status == status)
            .order_by(Application.submission_date.asc())
        )
        return result.all()


def get_application_repository(session: SessionDep) -> ApplicationRepository:
    return ApplicationRepository(session, Application)


ApplicationRepositoryDep = Annotated[ApplicationRepository, Depends(get_application_repository)]
