import uuid

from fastapi import APIRouter, Depends

from api.routes import API_V1_PREFIX, DRIVERS
from api.v1.dependencies import CurrentAdminDep, CurrentUserDep, get_current_user
from data.schemas.Common import MessageResponse
from data.schemas.Driver import DriverRead
from data.schemas.Vehicle import VehicleCreate, VehicleRead, VehicleUpdate
from services.DriverService import DriverService, DriverServiceDep
from services.VehicleService import VehicleService, VehicleServiceDep

router = APIRouter(
    prefix=f"{API_V1_PREFIX}{DRIVERS}",
    tags=["Drivers"],
    dependencies=[Depends(get_current_user)],
)

_r_driver = DriverService.to_read
_r_vehicle = VehicleService.to_read


# ── Current driver ─────────────────────────────────────────────


@router.get("/me", response_model=DriverRead)
async def get_my_driver_profile(current_user: CurrentUserDep, service: DriverServiceDep):
    d = await service.get_by_user_id(current_user.id)
    return _r_driver(d)


@router.get("/me/vehicles", response_model=list[VehicleRead])
async def my_vehicles(current_user: CurrentUserDep, service: VehicleServiceDep):
    vehicles = await service.list_for_user(current_user.id)
    return [_r_vehicle(v) for v in vehicles]


@router.post("/me/vehicles", response_model=VehicleRead, status_code=201)
async def add_my_vehicle(
    data: VehicleCreate,
    current_user: CurrentUserDep,
    service: VehicleServiceDep,
):
    v = await service.create_for_user(current_user.id, data)
    return _r_vehicle(v)


@router.patch("/me/vehicles/{vehicle_id}", response_model=VehicleRead)
async def update_my_vehicle(
    vehicle_id: uuid.UUID,
    data: VehicleUpdate,
    current_user: CurrentUserDep,
    service: VehicleServiceDep,
):
    v = await service.update_for_user(current_user.id, vehicle_id, data)
    return _r_vehicle(v)


@router.delete("/me/vehicles/{vehicle_id}", response_model=MessageResponse)
async def delete_my_vehicle(
    vehicle_id: uuid.UUID,
    current_user: CurrentUserDep,
    service: VehicleServiceDep,
):
    deleted = await service.delete_for_user(current_user.id, vehicle_id)
    if deleted:
        return MessageResponse(success=True, message="Машина удалена")
    return MessageResponse(success=False, message="Машина не найдена")


# ── Admin ──────────────────────────────────────────────────────


@router.get("", response_model=list[DriverRead])
async def list_drivers(service: DriverServiceDep, _admin: CurrentAdminDep):
    drivers = await service.get_all()
    return [_r_driver(d) for d in drivers]
