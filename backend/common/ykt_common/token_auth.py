from typing import Any

import jwt

from .exceptions import InvalidTokenError, InvalidTokenTypeError, TokenExpiredError
from .redis import get_redis


class TokenAuthService:
    """Тонкая проверка JWT для сервисов без своей таблицы users:
    декодинг токена + blacklist + версия токена через общий Redis.
    Ключи blacklist/версии — те же, что пишет User-сервис."""

    _BLACKLIST_KEY = "token_bl:{jti}"
    _TOKEN_VER_KEY = "token_ver:{user_id}"

    def __init__(self, jwt_secret: str, jwt_algorithm: str) -> None:
        self._jwt_secret = jwt_secret
        self._jwt_algorithm = jwt_algorithm

    def decode_token(self, token: str, expected_type: str = "access") -> dict[str, Any]:
        try:
            payload = jwt.decode(token, self._jwt_secret, algorithms=[self._jwt_algorithm])
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError() from None
        except jwt.InvalidTokenError:
            raise InvalidTokenError() from None

        if payload.get("type") != expected_type:
            raise InvalidTokenTypeError()

        return payload

    async def is_token_revoked(self, jti: str) -> bool:
        key = self._BLACKLIST_KEY.format(jti=jti)
        return await get_redis().exists(key) > 0

    async def get_token_version(self, user_id: str) -> int | None:
        key = self._TOKEN_VER_KEY.format(user_id=user_id)
        value = await get_redis().get(key)
        return int(value) if value is not None else None
