import uuid

from data.schemas.common import MessageResponse
from fastapi import APIRouter, Depends

from api.routes import API_V1_PREFIX, RESOURCES
from api.v1.dependencies import CurrentAdminDep, get_current_user
from data.schemas.Resource import ResourceCreate, ResourceRead, ResourceUpdate
from services.ResourceService import ResourceService, ResourceServiceDep

router = APIRouter(
    prefix=f"{API_V1_PREFIX}{RESOURCES}",
    tags=["Resources"],
    dependencies=[Depends(get_current_user)],
)

_r = ResourceService.to_read


# ── Anyone authenticated can read ──────────────────────────────


@router.get("", response_model=list[ResourceRead])
async def list_resources(service: ResourceServiceDep):
    items = await service.list_active()
    return [_r(x) for x in items]


@router.get("/{resource_id}", response_model=ResourceRead)
async def get_resource(resource_id: uuid.UUID, service: ResourceServiceDep):
    r = await service.get(resource_id)
    return _r(r)


# ── Admin ──────────────────────────────────────────────────────


@router.get("/all/full", response_model=list[ResourceRead])
async def list_all_resources(service: ResourceServiceDep, _admin: CurrentAdminDep):
    items = await service.list_all()
    return [_r(x) for x in items]


@router.post("", response_model=ResourceRead, status_code=201)
async def create_resource(
    data: ResourceCreate, service: ResourceServiceDep, _admin: CurrentAdminDep
):
    r = await service.create(data)
    return _r(r)


@router.patch("/{resource_id}", response_model=ResourceRead)
async def update_resource(
    resource_id: uuid.UUID,
    data: ResourceUpdate,
    service: ResourceServiceDep,
    _admin: CurrentAdminDep,
):
    r = await service.update(resource_id, data)
    return _r(r)


@router.delete("/{resource_id}", response_model=MessageResponse)
async def delete_resource(
    resource_id: uuid.UUID, service: ResourceServiceDep, _admin: CurrentAdminDep
):
    deleted = await service.delete(resource_id)
    if deleted:
        return MessageResponse(success=True, message="Ресурс удалён")
    return MessageResponse(success=False, message="Ресурс не найден")
