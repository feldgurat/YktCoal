from typing import Optional
from uuid import UUID

from sqlmodel import Field, Relationship, SQLModel
from data.entities.Person import Person
from data.entities.PersonProxyMixin import PersonProxyMixin



class Driver(PersonProxyMixin, SQLModel, table=True):
    __tablename__ = "drivers"

    person_id: UUID = Field(
        foreign_key="persons.id",
        primary_key=True,
        ondelete="CASCADE",
    )
    license_number: str = Field(nullable=False, index=True, unique=True, max_length=64)

    person: Optional["Person"] = Relationship(back_populates="driver")
