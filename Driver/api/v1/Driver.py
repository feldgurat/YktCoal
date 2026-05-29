from uuid import UUID

from Driver.services.Exeptions import AppException
from fastapi import APIRouter, HTTPException

from api.routes import API_V1_PREFIX, DRIVERS
from api.v1.dependencies import CurrentAdminDep, CurrentDriverDep
from data.schemas.Driver import DriverRead, DriverStatusRead, DriverUpdate
from services.DriverService import DriverServiceDep

router = APIRouter(prefix=f"{API_V1_PREFIX}{DRIVERS}", tags=["Drivers"])


def _handle(exc: AppException):
    raise HTTPException(status_code=exc.status_code, detail=exc.message)


# ── Водитель: свой профиль ─────────────────────────────────────


@router.get("/me", response_model=DriverRead)
async def get_my_profile(
    token_user: CurrentDriverDep,
    driver_service: DriverServiceDep,
):
    try:
        driver = await driver_service.get_by_user(token_user.id)
    except AppException as exc:
        _handle(exc)
    return driver_service.to_read(driver)


@router.patch("/me", response_model=DriverRead)
async def update_my_profile(
    data: DriverUpdate,
    token_user: CurrentDriverDep,
    driver_service: DriverServiceDep,
):
    try:
        driver = await driver_service.update(token_user.id, data)
    except AppException as exc:
        _handle(exc)
    return driver_service.to_read(driver)


# ── Внутренний: проверка статуса (для Order-сервиса) ───────────


@router.get("/by-user/{user_id}/status", response_model=DriverStatusRead)
async def get_driver_status(
    user_id: UUID,
    driver_service: DriverServiceDep,
):
    """Открытый эндпоинт для проверки статуса водителя другими сервисами."""
    try:
        driver = await driver_service.get_by_user(user_id)
    except AppException as exc:
        _handle(exc)
    return driver_service.to_status_read(driver)


# ── Admin ──────────────────────────────────────────────────────


@router.get("", response_model=list[DriverRead])
async def get_all_drivers(
    _admin: CurrentAdminDep,
    driver_service: DriverServiceDep,
):
    drivers = await driver_service.get_all()
    return [driver_service.to_read(d) for d in drivers]


@router.get("/{driver_id}", response_model=DriverRead)
async def get_driver(
    driver_id: UUID,
    _admin: CurrentAdminDep,
    driver_service: DriverServiceDep,
):
    try:
        driver = await driver_service.get(driver_id)
    except AppException as exc:
        _handle(exc)
    return driver_service.to_read(driver)


@router.post("/{driver_id}/block", response_model=DriverRead)
async def block_driver(
    driver_id: UUID,
    _admin: CurrentAdminDep,
    driver_service: DriverServiceDep,
):
    try:
        driver = await driver_service.block(driver_id)
    except AppException as exc:
        _handle(exc)
    return driver_service.to_read(driver)


@router.post("/{driver_id}/unblock", response_model=DriverRead)
async def unblock_driver(
    driver_id: UUID,
    _admin: CurrentAdminDep,
    driver_service: DriverServiceDep,
):
    try:
        driver = await driver_service.unblock(driver_id)
    except AppException as exc:
        _handle(exc)
    return driver_service.to_read(driver)
