from __future__ import annotations


from uuid import UUID

from sqlmodel import Relationship, SQLModel, Field

from data.entities.Person import Person


class Driver(SQLModel, table=True):
    __tablename__ = "drivers"

    id: UUID = Field(primary_key=True, foreign_key="persons.id")
    licenseNumber: str = Field(nullable=False, index=True, unique=True, max_length=64)

    person: Person = Relationship(back_populates="driver")