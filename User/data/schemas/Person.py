from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ORMReadModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class PersonBase(BaseModel):
    name: str
    contact_number: str
    telegram_user_id: str | None = None


class PersonCreate(PersonBase):
    pass

class PersonUpdate(BaseModel):
    name: str | None = None
    contact_number: str | None = None
    telegram_user_id: str | None = None
    token_version: int | None = None


class PersonRead(ORMReadModel):
    id: UUID
    name: str
    contact_number: str
    telegram_user_id: str | None = None
    token_version: int