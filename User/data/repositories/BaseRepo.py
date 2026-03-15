from __future__ import annotations

from abc import ABC
from typing import Generic, TypeVar, Any

from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

ModelT = TypeVar("ModelT", bound=SQLModel)


class BaseRepository(ABC, Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def add(self, obj: ModelT) -> ModelT:
        self.session.add(obj)
        await self.session.flush()
        return obj

    async def get(self, pk: Any) -> ModelT | None:
        return await self.session.get(self.model, pk)

    async def list(self) -> list[ModelT]:
        stmt = select(self.model)
        result = await self.session.exec(stmt)
        return list(result.all())

    async def delete(self, obj: ModelT) -> None:
        await self.session.delete(obj)
        await self.session.flush()