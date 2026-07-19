import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.middleware.cors import CORSMiddleware

from api.v1.Application import router as applications_router
from api.v1.Debug import router as debug_router
from api.v1.Driver import router as drivers_router
from api.v1.Internal import router as internal_router
from api.v1.Telegram import router as telegram_router
from config import settings
from data.Database import create_tables, engine
from data.entities.Application import Application  # noqa: F401, E402
from data.entities.Driver import Driver  # noqa: F401, E402
from data.entities.Vehicle import Vehicle  # noqa: F401, E402
from data.Redis import close_redis, init_redis
from services.Exceptions import AppException

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up...")

    await create_tables()
    logger.info("Database tables ready")

    await init_redis()
    logger.info("Redis connected")

    logger.info("Startup complete")
    yield

    await close_redis()
    await engine.dispose()
    logger.info("Shutdown complete")


app = FastAPI(title="Driver API", version="1.0.0", lifespan=lifespan)


@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled exception", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Внутренняя ошибка сервера"},
    )


app.include_router(applications_router)
app.include_router(drivers_router)
app.include_router(telegram_router)
if not settings.is_production:
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
