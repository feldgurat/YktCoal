from datetime import date
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship
from Base import Base


class Person(Base, table=True):
    __tablename__ = "persons"

    name: str = Field(nullable=False, max_length=255)
    birthDate: Optional[date] = Field(default=None)
    contactNumber: str = Field(nullable=False, max_length=30, index=True)
    email: str = Field(unique=True, nullable=False, max_length=320, index=True)
    telegramUserId: Optional[str] = Field(
        default=None, nullable=True, index=True, unique=True
    )
    password_hash: str = Field(nullable=False)
    isAdmin: bool = Field(nullable=False, default=False)
