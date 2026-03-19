from uuid import UUID

from pydantic import BaseModel

from data.schemas.Person import PersonCreate, PersonRead, PersonUpdate

class UserBase(BaseModel):
    address: str | None = None


class UserCreate(UserBase):
    pass


class UserCreateWithPerson(UserBase, PersonCreate):
    pass


class UserUpdate(PersonUpdate):
    address: str | None = None


class UserRead(PersonRead):
    address: str | None = None