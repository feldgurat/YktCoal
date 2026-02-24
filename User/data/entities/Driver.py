from uuid import UUID

from sqlmodel import Field

from data.entities.Base import Base



class Driver(Base, table=True):
    __tablename__ = "drivers"

    id: UUID = Field(primary_key=True, foreign_key="persons.id")
    licenseNumber: str = Field(nullable=False, index=True, unique=True, max_length=64)
