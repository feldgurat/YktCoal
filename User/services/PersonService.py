from typing import Annotated
from uuid import UUID
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from data.Database import SessionDep
from data.entities.Person import Person
from data.entities.User import User
from data.repositories.PersonRepo import PersonRepository
from data.repositories.UserRepo import UserRepository
from data.schemas.Person import PersonCreate, PersonUpdate


class PersonService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.personsRepo = PersonRepository(session)
    
    async def create(
            self,
            payload: PersonCreate
    ) -> Person:
        person = Person(
            **payload.person.model_dump()
        )
        await self.personsRepo.add(person)
        await self.session.flush()

        person = await self.personsRepo.get_by_contact_number(person.contact_number)
        assert person is not None
        return person
    
    async def get(self, person_id: UUID) -> User | None:
        return await self.personsRepo.get_with_roles(person_id)
    
    async def get_by_contact_number(self, contact_number: str) -> User | None:
        return await self.personsRepo.get_by_contact_number(contact_number)
    
    async def update(
            self,
            person_id: UUID,
            payload: PersonUpdate
    ) -> User | None:
        person = await self.personsRepo.get(person_id)
        if person is None:
            return None
        data = payload.model_dump(exclude_unset=True)


        for field, value in data.items():
            setattr(person, field, value)

        await self.session.flush()
        person = await self.personsRepo.get_with_roles(person_id)
        return person
    
    async def delete(self, person_id: UUID) -> bool:
        person = await self.personsRepo.get_with_roles(person_id)
        if person is None:
            return False

        await self.personsRepo.delete(person)
        await self.session.flush()
        return True


def get_person_service(
    session: SessionDep,
) -> PersonService:
    return PersonService(session)
    
PersonServiceDep = Annotated[PersonService, Depends(get_person_service)]