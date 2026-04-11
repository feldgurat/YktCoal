from fastapi import Cookie
from fastapi.responses import JSONResponse
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from api.v1.dependencies import UserWithPayload
from api.routes import API_V1_PREFIX, AUTH
from data.schemas.Auth import (
    AccessTokenOut,
    RegisterIn,
    RegisterOut,
    SmsRequestIn,
    SmsVerifyIn,
    StatusOut,
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



@router.post("/sign-in-code-answer", response_model=AccessTokenOut)
async def verify_sign_in_code(data: SmsVerifyIn, auth_service: AuthServiceDep):
    try:
        _user, access, refresh = await auth_service.verify_sign_in_code(
            data.phone, data.code
        )
    except AppException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    response = JSONResponse(content={"access_token": access})
    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        secure=False,           # False для localhost без HTTPS
        samesite="strict",
        path="/api/auth",      # cookie летит только на auth-эндпоинты
        max_age=7 * 24 * 3600, # 7 дней
    )
    return response



@router.post("/refresh", response_model=AccessTokenOut)
async def refresh_tokens(
    auth_service: AuthServiceDep,
    refresh_token: str = Cookie(...),
):
    try:
        access, new_refresh = await auth_service.refresh_tokens(refresh_token)
    except AppException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    response = JSONResponse(content={"access_token": access})
    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/api/auth",
        max_age=7 * 24 * 3600,
    )
    return response

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

 

 
@router.post("/logout", response_model=StatusOut)
async def logout(
    auth_service: AuthServiceDep,
    user_and_payload: UserWithPayload,
    refresh_token: str = Cookie(...),
):
    _, payload = user_and_payload
    try:
        await auth_service.logout(payload, refresh_token)
    except AppException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    response = JSONResponse(content={"status": "ok"})
    response.delete_cookie("refresh_token", path="/api/auth")
    return response
 