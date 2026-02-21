from typing import List, Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .BaseRepo import BaseRepository
from data.entities.Person import Person


class PersonRepository(BaseRepository[Person]):
    def __init__(self):
        super().__init__(Person)

    def get_admin_status(self, id: UUID, session: AsyncSession) -> Optional[bool]:
        person = session.get(Person, id)
        return None if person is None else person.isAdmin

    def get_admins(self, session: AsyncSession) -> List[Person]:
        stmt = select(Person).where(Person.isAdmin == True)
        return list(session.exec(stmt).all())
