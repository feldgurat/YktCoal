

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from Person import PersonRead



class DriverCreateForExistingPerson(BaseModel):
    model_config = ConfigDict(extra="forbid")
    personId: UUID
    licenseNumber: str = Field(min_length=1, max_length=64)


class DriverUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    personId: UUID
    licenseNumber: Optional[str] = Field(default=None, min_length=1, max_length=64)


class DriverRead(PersonRead):
    model_config = ConfigDict(extra="forbid")
    model_config = ConfigDict(from_attributes=True)
    licenseNumber: str

