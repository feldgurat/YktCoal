from typing import Annotated, Sequence

from fastapi import Depends

from data.entities.Resource import Resource
from data.repositories.ResourceRepo import ResourceRepository, ResourceRepositoryDep
from data.schemas.Resource import ResourceCreate, ResourceRead, ResourceUpdate
from services.Exceptions import ResourceNotFoundError


class ResourceService:
    def __init__(self, repository: ResourceRepository) -> None:
        self._repo = repository

    @staticmethod
    def to_read(resource: Resource) -> ResourceRead:
        return ResourceRead(
            id=resource.id,
            name=resource.name,
            unit=resource.unit,
            price_per_unit=resource.price_per_unit,
            is_active=resource.is_active,
        )

    async def get(self, resource_id) -> Resource:
        resource = await self._repo.get_by_id(resource_id)
        if resource is None:
            raise ResourceNotFoundError()
        return resource

    async def get_list(self, active_only: bool = True) -> Sequence[Resource]:
        if active_only:
            return await self._repo.get_active()
        return await self._repo.get_all()

    async def create(self, data: ResourceCreate) -> Resource:
        resource = Resource(
            name=data.name,
            unit=data.unit,
            price_per_unit=data.price_per_unit,
        )
        return await self._repo.create(resource)

    async def update(self, resource_id, data: ResourceUpdate) -> Resource:
        resource = await self._repo.update(resource_id, data)
        if resource is None:
            raise ResourceNotFoundError()
        return resource

    async def delete(self, resource_id) -> bool:
        return await self._repo.delete(resource_id)


def get_resource_service(repo: ResourceRepositoryDep) -> ResourceService:
    return ResourceService(repo)


ResourceServiceDep = Annotated[ResourceService, Depends(get_resource_service)]
