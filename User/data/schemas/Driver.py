from typing import Optional
from uuid import UUID
from pydantic_extra_types.phone_numbers import PhoneNumber
from pydantic import BaseModel, ConfigDict, Field

from Person import PersonCreate, PersonRead, PersonUpdate

class DriverCreate(PersonCreate):
    model_config = ConfigDict(extra="forbid")
    licenseNumber: str = Field(min_length=1, max_length=64)

class DriverCreateForExistingPersonId(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: UUID
    licenseNumber: str = Field(min_length=1, max_length=64)

class DriverCreateForExistingPersonContactNumber(BaseModel):
    model_config = ConfigDict(extra="forbid")
    contactNumber: PhoneNumber = Field(min_length=1, max_length=30)
    licenseNumber: str = Field(min_length=1, max_length=64)

class DriverUpdate(PersonUpdate):
    model_config = ConfigDict(extra="forbid")
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    licenseNumber: Optional[str] = Field(default=None, min_length=1, max_length=64)


class DriverRead(PersonRead):
    model_config = ConfigDict(extra="forbid")
    model_config = ConfigDict(from_attributes=True)
    licenseNumber: str

