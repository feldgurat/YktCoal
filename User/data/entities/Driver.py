from __future__ import annotations

from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship


class Driver(SQLModel, table=True):
    __tablename__ = "drivers"

    id: int = Field(primary_key=True, foreign_key="persons.id")

    licenseNumber: str = Field(nullable=False, index=True, unique=True, max_length=64)

    person: "Person" = Relationship(back_populates="driver")
