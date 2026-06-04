import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class ApplicationStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Application(SQLModel, table=True):
    __tablename__ = "applications"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(index=True)  # ссылка на User-сервис

    status: ApplicationStatus = Field(default=ApplicationStatus.PENDING, index=True)

    license_url: str = Field(max_length=512)
    passport: str = Field(max_length=512)

    # Снепшот машин на момент подачи заявки. Это не таблица Vehicle —
    # настоящие Vehicle создаются только при approve, из этого снепшота.
    # Формат: [{"brand": "...", "model": "...", "reg_number": "...",
    #          "registration_docs": "...", "insurance": "...", "capacity": N}, ...]
    vehicles_snapshot: list[dict] = Field(default_factory=list, sa_column=Column(JSONB))

    submission_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    reviewed_at: datetime | None = Field(default=None)
    reviewed_by: uuid.UUID | None = Field(default=None)  # user_id админа
    rejection_reason: str | None = Field(default=None, max_length=512)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),  # ← изменить
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),  # ← изменить
    )
