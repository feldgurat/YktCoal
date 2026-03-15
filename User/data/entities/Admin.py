from typing import Optional
from uuid import UUID
from sqlmodel import Field, Relationship, SQLModel

from data.entities.Person import Person
from data.entities.PersonProxyMixin import PersonProxyMixin

class Admin(PersonProxyMixin, SQLModel, table=True):
    __tablename__ = "admins"

    person_id: UUID = Field(
        foreign_key="persons.id",
        primary_key=True,
    )

    person: Optional["Person"] = Relationship(back_populates="admin")