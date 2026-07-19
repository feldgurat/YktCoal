from config import settings
from ykt_common.redis import close_redis, get_redis
from ykt_common.redis import init_redis as _init_redis

__all__ = ["close_redis", "get_redis", "init_redis"]


async def init_redis() -> None:
    await _init_redis(settings.REDIS_URL)
