import uuid
from datetime import datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel


class ResourceCreate(SQLModel):
    name: str = Field(min_length=1, max_length=128)
    price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)
    unit: str = Field(default="т", min_length=1, max_length=16)


class ResourceUpdate(SQLModel):
    name: str | None = Field(default=None, min_length=1, max_length=128)
    price: Decimal | None = Field(default=None, ge=0, max_digits=12, decimal_places=2)
    unit: str | None = Field(default=None, min_length=1, max_length=16)
    is_active: bool | None = None


class ResourceRead(SQLModel):
    id: uuid.UUID
    name: str
    price: Decimal
    unit: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
