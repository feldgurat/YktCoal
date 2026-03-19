from uuid import UUID
from pydantic import BaseModel

from data.schemas.Person import PersonCreate, PersonRead, PersonUpdate


class DriverBase(BaseModel):
    license_number: str


class DriverCreate(DriverBase):
    pass


class DriverCreateWithPerson(DriverBase, PersonCreate):
    pass


class DriverUpdate(PersonUpdate):
    license_number: str | None = None


class DriverRead(PersonRead):
    license_number: str