import uuid
from datetime import UTC, datetime

from sqlmodel import Field, SQLModel


class Driver(SQLModel, table=True):
    __tablename__ = "drivers"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(unique=True, index=True)  # ссылка на User-сервис

    # ID заявки, по которой стал водителем (Approved)
    application_id: uuid.UUID = Field(foreign_key="applications.id")

    is_active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
