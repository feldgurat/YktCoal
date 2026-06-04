import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlmodel import SQLModel

from api.routes import API_V1_PREFIX, TELEGRAM
from config import settings
from data.schemas.Application import (
    ApplicationCreate,
    ApplicationRead,
    TgApplicationCreate,
)
from data.schemas.Common import UploadedFileOut
from data.schemas.Driver import DriverRead
from data.schemas.Vehicle import TgVehicleCreate, VehicleRead
from services.ApplicationService import ApplicationService, ApplicationServiceDep
from services.DriverService import DriverService, DriverServiceDep
from services.FileService import FileServiceDep
from services.VehicleService import VehicleService, VehicleServiceDep


async def verify_bot_key(
    x_service_key: str = Header(..., alias="X-Service-Key"),
) -> None:
    if x_service_key != settings.INTERNAL_TELEGRAM_SERVICE_KEY:
        raise HTTPException(status_code=403, detail="Неверный сервисный ключ")


router = APIRouter(
    prefix=f"{API_V1_PREFIX}{TELEGRAM}",
    tags=["Telegram"],
    dependencies=[Depends(verify_bot_key)],
)

_r_app = ApplicationService.to_read
_r_driver = DriverService.to_read
_r_vehicle = VehicleService.to_read


# Все ручки принимают user_id в теле (резолвится ботом через User-сервис заранее).


class TgUserRef(SQLModel):
    user_id: uuid.UUID


# ── Uploads ────────────────────────────────────────────────────


@router.post("/upload-doc", response_model=UploadedFileOut, status_code=201)
async def tg_upload_doc(file: UploadFile, file_service: FileServiceDep):
    filename = await file_service.save_upload(file)
    return UploadedFileOut(path=filename)


@router.get("/files/{filename}")
async def tg_download_doc(filename: str, file_service: FileServiceDep):
    path = file_service.get_file_path(filename)
    return FileResponse(path)


# ── Applications ───────────────────────────────────────────────


@router.post("/applications", response_model=ApplicationRead, status_code=201)
async def tg_submit_application(data: TgApplicationCreate, service: ApplicationServiceDep):
    # Отделяем user_id от ApplicationCreate, чтобы не передавать его лишний раз.
    payload = ApplicationCreate(
        license_url=data.license_url,
        passport=data.passport,
        vehicles=data.vehicles,
    )
    app = await service.submit(data.user_id, payload)
    return _r_app(app)


@router.get("/applications/by-user/{user_id}", response_model=list[ApplicationRead])
async def tg_my_applications(user_id: uuid.UUID, service: ApplicationServiceDep):
    apps = await service.get_my(user_id)
    return [_r_app(a) for a in apps]


# ── Driver / Vehicles ──────────────────────────────────────────


@router.get("/drivers/by-user/{user_id}", response_model=DriverRead | None)
async def tg_get_driver(user_id: uuid.UUID, service: DriverServiceDep):
    d = await service.get_by_user_id_or_none(user_id)
    return _r_driver(d) if d else None


@router.get("/drivers/by-user/{user_id}/vehicles", response_model=list[VehicleRead])
async def tg_list_vehicles(user_id: uuid.UUID, service: VehicleServiceDep):
    vehicles = await service.list_for_user(user_id)
    return [_r_vehicle(v) for v in vehicles]


@router.post("/drivers/vehicles", response_model=VehicleRead, status_code=201)
async def tg_add_vehicle(data: TgVehicleCreate, service: VehicleServiceDep):
    from data.schemas.Vehicle import VehicleCreate

    payload = VehicleCreate(
        brand=data.brand,
        model=data.model,
        reg_number=data.reg_number,
        registration_docs=data.registration_docs,
        insurance=data.insurance,
        capacity=data.capacity,
    )
    v = await service.create_for_user(data.user_id, payload)
    return _r_vehicle(v)
