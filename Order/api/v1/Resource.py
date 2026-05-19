from uuid import UUID

from fastapi import APIRouter, HTTPException

from api.routes import API_V1_PREFIX, RESOURCES
from api.v1.dependencies import CurrentAdminDep, CurrentTokenUserDep
from data.schemas.Order import MessageResponse
from data.schemas.Resource import ResourceCreate, ResourceRead, ResourceUpdate
from services.Exceptions import AppException
from services.ResourceService import ResourceServiceDep

router = APIRouter(prefix=f"{API_V1_PREFIX}{RESOURCES}", tags=["Resources"])


def _handle(exc: AppException):
    raise HTTPException(status_code=exc.status_code, detail=exc.message)


@router.get("", response_model=list[ResourceRead])
async def get_resources(
    _token_user: CurrentTokenUserDep,
    resource_service: ResourceServiceDep,
    all: bool = False,
):
    """Список ресурсов. По умолчанию только активные."""
    resources = await resource_service.get_list(active_only=not all)
    return [resource_service.to_read(r) for r in resources]


@router.get("/{resource_id}", response_model=ResourceRead)
async def get_resource(
    resource_id: UUID,
    _token_user: CurrentTokenUserDep,
    resource_service: ResourceServiceDep,
):
    try:
        resource = await resource_service.get(resource_id)
    except AppException as exc:
        _handle(exc)
    return resource_service.to_read(resource)


@router.post("", response_model=ResourceRead, status_code=201)
async def create_resource(
    data: ResourceCreate,
    _admin: CurrentAdminDep,
    resource_service: ResourceServiceDep,
):
    """Создать ресурс (admin)."""
    try:
        resource = await resource_service.create(data)
    except AppException as exc:
        _handle(exc)
    return resource_service.to_read(resource)


@router.patch("/{resource_id}", response_model=ResourceRead)
async def update_resource(
    resource_id: UUID,
    data: ResourceUpdate,
    _admin: CurrentAdminDep,
    resource_service: ResourceServiceDep,
):
    """Обновить ресурс (admin)."""
    try:
        resource = await resource_service.update(resource_id, data)
    except AppException as exc:
        _handle(exc)
    return resource_service.to_read(resource)


@router.delete("/{resource_id}", response_model=MessageResponse)
async def delete_resource(
    resource_id: UUID,
    _admin: CurrentAdminDep,
    resource_service: ResourceServiceDep,
):
    """Удалить ресурс (admin)."""
    deleted = await resource_service.delete(resource_id)
    if deleted:
        return MessageResponse(success=True, message="Ресурс удалён")
    return MessageResponse(success=False, message="Ресурс не найден")
