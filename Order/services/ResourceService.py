import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends

from data.entities.Resource import Resource
from data.repositories.ResourceRepo import ResourceRepository, ResourceRepositoryDep
from data.schemas.Resource import ResourceCreate, ResourceRead, ResourceUpdate
from services.Exeptions import ResourceAlreadyExistsError, ResourceNotFoundError


class ResourceService:
    def __init__(self, repo: ResourceRepository) -> None:
        self._repo = repo

    @staticmethod
    def to_read(r: Resource) -> ResourceRead:
        return ResourceRead(
            id=r.id,
            name=r.name,
            price=r.price,
            is_active=r.is_active,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )

    async def list_active(self) -> Sequence[Resource]:
        return await self._repo.get_active()

    async def list_all(self) -> Sequence[Resource]:
        return await self._repo.get_all()

    async def get(self, resource_id: uuid.UUID) -> Resource:
        r = await self._repo.get_by_id(resource_id)
        if r is None:
            raise ResourceNotFoundError()
        return r

    async def create(self, data: ResourceCreate) -> Resource:
        if await self._repo.get_by_name(data.name) is not None:
            raise ResourceAlreadyExistsError()
        r = Resource(name=data.name, price=data.price)
        return await self._repo.create(r)

    async def update(self, resource_id: uuid.UUID, data: ResourceUpdate) -> Resource:
        r = await self._repo.update(resource_id, data)
        if r is None:
            raise ResourceNotFoundError()
        return r

    async def delete(self, resource_id: uuid.UUID) -> bool:
        return await self._repo.delete(resource_id)


def get_resource_service(repo: ResourceRepositoryDep) -> ResourceService:
    return ResourceService(repo)


ResourceServiceDep = Annotated[ResourceService, Depends(get_resource_service)]
