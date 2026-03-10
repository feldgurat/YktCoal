from typing import List
from data.entities.Person import Person
from data.entities.User import User
from data.repositories.PersonRepo import PersonRepository
from data.repositories.UserRepo import UserRepository
from data.schemas.User import UserCreateForExistingPerson, UserRead
from sqlmodel.ext.asyncio.session import AsyncSession



async def add_new_user(user: UserCreateForExistingPerson, session: AsyncSession) -> UserRead:
    personRepo = PersonRepository()
    existingPerson = await personRepo.get_entity(user.id, session)
    if existingPerson is None:
        raise Exception("Person с таким id не существует")
    
    userRepo = UserRepository()
    existingUser = await userRepo.get_entity(user.id, session)
    if existingUser is not None:
        raise Exception("User с таким id уже существует")



    entity = User(**user.model_dump())

    try:
        entity = await userRepo.save_entity(entity, session)
    except Exception as e:
        raise e

    return entity

async def get_all_users(session: AsyncSession) -> List[UserRead]:
    userRepo = UserRepository()
    try:
        return await userRepo.get_entities(session)
    except Exception as e:
        raise e