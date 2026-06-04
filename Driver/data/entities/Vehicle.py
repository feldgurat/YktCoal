import uuid
from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


class Vehicle(SQLModel, table=True):
    __tablename__ = "vehicles"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    driver_id: uuid.UUID = Field(foreign_key="drivers.id", index=True)

    brand: str = Field(max_length=128)
    model: str = Field(max_length=128)
    reg_number: str = Field(max_length=32, index=True)
    registration_docs: str = Field(max_length=512)
    insurance: str = Field(max_length=512)
    capacity: int = Field(ge=1)  # тонны или килограммы — на усмотрение фронта

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),  # ← изменить
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_type=DateTime(timezone=True),  # ← изменить
    )
