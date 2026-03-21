from typing import TypeVar
from uuid import UUID

from sqlmodel import SQLModel, select
from sqlalchemy.orm import selectinload

from data.entities.Person import Person
from data.repositories.BaseRepo import BaseRepository

ModelT = TypeVar("ModelT", bound=SQLModel)

class RoleBaseRepository(BaseRepository[ModelT]):
    model: type[ModelT]

    async def get_with_person(self, person_id: UUID) -> ModelT | None:
        stmt = (
            select(self.model)
            .where(self.model.person_id == person_id)
            .options(selectinload(self.model.person))
        )
        result = await self.session.exec(stmt)
        return result.first()
    
    async def exists_for_person(self, person_id: UUID) -> bool:
        p = await self.get_with_person(person_id)
        return p is not None
    
    async def list_with_person(self) -> list[ModelT]:
        stmt = select(self.model).options(selectinload(self.model.person))
        result = await self.session.exec(stmt)
        return list(result.all())
    
    async def get_by_contact_number(self, contact_number: str) -> ModelT | None:
        stmt = (
            select(self.model)
            .join(Person, Person.id == self.model.person_id)
            .where(Person.contact_number == contact_number)
            .options(selectinload(self.model.person))
        )
        result = await self.session.exec(stmt)
        return result.first()
    
    async def get_by_telegram_user_id(self, telegram_user_id: str) -> ModelT | None:
        stmt = (
            select(self.model)
            .join(Person, Person.id == self.model.person_id)
            .where(self.model.telegram_user_id == telegram_user_id)
            .options(selectinload(self.model.person))
        )
        result = await self.session.exec(stmt)
        return result.first()