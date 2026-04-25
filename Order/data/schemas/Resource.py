from uuid import UUID

from sqlmodel import SQLModel, Field


class ResourceCreate(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    unit: str = Field(default="тонна", max_length=50)
    price_per_unit: int = Field(ge=0)


class ResourceUpdate(SQLModel):
    name: str | None = None
    unit: str | None = None
    price_per_unit: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class ResourceRead(SQLModel):
    id: UUID
    name: str
    unit: str
    price_per_unit: int
    is_active: bool
