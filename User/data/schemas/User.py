from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from .Person import PersonCreate, PersonRead

class UserCreateForExistingPerson(BaseModel):
    model_config = ConfigDict(extra="forbid")
    personId: UUID
    address: Optional[str] = Field(default=None, max_length=255)

class UserUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    address: Optional[str] = Field(default=None, max_length=255)

class UserRead(PersonRead):
    model_config = ConfigDict(from_attributes=True)
    address: Optional[str] = None
