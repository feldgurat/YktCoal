from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from .Person import PersonCreate, PersonRead

class UserCreateForExistingPerson(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    address: Optional[str] = Field(default=None, max_length=255)

class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    address: Optional[str] = Field(default=None, max_length=255)

class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    address: Optional[str] = None

class UserReadFull(PersonRead):
    model_config = ConfigDict(extra="forbid")
    address: Optional[str] = None