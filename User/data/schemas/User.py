

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from Person import PersonCreate, PersonRead, PersonUpdate


class UserCreate(BaseModel):
    person: PersonCreate
    address: Optional[str] = Field(default=None, max_length=255)


class UserCreateForExistingPerson(BaseModel):
    personId: int
    address: Optional[str] = Field(default=None, max_length=255)


class UserUpdate(BaseModel):
    address: Optional[str] = Field(default=None, max_length=255)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    address: Optional[str] = None

    person: PersonRead


