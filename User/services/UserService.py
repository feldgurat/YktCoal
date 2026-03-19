from typing import Annotated, List
from uuid import UUID
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from data.Database import SessionDep
from data.entities.Person import Person
from data.entities.User import User
from data.repositories.PersonRepo import PersonRepository
from data.repositories.UserRepo import UserRepository
from data.schemas.User import UserCreate, UserCreateWithPerson, UserRead, UserUpdate





class UserService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.personsRepo = PersonRepository(session)
        self.usersRepo = UserRepository(session)

    def _to_user_read(self, user: User) -> UserRead:
        return UserRead(
            id=user.person_id,
            name=user.name,
            contact_number=user.contact_number,
            telegram_user_id=user.telegram_user_id,
            address=user.address,
        )

    async def create_for_existing_person(
            self,
            person_id: UUID,
            payload: UserCreate
    ) -> UserRead:
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
        return self._to_user_read(user)
    
    async def create_full(
            self,
            payload: UserCreateWithPerson
    ) -> UserRead:
        user = User(
            address=payload.address,
            person=Person(**payload.model_dump())
        )

        if await self.personsRepo.get_by_contact_number(user.contact_number) is not None:
            raise ValueError("Person с таким contact_number уже существует")
        
        if user.telegram_user_id is not None and await self.personsRepo.get_by_telegram_user_id(user.telegram_user_id) is not None:
            raise ValueError("Person с таким telegram_user_id уже существует")
        
        if await self.usersRepo.get_by_contact_number(user.contact_number) is not None:
            raise ValueError("User с таким contact_number уже существует")

        await self.usersRepo.add(user)
        await self.session.flush()

        assert user is not None
        return self._to_user_read(user)
    
    async def get(self, person_id: UUID) -> UserRead | None:
        user =  await self.usersRepo.get_with_person(person_id)
        return self._to_user_read(user)
    
    async def get_list(self) -> List[UserRead]:
        users = await self.usersRepo.list_with_person()
        resps = [
            self._to_user_read(user)
            for user in users
        ]
        return resps
    
    async def update(
            self,
            person_id: UUID,
            payload: UserUpdate
    ) -> UserRead | None:
        user = await self.usersRepo.get_with_person(person_id)
        if user is None:
            return None
        data = payload.model_dump(exclude_unset=True)

        for field, value in data.items():
            setattr(user, field, value)
        await self.session.flush()
        user = await self.usersRepo.get_with_person(person_id)
        return self._to_user_read(user)
    
    async def delete(self, person_id: UUID) -> bool:
        user = await self.usersRepo.get_with_person(person_id)
        if user is None:
            return False

        await self.usersRepo.delete(user)
        await self.session.flush()
        return True


def get_user_service(
    session: SessionDep,
) -> UserService:
    return UserService(session)
    
UserServiceDep = Annotated[UserService, Depends(get_user_service)]