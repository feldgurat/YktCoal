from typing import Annotated

from fastapi import APIRouter, Cookie, Header, Response, status

from api.routes import API_V1_PREFIX, AUTH
from config import settings
from data.schemas.Auth import (
    AccessTokenOut,
    RegisterIn,
    RegisterOut,
    SmsRequestIn,
    SmsVerifyIn,
    StatusOut,
)
from services.AuthService import AuthServiceDep

router = APIRouter(prefix=f"{API_V1_PREFIX}{AUTH}", tags=["Auth"])


@router.post("/sign-in-code-request", response_model=StatusOut)
async def request_sign_in_code(data: SmsRequestIn, auth_service: AuthServiceDep):
    await auth_service.request_sign_in_code(data.phone)
    return StatusOut(status="ok")


@router.post("/sign-in-code-answer", response_model=AccessTokenOut)
async def verify_sign_in_code(data: SmsVerifyIn, auth_service: AuthServiceDep, response: Response):
    _user, access, refresh = await auth_service.verify_sign_in_code(data.phone, data.code)

    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="strict",
        path=f"{API_V1_PREFIX}{AUTH}",  # cookie летит только на auth-эндпоинты
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,  # 7 дней
    )
    return AccessTokenOut(access_token=access)


@router.post("/refresh", response_model=AccessTokenOut)
async def refresh_tokens(
    auth_service: AuthServiceDep,
    response: Response,
    refresh_token: str = Cookie(...),
):
    access, new_refresh = await auth_service.refresh_tokens(refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="strict",
        path=f"{API_V1_PREFIX}{AUTH}",
        max_age=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 3600,
    )
    return AccessTokenOut(access_token=access)


@router.post("/register", response_model=RegisterOut, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterIn, auth_service: AuthServiceDep):
    await auth_service.register(data)
    return RegisterOut(success=True, message="Пользователь создан. Код отправлен по SMS.")


@router.post("/logout", response_model=StatusOut)
async def logout(
    auth_service: AuthServiceDep,
    response: Response,
    refresh_token: Annotated[str | None, Cookie()] = None,
    authorization: Annotated[str | None, Header()] = None,
):
    """
    Выход из системы. Отзывает токены если возможно,
    удаляет cookie всегда.
    """
    access_payload = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:]
        access_payload = auth_service.decode_token(token, expected_type="access")

    await auth_service.logout(access_payload, refresh_token)

    response.delete_cookie("refresh_token", path=f"{API_V1_PREFIX}{AUTH}")
    return StatusOut(status="ok")
