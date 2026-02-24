import os
from typing import Annotated, AsyncGenerator
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlmodel import SQLModel


DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///database.db")


def create_engine(url: str = DATABASE_URL) -> AsyncEngine:

    connect_args = {}

    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    return create_async_engine(
        url,
        echo=True,
        connect_args=connect_args,
    )


engine: AsyncEngine = create_engine()


SessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)



async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        await session.close()

SessionDep = Annotated[AsyncSession, Depends(get_session)]

async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
