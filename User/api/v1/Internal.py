from fastapi import APIRouter, Depends, Header, HTTPException, status

from api.routes import API_V1_PREFIX
from config import settings
from data.schemas.User import UserRead
from services.UserService import UserService, UserServiceDep

_r = UserService.to_read


async def verify_service_key(
    x_service_key: str = Header(..., alias="X-Service-Key"),
) -> None:
    if x_service_key != settings.INTERNAL_SERVICE_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Неверный сервисный ключ",
        )


router = APIRouter(
    prefix=f"{API_V1_PREFIX}/internal",
    tags=["Internal"],
    dependencies=[Depends(verify_service_key)],
)


@router.post("/users/{user_id}/roles/{role}", response_model=UserRead)
async def internal_add_role(
    user_id: str,
    role: str,
    user_service: UserServiceDep,
):
    """Внутренний эндпоинт: добавить роль пользователю. Защищён сервисным ключом."""
    user = await user_service.add_role(user_id, role)
    return _r(user)


@router.delete("/users/{user_id}/roles/{role}", response_model=UserRead)
async def internal_remove_role(
    user_id: str,
    role: str,
    user_service: UserServiceDep,
):
    """Внутренний эндпоинт: убрать роль у пользователя. Защищён сервисным ключом."""
    user = await user_service.remove_role(user_id, role)
    return _r(user)
