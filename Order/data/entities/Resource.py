import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


class Resource(SQLModel, table=True):
    __tablename__ = "resources"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=128, unique=True, index=True)
    price: Decimal = Field(max_digits=12, decimal_places=2, ge=0)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True)),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True)),
    )