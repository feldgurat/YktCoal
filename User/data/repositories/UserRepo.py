from typing import List
from uuid import UUID

from sqlmodel import select
from sqlalchemy.orm import selectinload

from data.entities.Person import Person
from data.entities.User import User
from data.repositories.BaseRepo import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    async def get_with_person(self, person_id: UUID) -> User | None:
        stmt = (
            select(User)
            .where(User.person_id == person_id)
            .options(selectinload(User.person))
        )
        result = await self.session.exec(stmt)
        return result.first()

    async def exists_for_person(self, person_id: UUID) -> bool:
        p = await self.get_with_person(person_id)
        return p is not None
    
    async def list_with_person(self) -> list[User]:
        stmt = select(User).options(selectinload(User.person))
        result = await self.session.exec(stmt)
        return list(result.all())
    
    async def get_by_contact_number(self, contact_number: str) -> User | None:
        stmt = (
            select(User)
            .where(Person.contact_number == contact_number)
            .options(selectinload(User.person))
        )
        result = await self.session.exec(stmt)
        return result.first()
    
    async def get_by_telegram_user_id(self, telegram_user_id: str) -> User | None:
        stmt = (
            select(User)
            .where(User.telegram_user_id == telegram_user_id)
            .options(selectinload(User.person))
        )
        result = await self.session.exec(stmt)
        return result.first()