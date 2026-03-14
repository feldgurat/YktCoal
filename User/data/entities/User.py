from typing import Optional
from uuid import UUID
from sqlmodel import Field, Relationship

from data.entities.Base import Base
from data.entities.Person import Person
from data.entities.PersonProxyMixin import PersonProxyMixin

class User(PersonProxyMixin, Base, table=True):
    __tablename__ = "users"

    person_id: UUID = Field(
        foreign_key="persons.id",
        primary_key=True,
    )
    address: Optional[str] = Field(default=None, max_length=512)

    person: Optional["Person"] = Relationship(back_populates="user")