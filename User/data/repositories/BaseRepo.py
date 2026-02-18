from typing import Any, Generic, Optional, TypeVar
from uuid import UUID

from pydantic import EmailStr
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession

T = TypeVar("T", bound=SQLModel)


class BaseRepository(Generic[T]):
    def __init__(self, model: type[T]):
        self.model = model

    async def save_entity(self, entity: T, session: AsyncSession) -> T:
        session.add(entity)
        await session.flush()
        await session.refresh(entity)
        return entity

    async def update_entity(
        self,
        id: UUID,
        data: dict[str, Any],
        session: AsyncSession,
    ) -> Optional[T]:
        entity = await session.get(self.model, id)
        if entity is None:
            return None

        for key, value in data.items():
            if hasattr(entity, key):
                setattr(entity, key, value)

        session.add(entity)
        await session.flush()
        await session.refresh(entity)
        return entity

    async def delete_entity(self, id: UUID, session: AsyncSession) -> bool:
        entity = await session.get(self.model, id)
        if entity is None:
            return False

        await session.delete(entity)
        await session.flush()
        return True

    async def get_entities(
        self,
        session: AsyncSession,
        limit: int = 100,
        skip: int = 0,
    ) -> list[T]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await session.exec(stmt)
        return list(result.all())

    async def get_entity(self, id: UUID, session: AsyncSession) -> Optional[T]:
        return await session.get(self.model, id)

    async def get_entity_by_mail(
        self,
        mail: EmailStr,
        session: AsyncSession,
    ) -> Optional[T]:
        stmt = select(self.model).where(self.model.email == str(mail))
        result = await session.exec(stmt)
        return result.first()
