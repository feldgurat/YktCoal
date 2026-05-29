import uuid
from collections.abc import Callable
from typing import Annotated, Any

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from config import settings
from data.Redis import get_redis

bearer_scheme = HTTPBearer(auto_error=False)

_BLACKLIST_KEY = "token_bl:{jti}"


class TokenUser:
    """Минимальная информация о пользователе из JWT."""

    def __init__(self, user_id: uuid.UUID, roles: list[str], payload: dict[str, Any]) -> None:
        self.id = user_id
        self.roles = roles
        self.token_version: int = payload.get("ver", 0)
        self.jti: str = payload["jti"]
        self.payload = payload

    def has_role(self, role: str) -> bool:
        return role in self.roles


async def get_current_token_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> TokenUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не передан Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    raw_token = credentials.credentials

    try:
        payload = jwt.decode(
            raw_token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM],
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен просрочен",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный тип токена",
        )

    # Проверка blacklist в общем Redis
    jti = payload.get("jti")
    if jti:
        redis_client = get_redis()
        if await redis_client.exists(_BLACKLIST_KEY.format(jti=jti)):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен отозван",
                headers={"WWW-Authenticate": "Bearer"},
            )

    user_id = uuid.UUID(payload["sub"])
    roles = payload.get("roles", ["user"])
    if not isinstance(roles, list):
        roles = ["user"]

    return TokenUser(user_id, roles, payload)


CurrentTokenUserDep = Annotated[TokenUser, Depends(get_current_token_user)]


def require_role(role: str) -> Callable:
    async def _check(token_user: CurrentTokenUserDep) -> TokenUser:
        if not token_user.has_role(role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав",
            )
        return token_user

    return _check


CurrentAdminDep = Annotated[TokenUser, Depends(require_role("admin"))]
CurrentDriverDep = Annotated[TokenUser, Depends(require_role("driver"))]
