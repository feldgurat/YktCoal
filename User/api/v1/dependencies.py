from typing import Annotated, Any, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from data.entities.User import User
from services.AuthService import AuthServiceDep
from services.Exeptions import AppException
from services.UserService import UserServiceDep

bearer_scheme = HTTPBearer(auto_error=False)

async def get_current_user_with_payload(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    auth_service: AuthServiceDep,
    user_service: UserServiceDep,
) -> tuple[User, dict[str, Any]]:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не передан Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
 
    try:
        payload = auth_service.decode_token(
            credentials.credentials, expected_type="access"
        )
    except AppException as exc:
        raise HTTPException(
            status_code=exc.status_code,
            detail=exc.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
 
    jti = payload["jti"]
    if await auth_service.is_token_revoked(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен отозван",
            headers={"WWW-Authenticate": "Bearer"},
        )
 
    user = await user_service._repo.get_by_id(payload["sub"])
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )
 
    token_version = payload.get("ver")
    if token_version is not None and token_version != user.token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен устарел",
            headers={"WWW-Authenticate": "Bearer"},
        )
 
    return user, payload
 
 
UserWithPayload = Annotated[tuple[User, dict[str, Any]], Depends(get_current_user_with_payload)]
 
 
async def get_current_user(
    user_with_payload: UserWithPayload,
) -> User:
    user, _ = user_with_payload
    return user
 
 
CurrentUserDep = Annotated[User, Depends(get_current_user)]
 
 
def require_role(role: str) -> Callable:
    async def _check(current_user: CurrentUserDep) -> User:
        if not current_user.has_role(role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Недостаточно прав",
            )
        return current_user
 
    return _check
 
 
CurrentAdminDep = Annotated[User, Depends(require_role("admin"))]
 