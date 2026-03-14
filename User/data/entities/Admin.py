from typing import Optional
from uuid import UUID
from sqlmodel import Field, Relationship

from data.entities.Base import Base
from data.entities.Person import Person
from data.entities.PersonProxyMixin import PersonProxyMixin

class Admin(PersonProxyMixin, Base, table=True):
    __tablename__ = "admins"

    person_id: UUID = Field(
        foreign_key="persons.id",
        primary_key=True,
    )

    person: Optional["Person"] = Relationship(back_populates="admin")