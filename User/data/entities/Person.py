from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship

from data.entities.Base import Base
from data.entities.Driver import Driver
from data.entities.User import User


class Person(Base, table=True):
    __tablename__ = "persons"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(nullable=False, max_length=255)
    contactNumber: str = Field(nullable=False, max_length=30, index=True)
    telegramUserId: Optional[str] = Field(
        default=None, nullable=True, index=True, unique=True
    )
    isAdmin: bool = Field(nullable=False, default=False)
    token_version: int = Field(default=0, nullable=False)

    driver: Optional["Driver"] = Relationship(
        sa_relationship_kwargs={"uselist": False,
                                "primaryjoin": "Person.id == Driver.id",},
        
    )
    user: Optional["User"] = Relationship(
        sa_relationship_kwargs={"uselist": False,
                                "primaryjoin": "Person.id == User.id",},
    )