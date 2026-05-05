import redis.asyncio as redis

from config import settings

redis_client: redis.Redis | None = None


async def init_redis() -> None:
    global redis_client
    redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    await redis_client.ping()


async def close_redis() -> None:
    global redis_client
    if redis_client is not None:
        await redis_client.aclose()
        redis_client = None


def get_redis() -> redis.Redis:
    if redis_client is None:
        raise RuntimeError("Redis not initialized")
    return redis_client
