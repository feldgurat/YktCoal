import uuid

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import FileResponse

from api.routes import API_V1_PREFIX, APPLICATIONS
from api.v1.dependencies import CurrentAdminDep, CurrentUserDep, get_current_user
from data.schemas.Application import (
    ApplicationCreate,
    ApplicationRead,
    ApplicationReject,
)
from data.schemas.Common import UploadedFileOut
from services.ApplicationService import ApplicationService, ApplicationServiceDep
from services.FileService import FileServiceDep

router = APIRouter(
    prefix=f"{API_V1_PREFIX}{APPLICATIONS}",
    tags=["Applications"],
    dependencies=[Depends(get_current_user)],
)

_r = ApplicationService.to_read


# ── Uploads ────────────────────────────────────────────────────


@router.post("/upload-doc", response_model=UploadedFileOut, status_code=201)
async def upload_doc(
    file: UploadFile,
    file_service: FileServiceDep,
    _user: CurrentUserDep,
):
    """
    Загрузить один документ (паспорт / права / страховка / ПТС-СТС).
    Возвращает имя файла, которое нужно подставить в соответствующее
    поле при создании заявки (license_url / passport, и т.д.).
    """
    filename = await file_service.save_upload(file)
    return UploadedFileOut(path=filename)


@router.get("/files/{filename}")
async def download_doc(
    filename: str,
    file_service: FileServiceDep,
    _user: CurrentUserDep,
):
    """
    Отдать ранее загруженный документ. Доступ — любой аутентифицированный
    пользователь (защита от анонимного скачивания), на MVP без fine-grained
    проверки владельца.
    """
    path = file_service.get_file_path(filename)
    return FileResponse(path)


# ── Current user ───────────────────────────────────────────────


@router.post("", response_model=ApplicationRead, status_code=201)
async def submit_application(
    data: ApplicationCreate,
    current_user: CurrentUserDep,
    service: ApplicationServiceDep,
):
    app = await service.submit(current_user.id, data)
    return _r(app)


@router.get("/me", response_model=list[ApplicationRead])
async def my_applications(current_user: CurrentUserDep, service: ApplicationServiceDep):
    apps = await service.get_my(current_user.id)
    return [_r(a) for a in apps]


# ── Admin ──────────────────────────────────────────────────────


@router.get("", response_model=list[ApplicationRead])
async def list_applications(service: ApplicationServiceDep, _admin: CurrentAdminDep):
    apps = await service.get_all()
    return [_r(a) for a in apps]


@router.get("/pending", response_model=list[ApplicationRead])
async def list_pending(service: ApplicationServiceDep, _admin: CurrentAdminDep):
    apps = await service.get_pending()
    return [_r(a) for a in apps]


@router.get("/{app_id}", response_model=ApplicationRead)
async def get_application(
    app_id: uuid.UUID, service: ApplicationServiceDep, _admin: CurrentAdminDep
):
    app = await service.get(app_id)
    return _r(app)


@router.post("/{app_id}/approve", response_model=ApplicationRead)
async def approve_application(
    app_id: uuid.UUID, service: ApplicationServiceDep, admin: CurrentAdminDep
):
    app = await service.approve(app_id, admin.id)
    return _r(app)


@router.post("/{app_id}/reject", response_model=ApplicationRead)
async def reject_application(
    app_id: uuid.UUID,
    data: ApplicationReject,
    service: ApplicationServiceDep,
    admin: CurrentAdminDep,
):
    app = await service.reject(app_id, admin.id, data.reason)
    return _r(app)
