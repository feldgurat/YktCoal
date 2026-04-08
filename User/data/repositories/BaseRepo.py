from datetime import datetime, timezone
from typing import Generic, Sequence, TypeVar
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel, select

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    def __init__(self, session: AsyncSession, model: type[T]) -> None:
        self._session = session
        self._model = model

    async def get_by_id(self, entity_id: str) -> T | None:
        return await self._session.get(self._model, entity_id)


    async def get_all(self) -> Sequence[T]:
        result = await self._session.exec(
            select(self._model)
        )
        return result.all()



    async def create(self, entity: T) -> T:
        self._session.add(entity)
        await self._session.flush()
        return entity


    async def update(self, entity_id: str, data: SQLModel) -> T | None:
        ent = await self.get_by_id(entity_id)
        if ent is None:
            return None
        ent.updated_at = datetime.now(timezone.utc).isoformat()
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(ent, field, value)
        await self._session.flush()
        return ent


    async def delete(self, entity_id: str) -> bool:
        ent = await self.get_by_id(entity_id)
        if ent is None:
            return False
        await self._session.delete(ent)
        await self._session.flush()
        return True