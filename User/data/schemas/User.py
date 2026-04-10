from datetime import datetime

from sqlmodel import UUID, SQLModel, Field


class UserCreate(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    contact_number: str = Field(min_length=10, max_length=20)
    telegram_user_id: str | None = None
    address: str | None = None
    roles: list[str] = Field(default_factory=lambda: ["user"])


class UserUpdate(SQLModel):
    name: str | None = None
    contact_number: str | None = None
    telegram_user_id: str | None = None
    address: str | None = None


class UserRoleUpdate(SQLModel):
    role: str


class UserRead(SQLModel):
    id: UUID
    name: str
    contact_number: str
    telegram_user_id: str | None
    address: str | None
    roles: list[str]
    is_active: bool
    created_at: str
    updated_at: str
