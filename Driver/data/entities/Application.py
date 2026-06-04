import uuid
from datetime import UTC, datetime

from sqlalchemy import Column, DateTime
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel

from data.entities.ApplicationStatus import ApplicationStatus


class Application(SQLModel, table=True):
    __tablename__ = "applications"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(index=True)  # ссылка на User-сервис

    status: ApplicationStatus = Field(default=ApplicationStatus.PENDING, index=True)

    license_url: str = Field(max_length=512)
    passport: str = Field(max_length=512)

    vehicles_snapshot: list[dict] = Field(default_factory=list, sa_column=Column(JSONB))

    submission_date: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True)),
    )
    reviewed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    reviewed_by: uuid.UUID | None = Field(default=None)  # user_id админа
    rejection_reason: str | None = Field(default=None, max_length=512)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True)),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True)),
    )