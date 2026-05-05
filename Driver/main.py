import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from data.Database import create_tables, engine
from data.Redis import close_redis, init_redis

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

from api.v1.Driver import router as driver_router
from api.v1.Application import router as application_router

app.include_router(driver_router)
app.include_router(application_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok"}
