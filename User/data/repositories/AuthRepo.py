from typing import Annotated

import redis.asyncio as redis
from fastapi import Depends

from config import settings
from data.Redis import get_redis


class AuthRepository:
    _OTP_KEY = "otp:{phone}"
    _RATE_KEY = "otp_rate:{phone}"
    _ATTEMPTS_KEY = "otp_attempts:{phone}"
    _BLACKLIST_KEY = "token_bl:{jti}"
    _TOKEN_VER_KEY = "token_ver:{user_id}"

    def __init__(self, redis_client: redis.Redis) -> None:
        self._redis = redis_client

    async def save_otp(self, phone: str, code_hash: str) -> None:
        key = self._OTP_KEY.format(phone=phone)
        await self._redis.setex(key, settings.OTP_TTL_SECONDS, code_hash)
        await self.reset_attempts(phone)

    async def get_otp(self, phone: str) -> str | None:
        key = self._OTP_KEY.format(phone=phone)
        return await self._redis.get(key)

    async def delete_otp(self, phone: str) -> None:
        key = self._OTP_KEY.format(phone=phone)
        await self._redis.delete(key)

    async def incr_attempts(self, phone: str) -> int:
        key = self._ATTEMPTS_KEY.format(phone=phone)
        async with self._redis.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.expire(key, settings.OTP_TTL_SECONDS)
            count, _ = await pipe.execute()
        return count

    async def reset_attempts(self, phone: str) -> None:
        key = self._ATTEMPTS_KEY.format(phone=phone)
        await self._redis.delete(key)

    async def is_rate_limited(self, phone: str) -> bool:
        key = self._RATE_KEY.format(phone=phone)
        return await self._redis.exists(key) > 0

    async def set_rate_limit(self, phone: str) -> None:
        key = self._RATE_KEY.format(phone=phone)
        await self._redis.setex(key, settings.OTP_RATE_LIMIT_SECONDS, "1")

    async def blacklist_token(self, jti: str, ttl_seconds: int) -> None:
        key = self._BLACKLIST_KEY.format(jti=jti)
        await self._redis.setex(key, ttl_seconds, "1")

    async def is_token_blacklisted(self, jti: str) -> bool:
        key = self._BLACKLIST_KEY.format(jti=jti)
        return await self._redis.exists(key) > 0

    async def set_token_version(self, user_id: str, version: int) -> None:
        key = self._TOKEN_VER_KEY.format(user_id=user_id)
        ttl = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 86400
        await self._redis.setex(key, ttl, version)


def get_auth_repository() -> AuthRepository:
    return AuthRepository(get_redis())


AuthRepositoryDep = Annotated[AuthRepository, Depends(get_auth_repository)]
