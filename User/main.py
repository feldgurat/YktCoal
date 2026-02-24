from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
from data.Database import init_db
from api.User import router as user_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(user_router)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)