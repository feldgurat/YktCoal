import uuid
from typing import Annotated, Sequence

from fastapi import Depends
from sqlmodel import select

from data.Database import SessionDep
from data.entities.Application import Application, ApplicationStatus
from data.repositories.BaseRepo import BaseRepository


class ApplicationRepository(BaseRepository[Application]):

    async def get_pending_by_user(self, user_id: uuid.UUID) -> Application | None:
        result = await self._session.exec(
            select(Application)
            .where(Application.user_id == user_id)
            .where(Application.status == int(ApplicationStatus.PENDING))
        )
        return result.first()

    async def get_by_user(self, user_id: uuid.UUID) -> Sequence[Application]:
        result = await self._session.exec(
            select(Application).where(Application.user_id == user_id)
        )
        return result.all()

    async def get_pending(self) -> Sequence[Application]:
        result = await self._session.exec(
            select(Application).where(
                Application.status == int(ApplicationStatus.PENDING)
            )
        )
        return result.all()


def get_application_repository(session: SessionDep) -> ApplicationRepository:
    return ApplicationRepository(session, Application)


ApplicationRepositoryDep = Annotated[
    ApplicationRepository, Depends(get_application_repository)
]
