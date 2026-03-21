import data.entities
from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import select
import uvicorn
from data.Database import close_redis, get_session, init_db, init_redis
from api.v1.User import router as user_router
from api.v1.Person import router as person_router
from api.v1.Admin import router as admin_router
from api.v1.Driver import router as driver_router
from api.v1.Auth import router as auth_router
from api.v1.Telegram import router as telegram_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await init_redis()
    yield
    await close_redis()


app = FastAPI(lifespan=lifespan)
app.include_router(user_router)
app.include_router(admin_router)
app.include_router(driver_router)
app.include_router(person_router)
app.include_router(auth_router)
app.include_router(telegram_router)

live_router = APIRouter()
@live_router.get("/")
def root():
    return "IM LIVE MOTHAFAKA"
app.include_router(live_router)


origins = [
    "http://localhost:5173",  # адрес Vite-сервера
    "http://127.0.0.1:5173",
    # для продакшена добавьте домен вашего сайта
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],      # разрешаем все HTTP-методы
    allow_headers=["*"],      # разрешаем все заголовки
)

if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
    session = get_session()