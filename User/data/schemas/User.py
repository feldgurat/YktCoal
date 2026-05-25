from uuid import UUID

from pydantic import field_validator

from User.data.validators import normalize_phone
from sqlmodel import Field, SQLModel


class UserCreate(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    contact_number: str = Field(min_length=10, max_length=20)
    telegram_user_id: str | None = None
    address: str | None = None
    roles: list[str] = Field(default_factory=lambda: ["user"])

    @field_validator("contact_number")
    @classmethod
    def _normalize_phone(cls, v: str) -> str:
        return normalize_phone(v)


class UserUpdate(SQLModel):
    name: str | None = None
    contact_number: str | None = None
    telegram_user_id: str | None = None
    address: str | None = None

    @field_validator("contact_number")
    @classmethod
    def _normalize_phone(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return normalize_phone(v)


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
