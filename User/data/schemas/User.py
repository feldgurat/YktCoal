from uuid import UUID

from pydantic import BaseModel

from data.schemas.Person import ORMReadModel, PersonCreate, PersonRead, PersonUpdate

class UserBase(BaseModel):
    address: str | None = None


# POST /persons/{person_id}/user
class UserCreate(UserBase):
    pass


# POST /users
class UserCreateWithPerson(UserBase):
    person: PersonCreate


class UserUpdate(BaseModel):
    address: str | None = None
    person: PersonUpdate | None = None


class UserRead(ORMReadModel):
    person_id: UUID
    address: str | None = None
    person: PersonRead