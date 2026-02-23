from typing import Optional

from sqlmodel import Field, Relationship

from data.entities.Base import Base
from data.entities.Driver import Driver
from data.entities.User import User


class Person(Base, table=True):
    __tablename__ = "persons"
    name: str = Field(nullable=False, max_length=255)
    contactNumber: str = Field(nullable=False, max_length=30, index=True)
    telegramUserId: Optional[str] = Field(
        default=None, nullable=True, index=True, unique=True
    )
    isAdmin: bool = Field(nullable=False, default=False)

    driver: Optional["Driver"] = Relationship(
        back_populates="person",
        sa_relationship_kwargs={"uselist": False},
    )
    user: Optional["User"] = Relationship(
        back_populates="person",
        sa_relationship_kwargs={"uselist": False},
    )