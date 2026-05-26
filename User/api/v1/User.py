from fastapi import APIRouter, Depends

from api.routes import API_V1_PREFIX, USERS
from api.v1.dependencies import CurrentAdminDep, CurrentUserDep, get_current_user
from data.schemas.Common import MessageResponse
from data.schemas.User import UserCreate, UserRead, UserRoleUpdate, UserUpdate
from services.UserService import UserService, UserServiceDep

router = APIRouter(
    prefix=f"{API_V1_PREFIX}{USERS}",
    tags=["Users"],
    dependencies=[Depends(get_current_user)],
)

_r = UserService.to_read


# ── Current user ───────────────────────────────────────────────


@router.get("/me", response_model=UserRead)
async def get_my_profile(current_user: CurrentUserDep):
    return _r(current_user)


@router.patch("/me", response_model=UserRead)
async def update_my_profile(
    data: UserUpdate,
    current_user: CurrentUserDep,
    user_service: UserServiceDep,
):
    user = await user_service.update(current_user.id, data)
    return _r(user)


# ── Admin-only ─────────────────────────────────────────────────


@router.post("", response_model=UserRead, status_code=201)
async def create_user(
    data: UserCreate,
    user_service: UserServiceDep,
    _admin: CurrentAdminDep,
):
    user = await user_service.create(data)
    return _r(user)


@router.get("", response_model=list[UserRead])
async def get_users(user_service: UserServiceDep, _admin: CurrentAdminDep):
    users = await user_service.get_list()
    return [_r(u) for u in users]


@router.get("/by-role/{role}", response_model=list[UserRead])
async def get_users_by_role(role: str, user_service: UserServiceDep, _admin: CurrentAdminDep):
    users = await user_service.get_by_role(role)

    return [_r(u) for u in users]


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: str, user_service: UserServiceDep, _admin: CurrentAdminDep):
    user = await user_service.get(user_id)
    return _r(user)


@router.patch("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    data: UserUpdate,
    user_service: UserServiceDep,
    _admin: CurrentAdminDep,
):
    user = await user_service.update(user_id, data)
    return _r(user)


@router.delete("/{user_id}", response_model=MessageResponse)
async def delete_user(
    user_id: str,
    user_service: UserServiceDep,
    _admin: CurrentAdminDep,
):
    deleted = await user_service.delete(user_id)
    if deleted:
        return MessageResponse(success=True, message="Пользователь удалён")
    return MessageResponse(success=False, message="Пользователь не найден")


@router.post("/{user_id}/roles", response_model=UserRead)
async def add_role(
    user_id: str,
    data: UserRoleUpdate,
    user_service: UserServiceDep,
    _admin: CurrentAdminDep,
):
    user = await user_service.add_role(user_id, data.role)
    return _r(user)


@router.delete("/{user_id}/roles/{role}", response_model=UserRead)
async def remove_role(
    user_id: str,
    role: str,
    user_service: UserServiceDep,
    _admin: CurrentAdminDep,
):
    user = await user_service.remove_role(user_id, role)
    return _r(user)
