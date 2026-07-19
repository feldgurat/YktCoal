from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from services.AuthService import AuthServiceDep
from ykt_common.auth_deps import AuthenticatedUser, authenticate, bearer_scheme

__all__ = [
    "AuthenticatedUser",
    "CurrentAdminDep",
    "CurrentDriverDep",
    "CurrentUserDep",
    "get_current_user",
    "require_role",
]


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    auth_service: AuthServiceDep,
) -> AuthenticatedUser:
    return await authenticate(credentials, auth_service)


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
