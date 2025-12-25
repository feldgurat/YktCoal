from datetime import date
from typing import Optional

from sqlmodel import SQLModel, Field, Relationship


class Person(SQLModel, table=True):
    __tablename__ = "persons"

    id: Optional[int] = Field(default=None, primary_key=True)

    name: str = Field(nullable=False, max_length=255)

    birthDate: Optional[date] = Field(default=None)

    contactNumber: str = Field(nullable=False, max_length=30, index=True)

    email: str = Field(index=True, unique=True, nullable=False, max_length=320)

    telegramUserName: Optional[str] = Field(
        default=None, nullable=True, index=True, unique=True, max_length=255
    )

    telegramUserId: Optional[str] = Field(
        default=None, nullable=True, index=True, unique=True
    )

    hashedPassword: str = Field(nullable=False)

    isAdmin: bool = Field(nullable=False, default=False)

    user: Optional["User"] = Relationship(back_populates="person")

    driver: Optional["Driver"] = Relationship(back_populates="person")
