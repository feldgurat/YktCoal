from typing import List, Optional
from uuid import UUID

from sqlmodel import select

from .BaseRepo import BaseRepository
from data.entities.Person import Person


class PersonRepository(BaseRepository[Person]):
    def __init__(self, session):
        super().__init__(Person, session)

    def get_admin_status(self, id: UUID) -> Optional[bool]:
        person = self.session.get(Person, id)
        return None if person is None else person.isAdmin

    def get_admins(self) -> List[Person]:
        stmt = select(Person).where(Person.isAdmin == True)
        return list(self.session.exec(stmt).all())
