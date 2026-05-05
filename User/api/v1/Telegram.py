from fastapi import APIRouter, HTTPException
from sqlmodel import SQLModel, Field

from api.routes import API_V1_PREFIX, TELEGRAM
from data.schemas.Auth import RegisterIn, RegisterOut, SmsRequestIn, SmsVerifyIn
from data.schemas.User import UserRead
from services.AuthService import AuthServiceDep
from services.Exeptions import AppException
from services.UserService import UserService, UserServiceDep

router = APIRouter(prefix=f"{API_V1_PREFIX}{TELEGRAM}", tags=["Telegram"])

_r = UserService.to_read


# ── Schemas ────────────────────────────────────────────────────

class TelegramTokensOut(SQLModel):
    access_token: str
    refresh_token: str


class TelegramRefreshIn(SQLModel):
    refresh_token: str


class TelegramUserCheck(SQLModel):
    exists: bool
    user: UserRead | None = None


# ── Check if user is registered by telegram_user_id ────────────

@router.get("/check/{telegram_user_id}", response_model=TelegramUserCheck)
async def check_telegram_user(
    telegram_user_id: str,
    user_service: UserServiceDep,
):
    """Проверить, зарегистрирован ли пользователь по Telegram ID."""
    user = await user_service._repo.get_by_telegram_user_id(telegram_user_id)
    if user is None:
        return TelegramUserCheck(exists=False)
    return TelegramUserCheck(exists=True, user=_r(user))


# ── Register via Telegram ──────────────────────────────────────

@router.post("/register", response_model=RegisterOut, status_code=201)
async def telegram_register(data: RegisterIn, auth_service: AuthServiceDep):
    """Регистрация через Telegram. Возвращает debug_code для разработки."""
    try:
        _user, code = await auth_service.register(data)
    except AppException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    # TODO: убрать debug_code перед продакшеном
    return RegisterOut(
        success=True,
        message=f"Пользователь создан через Telegram. Код: {code}",
    )


# ── Request sign-in code ───────────────────────────────────────

@router.post("/request-code")
async def telegram_request_code(
    data: SmsRequestIn,
    auth_service: AuthServiceDep,
):
    """Запрос кода авторизации для Telegram-пользователя."""
    try:
        code = await auth_service.request_sign_in_code(data.phone)
    except AppException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    # TODO: убрать debug_code перед продакшеном
    return {"status": "ok", "message": "Код отправлен", "debug_code": code}


# ── Verify code and get tokens (no cookies) ────────────────────

@router.post("/verify-code", response_model=TelegramTokensOut)
async def telegram_verify_code(
    data: SmsVerifyIn,
    auth_service: AuthServiceDep,
):
    """Подтвердить код и получить оба токена в теле ответа (без cookie)."""
    try:
        _user, access, refresh = await auth_service.verify_sign_in_code(
            data.phone, data.code
        )
    except AppException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    return TelegramTokensOut(access_token=access, refresh_token=refresh)


# ── Refresh tokens via body ────────────────────────────────────

@router.post("/refresh", response_model=TelegramTokensOut)
async def telegram_refresh(
    data: TelegramRefreshIn,
    auth_service: AuthServiceDep,
):
    """Обновить токены. Refresh-токен передаётся в теле запроса."""
    try:
        access, new_refresh = await auth_service.refresh_tokens(data.refresh_token)
    except AppException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    return TelegramTokensOut(access_token=access, refresh_token=new_refresh)
