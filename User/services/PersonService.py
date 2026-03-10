from typing import List
from uuid import UUID
from data.entities.Person import Person
from data.repositories.PersonRepo import PersonRepository
from data.schemas.Person import PersonCreate, PersonRead
from data.schemas.User import UserRead
from sqlmodel.ext.asyncio.session import AsyncSession



async def add_new_person(person: PersonCreate, session: AsyncSession) -> UserRead:
    personRepo = PersonRepository()
    existingUser = await personRepo.get_entity_by_number(person.contactNumber, session)
    if existingUser is not None:
        raise Exception("Person с таким номером уже существует")
    
    existingUser = await personRepo.get_entity_by_telegram_user_id(person.telegramUserId, session)
    if existingUser is not None:
        raise Exception("Person с таким telegramUserId уже существует")


    entity = Person(**person.model_dump())

    try:
        entity = await personRepo.save_entity(entity, session)
    except Exception as e:
        raise e

    return entity

async def get_all_persons(session: AsyncSession) -> List[PersonRead]:
    personRepo = PersonRepository()
    try:
        return await personRepo.get_entities(session)
    except Exception as e:
        raise e
    
async def is_user_exist_by_number(phone: str, session: AsyncSession) -> bool:
    personRepo = PersonRepository()
    user = await personRepo.get_entity_by_number(phone, session)
    return user != None

async def get_person_by_number(phone: str, session: AsyncSession) -> Person:
    personRepo = PersonRepository()
    user = await personRepo.get_entity_by_number(phone, session)
    return user

async def get_person_by_id(id: UUID, session: AsyncSession) -> Person:
    personRepo = PersonRepository()
    user = await personRepo.get_entity(id, session)
    return user