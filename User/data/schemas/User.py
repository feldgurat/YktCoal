from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from .Person import PersonCreate, PersonRead

class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    person: PersonCreate
    address: Optional[str] = Field(default=None, max_length=255)

class UserCreateForExistingPerson(BaseModel):
    model_config = ConfigDict(extra="forbid")
    personId: UUID
    address: Optional[str] = Field(default=None, max_length=255)

class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    address: Optional[str] = Field(default=None, max_length=255)

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    personId: UUID
    address: Optional[str] = None
    person: PersonRead
