from uuid import UUID

from fastapi import APIRouter, HTTPException

from api.routes import API_V1_PREFIX, APPLICATIONS
from api.v1.dependencies import CurrentAdminDep, CurrentTokenUserDep
from data.schemas.Application import ApplicationCreate, ApplicationRead, ApplicationReject
from services.ApplicationService import ApplicationServiceDep
from services.Exceptions import AppException

router = APIRouter(prefix=f"{API_V1_PREFIX}{APPLICATIONS}", tags=["Applications"])


def _handle(exc: AppException):
    raise HTTPException(status_code=exc.status_code, detail=exc.message)


# ── Пользователь подаёт заявку ─────────────────────────────────

@router.post("", response_model=ApplicationRead, status_code=201)
async def create_application(
    data: ApplicationCreate,
    token_user: CurrentTokenUserDep,
    app_service: ApplicationServiceDep,
):
    """Пользователь подаёт заявку на становление водителем."""
    try:
        app = await app_service.create(token_user.id, data)
    except AppException as exc:
        _handle(exc)
    return app_service.to_read(app)


# ── Мои заявки ─────────────────────────────────────────────────

@router.get("/my", response_model=list[ApplicationRead])
async def get_my_applications(
    token_user: CurrentTokenUserDep,
    app_service: ApplicationServiceDep,
):
    apps = await app_service.get_by_user(token_user.id)
    return [app_service.to_read(a) for a in apps]


# ── Admin: список заявок ───────────────────────────────────────

@router.get("", response_model=list[ApplicationRead])
async def get_all_applications(
    _admin: CurrentAdminDep,
    app_service: ApplicationServiceDep,
):
    apps = await app_service.get_all()
    return [app_service.to_read(a) for a in apps]


@router.get("/pending", response_model=list[ApplicationRead])
async def get_pending_applications(
    _admin: CurrentAdminDep,
    app_service: ApplicationServiceDep,
):
    apps = await app_service.get_pending()
    return [app_service.to_read(a) for a in apps]


@router.get("/{app_id}", response_model=ApplicationRead)
async def get_application(
    app_id: UUID,
    _admin: CurrentAdminDep,
    app_service: ApplicationServiceDep,
):
    try:
        app = await app_service.get(app_id)
    except AppException as exc:
        _handle(exc)
    return app_service.to_read(app)


# ── Admin: одобрить / отклонить ────────────────────────────────

@router.post("/{app_id}/approve", response_model=ApplicationRead)
async def approve_application(
    app_id: UUID,
    _admin: CurrentAdminDep,
    app_service: ApplicationServiceDep,
):
    """Одобрить заявку. Создаёт профиль водителя и добавляет роль DRIVER в User."""
    try:
        app = await app_service.approve(app_id)
    except AppException as exc:
        _handle(exc)
    return app_service.to_read(app)


@router.post("/{app_id}/reject", response_model=ApplicationRead)
async def reject_application(
    app_id: UUID,
    data: ApplicationReject,
    _admin: CurrentAdminDep,
    app_service: ApplicationServiceDep,
):
    """Отклонить заявку с указанием причины."""
    try:
        app = await app_service.reject(app_id, data.reason)
    except AppException as exc:
        _handle(exc)
    return app_service.to_read(app)
