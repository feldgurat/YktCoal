

from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from Person import PersonCreate, PersonRead

class DriverCreate(BaseModel):
    person: PersonCreate
    licenseNumber: str = Field(min_length=1, max_length=64)


class DriverCreateForExistingPerson(BaseModel):
    personId: int
    licenseNumber: str = Field(min_length=1, max_length=64)


class DriverUpdate(BaseModel):
    licenseNumber: Optional[str] = Field(default=None, min_length=1, max_length=64)


class DriverRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    licenseNumber: str

    person: PersonRead

