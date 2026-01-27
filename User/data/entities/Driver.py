from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from sqlmodel import SQLModel, Field, Relationship
from Person import Person


class Driver(Person, table=True):
    __tablename__ = "drivers"

    id: UUID = Field(primary_key=True, foreign_key="persons.id")
    licenseNumber: str = Field(nullable=False, index=True, unique=True, max_length=64)
