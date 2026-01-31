from datetime import date
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import SQLModel, Field, Relationship


class Person(SQLModel, table=True):
    __tablename__ = "persons"
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str = Field(nullable=False, max_length=255)
    birthDate: Optional[date] = Field(default=None)
    contactNumber: str = Field(nullable=False, max_length=30, index=True)
    email: str = Field(unique=True, nullable=False, max_length=320, index=True)
    telegramUserId: Optional[str] = Field(
        default=None, nullable=True, index=True, unique=True
    )
    password_hash: str = Field(nullable=False)
    isAdmin: bool = Field(nullable=False, default=False)
