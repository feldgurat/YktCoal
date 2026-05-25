import logging
from contextlib import asynccontextmanager

from api.v1.Auth import router as auth_router
from api.v1.Debug import router as debug_router
from api.v1.Internal import router as internal_router
from api.v1.Telegram import router as telegram_router
from api.v1.User import router as users_router
from config import settings
from data.Database import async_session_factory, create_tables, engine
from data.Redis import close_redis, init_redis
from fastapi import FastAPI
from services.Startup import create_default_admin
from starlette.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")

    await create_tables()
    logger.info("Database tables ready")

    await init_redis()
    logger.info("Redis connected")

    async with async_session_factory() as session:
        await create_default_admin(session)

    logger.info("Startup complete")
    yield

    await close_redis()
    await engine.dispose()
    logger.info("Shutdown complete")


app = FastAPI(title="App API", version="1.0.0", lifespan=lifespan)


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(telegram_router)
app.include_router(debug_router)
app.include_router(internal_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}
