from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from data.Database import close_redis, init_db, init_redis
from api.User import router as user_router
from api.Auth import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_redis()
    yield
    await close_redis()


app = FastAPI(lifespan=lifespan)
app.include_router(user_router)
app.include_router(auth_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)