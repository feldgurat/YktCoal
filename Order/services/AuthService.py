from typing import Annotated, Any

import jwt
import redis.asyncio as redis
from fastapi import Depends

from config import settings
from data.Redis import get_redis
from services.Exeptions import (
    InvalidTokenError,
    InvalidTokenTypeError,
    TokenExpiredError,
)


class AuthService:
    """
    Тонкий AuthService для Order-сервиса.
    Только декодинг JWT и проверка blacklist'а через общий Redis.
    """

    _BLACKLIST_KEY = "token_bl:{jti}"

    def __init__(self, redis_client: redis.Redis) -> None:
        self._redis = redis_client

    def decode_token(self, token: str, expected_type: str = "access") -> dict[str, Any]:
        try:
            payload = jwt.decode(
                token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
            )
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError() from None
        except jwt.InvalidTokenError:
            raise InvalidTokenError() from None

        if payload.get("type") != expected_type:
            raise InvalidTokenTypeError()

        return payload

    async def is_token_revoked(self, jti: str) -> bool:
        key = self._BLACKLIST_KEY.format(jti=jti)
        return await self._redis.exists(key) > 0


def get_auth_service() -> AuthService:
    return AuthService(get_redis())


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
