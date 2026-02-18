from data.entities.Person import Person
from data.repositories import PersonRepo
from data.schemas.Person import PersonCreate
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.exc import IntegrityError

class EmailAlreadyExistsError(Exception):
    pass


async def add_new_person(
    person: PersonCreate,
    session: AsyncSession,
    repo: PersonRepo,
) -> Person:
    existing = await repo.get_entity_by_mail(person.email, session)
    if existing is not None:
        raise EmailAlreadyExistsError("Email already exists")

    entity = Person(**person.model_dump())

    session.add(entity)
    try:
        await session.flush()
        await session.refresh(entity)
    except IntegrityError as e:
        await session.rollback()
        raise EmailAlreadyExistsError("Email already exists") from e

    return entity