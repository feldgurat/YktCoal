from uuid import UUID

from sqlmodel import select
from sqlalchemy.orm import selectinload

from data.entities.Person import Person
from data.repositories.BaseRepo import BaseRepository



class PersonRepository(BaseRepository[Person]):
    model = Person

    async def get_by_telegram_user_id(self, telegram_user_id: str) -> Person | None:
        stmt = select(Person).where(Person.telegram_user_id == telegram_user_id)
        result = await self.session.exec(stmt)
        return result.first()
    
    async def get_by_contact_number(self, contact_number: str) -> Person | None:
        stmt = select(Person).where(Person.contact_number == contact_number)
        result = await self.session.exec(stmt)
        return result.first()

    async def get_with_roles(self, person_id: UUID) -> Person | None:
        stmt = (
            select(Person)
            .where(Person.id == person_id)
            .options(
                selectinload(Person.user),
                selectinload(Person.driver),
                selectinload(Person.admin),
            )
        )
        result = await self.session.exec(stmt)
        return result.first()