from fastapi import APIRouter, Depends, Header, HTTPException

from api.routes import API_V1_PREFIX, TELEGRAM
from config import settings
from data.entities.Role import Role
from data.entities.User import User
from data.repositories.UserRepo import UserRepositoryDep
from data.schemas.Telegram import TgLinkIn, TgRegisterIn
from data.schemas.User import UserRead
from services.Exceptions import UserAlreadyExistsError, UserNotFoundError
from services.UserService import UserService, UserServiceDep


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

_r = UserService.to_read


@router.get("/by-tg-id/{telegram_user_id}", response_model=UserRead | None)
async def find_by_tg_id(telegram_user_id: str, user_service: UserServiceDep):
    """Знаем ли мы этого Telegram-пользователя? Возвращает null если нет."""
    user = await user_service.get_by_telegram_user_id(telegram_user_id)
    return _r(user) if user else None


@router.get("/by-phone/{phone}", response_model=UserRead | None)
async def find_by_phone(phone: str, user_service: UserServiceDep):
    """Есть ли пользователь с таким телефоном (например, зарегался через веб)."""
    user = await user_service.get_by_contact_number(phone)
    return _r(user) if user else None


@router.post("/register", response_model=UserRead, status_code=201)
async def tg_register(data: TgRegisterIn, user_repo: UserRepositoryDep):
    """Регистрация через бот. Телефон уже верифицирован Telegram'ом, OTP не нужен."""
    existing = await user_repo.get_by_contact_number(data.phone)
    if existing is not None:
        raise UserAlreadyExistsError()

    user = User(
        name=data.name,
        contact_number=data.phone,
        telegram_user_id=data.telegram_user_id,
        address=data.address,
        roles=int(Role.USER),
    )
    await user_repo.create(user)
    return _r(user)


@router.post("/link", response_model=UserRead)
async def tg_link(data: TgLinkIn, user_repo: UserRepositoryDep):
    """Привязать tg_id к существующему пользователю (который регался через веб)."""
    user = await user_repo.get_by_contact_number(data.phone)
    if user is None:
        raise UserNotFoundError()
    user.telegram_user_id = data.telegram_user_id
    await user_repo.flush()
    return _r(user)
