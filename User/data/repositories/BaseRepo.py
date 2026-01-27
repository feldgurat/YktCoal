from typing import Any, Generic, List, Optional, Protocol, Type, TypeVar
from uuid import UUID
from sqlmodel import SQLModel, Session, select


M = TypeVar("M", bound=SQLModel)
K = TypeVar("K", bound=UUID)


class BaseRepository(Generic[M, K]):
    def __init__(self, model: Type[M], session: Session):
        self.model = model
        self.session = session

    def save_entity(self, entity: M) -> Optional[M]:
        self.session.add(entity)
        self.session.flush()
        return entity

    def update_entity(self, id: K, data: dict[str, Any]) -> Optional[M]:
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

    def get_entities(self, limit: int = 100, skip: int = 0, ) -> List[M]:
        stmt = select(self.model).offset(skip).limit(limit)
        return list(self.session.exec(stmt).all())

    def get_entity(self, id: K) -> Optional[M]:
        return self.session.get(self.model, id)
