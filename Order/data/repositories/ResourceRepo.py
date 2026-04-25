from typing import Annotated, Sequence

from fastapi import Depends
from sqlmodel import select

from data.Database import SessionDep
from data.entities.Resource import Resource
from data.repositories.BaseRepo import BaseRepository


class ResourceRepository(BaseRepository[Resource]):
    async def get_active(self) -> Sequence[Resource]:
        result = await self._session.exec(
            select(Resource).where(Resource.is_active == True)
        )
        return result.all()

    async def get_by_name(self, name: str) -> Resource | None:
        result = await self._session.exec(
            select(Resource).where(Resource.name == name)
        )
        return result.one_or_none()


def get_resource_repository(session: SessionDep) -> ResourceRepository:
    return ResourceRepository(session, Resource)


ResourceRepositoryDep = Annotated[ResourceRepository, Depends(get_resource_repository)]
