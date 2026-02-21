from typing import Optional
from uuid import UUID
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    __tablename__ = "users"

    id: UUID = Field(primary_key=True, foreign_key="persons.id")
    address: Optional[str] = Field(default=None, max_length=512)
