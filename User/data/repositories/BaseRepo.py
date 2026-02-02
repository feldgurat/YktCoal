from typing import Any, Generic, List, Optional, Protocol, Type, TypeVar
from uuid import UUID
from sqlmodel import SQLModel, Session, select

from data.repositories.exeptions import UniqueViolationError


T = TypeVar("M", bound=SQLModel)
K = TypeVar("K", bound=UUID)


class BaseRepository(Generic[T]):
    def __init__(self, model: T, session: Session):
        self.model = model
        #self.session = session

    async def save_entity(self, entity: T) -> Optional[T]:
        existTUI = await self.session.execute(
            select(self.model).where(self.model.telegramUserId == entity.telegramUserId)
        )
        if existTUI.scalar_one_or_none() is not None:
            raise UniqueViolationError("telegramUserId", entity.telegramUserId)

        existEmail = await self.session.execute(
            select(self.model).where(self.model.email == entity.email)
        )
        if existEmail.scalar_one_or_none() is not None:
            raise UniqueViolationError("email", entity.email)
        


        self.session.add(entity)
        self.session.flush()
        return entity

    def update_entity(self, id: K, data: dict[str, Any]) -> Optional[T]:
        entity = self.session.get(self.model, id)
        if entity is None:
            return None
        for key, value in data.items():
            if key == "id":
                continue
            if hasattr(entity, key):
                setattr(entity, key, value)
        self.session.add(entity)
        self.session.flush()
        self.session.refresh(entity)
        return entity

    def delete_entity(self, id: K) -> bool:
        entity = self.session.get(self.model, id)
        if entity is None:
            return False

        self.session.delete(entity)
        self.session.flush()
        return True

    def get_entities(self, limit: int = 100, skip: int = 0, ) -> List[T]:
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.session.exec(stmt).all())

    def get_entity(self, id: K) -> Optional[T]:
        return self.session.get(self.model, id)
