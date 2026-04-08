from fastapi import APIRouter, HTTPException, status

from api.routes import API_V1_PREFIX, AUTH
from data.schemas.Auth import (
    RefreshIn,
    RegisterIn,
    RegisterOut,
    SmsRequestIn,
    SmsVerifyIn,
    TokenPair,
)
from services.AuthService import AuthServiceDep
from services.Exeptions import AppException

router = APIRouter(prefix=f"{API_V1_PREFIX}{AUTH}", tags=["Auth"])


@router.post("/sign-in-code-request")
async def request_sign_in_code(data: SmsRequestIn, auth_service: AuthServiceDep):
    try:
        code = await auth_service.request_sign_in_code(data.phone)
    except AppException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    # TODO: убрать debug_code перед продакшеном
    return {"status": "ok", "message": "Код отправлен", "debug_code": code}


@router.post("/sign-in-code-answer", response_model=TokenPair)
async def verify_sign_in_code(data: SmsVerifyIn, auth_service: AuthServiceDep):
    try:
        _user, access, refresh = await auth_service.verify_sign_in_code(
            data.phone, data.code
        )
    except AppException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    return TokenPair(access_token=access, refresh_token=refresh)


@router.post("/refresh", response_model=TokenPair)
async def refresh_tokens(data: RefreshIn, auth_service: AuthServiceDep):
    try:
        access, refresh = await auth_service.refresh_tokens(data.refresh_token)
    except AppException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    return TokenPair(access_token=access, refresh_token=refresh)


@router.post(
    "/register", response_model=RegisterOut, status_code=status.HTTP_201_CREATED
)
async def register(data: RegisterIn, auth_service: AuthServiceDep):
    try:
        _user, code = await auth_service.register(data)
    except AppException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    # TODO: убрать code перед продакшеном
    return RegisterOut(
        success=True, message=f"Пользователь создан. Код отправлен. {code}"
    )
