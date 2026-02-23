from typing import Optional
from uuid import UUID
from sqlmodel import Relationship, SQLModel, Field

from data.entities.Person import Person


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(primary_key=True, foreign_key="persons.id")
    address: Optional[str] = Field(default=None, max_length=512)

    person: Person = Relationship(back_populates="user")