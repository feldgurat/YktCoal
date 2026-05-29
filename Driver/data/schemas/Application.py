import uuid
from datetime import datetime

from sqlmodel import Field, SQLModel

from data.entities.ApplicationStatus import ApplicationStatus


class VehicleInApplication(SQLModel):
    brand: str = Field(min_length=1, max_length=128)
    model: str = Field(min_length=1, max_length=128)
    reg_number: str = Field(min_length=1, max_length=32)
    registration_docs: str = Field(min_length=1, max_length=512)
    insurance: str = Field(min_length=1, max_length=512)
    capacity: int = Field(ge=1)


class ApplicationCreate(SQLModel):
    license_url: str = Field(min_length=1, max_length=512)
    passport: str = Field(min_length=1, max_length=512)
    # Минимум одна машина по требованию ТЗ.
    vehicles: list[VehicleInApplication] = Field(min_length=1)


class ApplicationReject(SQLModel):
    reason: str = Field(min_length=1, max_length=512)


class ApplicationRead(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    status: ApplicationStatus
    license_url: str
    passport: str
    vehicles_snapshot: list[dict]
    submission_date: datetime
    reviewed_at: datetime | None
    reviewed_by: uuid.UUID | None
    rejection_reason: str | None
    created_at: datetime
    updated_at: datetime


# Telegram-вариант: бот уже передаёт user_id (резолвив tg_id через User-сервис).
class TgApplicationCreate(ApplicationCreate):
    user_id: uuid.UUID
