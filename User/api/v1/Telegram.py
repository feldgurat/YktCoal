from fastapi import APIRouter, HTTPException

from api.routes import API_V1_PREFIX, TELEGRAM
from data.schemas.Auth import RegisterIn, RegisterOut
from services.AuthService import AuthServiceDep
from services.Exeptions import AppException

router = APIRouter(prefix=f"{API_V1_PREFIX}{TELEGRAM}", tags=["Telegram"])


@router.post("/register", response_model=RegisterOut, status_code=201)
async def telegram_register(data: RegisterIn, auth_service: AuthServiceDep):
    """TODO: добавить проверку telegram-токена / webhook secret."""
    try:
        _user, code = await auth_service.register(data)
    except AppException as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.message)

    return RegisterOut(success=True, message="Пользователь создан через Telegram")
