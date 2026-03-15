from typing import Annotated, List
from uuid import UUID
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from data.Database import SessionDep
from data.entities.Person import Person
from data.entities.User import User
from data.repositories.PersonRepo import PersonRepository
from data.repositories.UserRepo import UserRepository
from data.schemas.User import UserCreate, UserCreateWithPerson, UserUpdate





class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.personsRepo = PersonRepository(session)
        self.usersRepo = UserRepository(session)

    async def create_for_existing_person(
            self,
            person_id: UUID,
            payload: UserCreate
    ) -> User:
        person = await self.personsRepo.get(person_id)
        if person is None:
            raise ValueError("Person с таким id не существует")
        if await self.usersRepo.exists_for_person(person_id):
            raise ValueError("User для этого Person уже существует")
        user = User(
            person=person,
            address=payload.address
        )
        await self.usersRepo.add(user)
        await self.session.flush()
        user = await self.usersRepo.get_with_person(person_id)
        assert user is not None
        return user
    
    async def create_full(
            self,
            payload: UserCreateWithPerson
    ) -> User:
        user = User(
            address=payload.address,
            person=Person(**payload.person.model_dump())
        )

        if await self.personsRepo.get_by_contact_number(user.contact_number) is not None:
            raise ValueError("Person с таким contact_number уже существует")
        
        if user.telegram_user_id is not None and await self.personsRepo.get_by_telegram_user_id(user.telegram_user_id) is not None:
            raise ValueError("Person с таким telegram_user_id уже существует")
        
        if await self.usersRepo.get_by_contact_number(user.contact_number) is not None:
            raise ValueError("User с таким contact_number уже существует")

        await self.usersRepo.add(user)
        await self.session.flush()

        user = await self.usersRepo.get_with_person(user.person_id)
        assert user is not None
        return user
    
    async def get(self, person_id: UUID) -> User | None:
        return await self.usersRepo.get_with_person(person_id)
    
    async def get_list(self) -> List[User]:
        return await self.usersRepo.list_with_person()
    
    async def update(
            self,
            person_id: UUID,
            payload: UserUpdate
    ) -> User | None:
        user = await self.usersRepo.get_with_person(person_id)
        if user is None:
            return None
        data = payload.model_dump(exclude_unset=True)

        if "address" in data:
            user.address = data["address"]

        if "person" in data and data["person"] is not None:
            person_data = data["person"]
            for field, value in person_data.items():
                setattr(user.person, field, value)
        await self.session.flush()
        user = await self.usersRepo.get_with_person(person_id)
        return user
    
    async def delete(self, person_id: UUID) -> bool:
        user = await self.usersRepo.get_with_person(person_id)
        if user is None:
            return False

        await self.users.delete(user)
        await self.session.flush()
        return True


def get_user_service(
    session: SessionDep,
) -> UserService:
    return UserService(session)
    
UserServiceDep = Annotated[UserService, Depends(get_user_service)]