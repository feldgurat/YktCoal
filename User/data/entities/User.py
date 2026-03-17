from typing import Optional
from uuid import UUID
from sqlmodel import Field, Relationship, SQLModel

from data.entities.Person import Person
from data.entities.PersonProxyMixin import PersonProxyMixin

class User(PersonProxyMixin, SQLModel, table=True):
    __tablename__ = "users"

    person_id: UUID = Field(
        foreign_key="persons.id",
        primary_key=True,
        ondelete="CASCADE",
    )
    address: Optional[str] = Field(default=None, max_length=512)

    person: Optional["Person"] = Relationship(back_populates="user")