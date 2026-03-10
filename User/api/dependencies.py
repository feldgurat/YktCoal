# api/dependencies.py

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from data.Database import SessionDep
from data.entities.Person import Person
from services.AuthService import decode_token, is_token_blacklisted
from services.Exeptions import InvalidToken, InvalidTokenType, TokenHasExpired
from services.PersonService import get_person_by_id

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_person(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
    session: SessionDep,
) -> Person:
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не передан Bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = decode_token(token, expected_type="access")
    except TokenHasExpired as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (InvalidToken, InvalidTokenType) as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
            headers={"WWW-Authenticate": "Bearer"},
        )

    jti = payload["jti"]
    if await is_token_blacklisted(jti):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен отозван",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload["sub"]
    if isinstance(user_id, str):
        user_id = UUID(user_id)

    person = await get_person_by_id(user_id, session)
    if not person:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_version = payload.get("ver")
    if token_version is not None and token_version != person.token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Токен устарел",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return person


CurrentPersonDep = Annotated[Person, Depends(get_current_person)]


async def get_current_admin(current_person: CurrentPersonDep) -> Person:
    if not current_person.isAdmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав",
        )
    return current_person


CurrentAdminDep = Annotated[Person, Depends(get_current_admin)]