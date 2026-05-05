import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from data.Database import async_session_factory, create_tables, engine
from data.Redis import close_redis, init_redis
from services.Startup import seed_default_resources

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
        await seed_default_resources(session)

    logger.info("Startup complete")
    yield

    await close_redis()
    await engine.dispose()
    logger.info("Shutdown complete")


app = FastAPI(title="Order API", version="2.0.0", lifespan=lifespan)

from api.v1.Order import router as order_router
from api.v1.Resource import router as resource_router
from api.v1.Offer import router as offer_router

app.include_router(order_router)
app.include_router(resource_router)
app.include_router(offer_router)

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
