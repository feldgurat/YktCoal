from uuid import UUID
from pydantic import BaseModel

from data.schemas.Person import ORMReadModel, PersonCreate, PersonRead, PersonUpdate


class AdminCreate(BaseModel):
    pass


class AdminCreateWithPerson(PersonCreate):
    pass


class AdminUpdate(PersonUpdate):
    pass


class AdminRead(PersonRead):
    pass