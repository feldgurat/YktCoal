import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel


class VehicleCreate(SQLModel):
    brand: str = Field(min_length=1, max_length=128)
    model: str = Field(min_length=1, max_length=128)
    reg_number: str = Field(min_length=1, max_length=32)
    registration_docs: str = Field(min_length=1, max_length=512)
    insurance: str = Field(min_length=1, max_length=512)
    capacity: int = Field(ge=1)


class VehicleUpdate(SQLModel):
    brand: str | None = None
    model: str | None = None
    reg_number: str | None = None
    registration_docs: str | None = None
    insurance: str | None = None
    capacity: int | None = Field(default=None, ge=1)


class VehicleRead(SQLModel):
    id: uuid.UUID
    driver_id: uuid.UUID
    brand: str
    model: str
    reg_number: str
    registration_docs: str
    insurance: str
    capacity: int
    created_at: datetime
    updated_at: datetime


# Telegram-вариант: ID водителя резолвит бот.
class TgVehicleCreate(VehicleCreate):
    user_id: uuid.UUID
