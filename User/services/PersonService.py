from typing import List
from data.entities.Person import Person
from data.repositories import PersonRepo
from data.schemas.Person import PersonCreate, PersonRead
from data.schemas.User import UserRead
from sqlmodel.ext.asyncio.session import AsyncSession



async def add_new_person(person: PersonCreate, session: AsyncSession) -> UserRead:
    personRepo: PersonRepo = PersonRepo.PersonRepository()
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
    personRepo: PersonRepo = PersonRepo.PersonRepository()
    try:
        return await personRepo.get_entities(session)
    except Exception as e:
        raise e