from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from data.Database import init_db, get_session

# Важно: импортируем entities, чтобы они попали в SQLModel.metadata
from data.entities.Person import Person  # noqa: F401
from data.entities.User import User      # noqa: F401
from data.entities.Driver import Driver  # noqa: F401


app = FastAPI()


@app.on_event("startup")
async def on_startup() -> None:
    await init_db()


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/health/db")
async def health_db(session: AsyncSession = Depends(get_session)):
    # Проверяем, что сессия реально работает и запросы ходят в БД
    await session.execute(text("SELECT 1"))
    return {"db": "ok"}
