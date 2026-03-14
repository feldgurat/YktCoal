from uuid import UUID
from pydantic import BaseModel

from data.schemas.Person import ORMReadModel, PersonCreate, PersonRead, PersonUpdate


class AdminCreate(BaseModel):
    pass


class AdminCreateWithPerson(BaseModel):
    person: PersonCreate


class AdminUpdate(BaseModel):
    person: PersonUpdate | None = None


class AdminRead(ORMReadModel):
    person_id: UUID
    person: PersonRead