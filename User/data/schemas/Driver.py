from uuid import UUID
from pydantic import BaseModel

from data.schemas.Person import ORMReadModel, PersonCreate, PersonRead, PersonUpdate


class DriverBase(BaseModel):
    license_number: str


# POST /persons/{person_id}/driver
class DriverCreate(DriverBase):
    pass


# POST /drivers
class DriverCreateWithPerson(DriverBase):
    person: PersonCreate


class DriverUpdate(BaseModel):
    license_number: str | None = None
    person: PersonUpdate | None = None


class DriverRead(ORMReadModel):
    person_id: UUID
    license_number: str
    person: PersonRead