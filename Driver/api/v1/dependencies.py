import uuid
from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import SQLModel

from services.AuthService import AuthServiceDep
from services.Exeptions import AppException

bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser(SQLModel):
    """
    Лёгкое представление пользователя, восстановленное из JWT.
    Driver-сервис не хранит таблицу users — все данные приходят из токена.
    """

    id: uuid.UUID
    roles: list[str]

    def has_role(self, role: str) -> bool:
        return role.lower() in (r.lower() for r in self.roles)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    auth_service: AuthServiceDep,
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не передан Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = auth_service.decode_token(credentials.credentials, expected_type="access")
    except AppException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    jti = payload.get("jti")
    if jti is None or await auth_service.is_token_revoked(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен отозван",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = uuid.UUID(payload["sub"])
    except (KeyError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Невалидный токен",
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    token_version = payload.get("ver")
    if token_version is not None:
        current_version = await auth_service.get_token_version(str(user_id))
        if current_version is not None and token_version != current_version:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен устарел",
                headers={"WWW-Authenticate": "Bearer"},
            )

    roles = payload.get("roles") or []
    return AuthenticatedUser(id=user_id, roles=roles)


CurrentUserDep = Annotated[AuthenticatedUser, Depends(get_current_user)]


def require_role(role: str) -> Callable:
    async def _check(current_user: CurrentUserDep) -> AuthenticatedUser:
        if not current_user.has_role(role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав",
            )
        return current_user

    return _check


CurrentAdminDep = Annotated[AuthenticatedUser, Depends(require_role("admin"))]
CurrentDriverDep = Annotated[AuthenticatedUser, Depends(require_role("driver"))]
