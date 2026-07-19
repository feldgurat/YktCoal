import redis.asyncio as redis

_redis_client: redis.Redis | None = None


async def init_redis(url: str) -> None:
    global _redis_client
    _redis_client = redis.from_url(url, decode_responses=True)
    await _redis_client.ping()


async def close_redis() -> None:
    global _redis_client
    if _redis_client is not None:
        await _redis_client.aclose()
        _redis_client = None


def get_redis() -> redis.Redis:
    if _redis_client is None:
        raise RuntimeError("Redis not initialized")
    return _redis_client
