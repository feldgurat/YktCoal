import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status

from api.routes import API_V1_PREFIX, INTERNAL
from config import settings
from data.schemas.Driver import DriverRead
from services.DriverService import DriverService, DriverServiceDep


async def verify_service_key(
    x_service_key: str = Header(..., alias="X-Service-Key"),
) -> None:
    if x_service_key != settings.INTERNAL_SERVICE_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный сервисный ключ",
        )


router = APIRouter(
    prefix=f"{API_V1_PREFIX}{INTERNAL}",
    tags=["Internal"],
    dependencies=[Depends(verify_service_key)],
)

_r = DriverService.to_read


@router.get("/drivers/by-user/{user_id}", response_model=DriverRead | None)
async def internal_get_driver(user_id: uuid.UUID, service: DriverServiceDep):
    """Получить водителя по user_id. None если пользователь не водитель."""
    d = await service.get_by_user_id_or_none(user_id)
    return _r(d) if d else None
