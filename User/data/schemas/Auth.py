from pydantic import field_validator

from User.data.validators import normalize_phone
from sqlmodel import Field, SQLModel


class SmsRequestIn(SQLModel):
    phone: str = Field(min_length=10, max_length=20)

    @field_validator("phone")
    @classmethod
    def _normalize_phone(cls, v: str) -> str:
        return normalize_phone(v)


class SmsVerifyIn(SQLModel):
    phone: str = Field(min_length=10, max_length=20)
    code: str = Field(min_length=4, max_length=6)

    @field_validator("phone")
    @classmethod
    def _normalize_phone(cls, v: str) -> str:
        return normalize_phone(v)


class RegisterIn(SQLModel):
    name: str = Field(min_length=1, max_length=255)
    contact_number: str = Field(min_length=10, max_length=20)
    telegram_user_id: str | None = None
    address: str | None = None

    @field_validator("contact_number")
    @classmethod
    def _normalize_phone(cls, v: str) -> str:
        return normalize_phone(v)


class AccessTokenOut(SQLModel):
    access_token: str


class StatusOut(SQLModel):
    status: str



class RegisterOut(SQLModel):
    success: bool
    message: str
