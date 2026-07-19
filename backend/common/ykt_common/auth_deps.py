import uuid

from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import SQLModel

from .exceptions import AppException
from .token_auth import TokenAuthService

bearer_scheme = HTTPBearer(auto_error=False)


class AuthenticatedUser(SQLModel):
    """Лёгкое представление пользователя, восстановленное из JWT.
    Сервис не хранит таблицу users — все данные приходят из токена."""

    id: uuid.UUID
    roles: list[str]

    def has_role(self, role: str) -> bool:
        return role.lower() in (r.lower() for r in self.roles)


async def authenticate(
    credentials: HTTPAuthorizationCredentials | None,
    auth: TokenAuthService,
) -> AuthenticatedUser:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не передан Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = auth.decode_token(credentials.credentials, expected_type="access")
    except AppException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
            headers={"WWW-Authenticate": "Bearer"},
        ) from None

    jti = payload.get("jti")
    if jti is None or await auth.is_token_revoked(jti):
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
        current_version = await auth.get_token_version(str(user_id))
        if current_version is not None and token_version != current_version:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Токен устарел",
                headers={"WWW-Authenticate": "Bearer"},
            )

    roles = payload.get("roles") or []
    return AuthenticatedUser(id=user_id, roles=roles)
