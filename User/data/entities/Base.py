from uuid import UUID
from sqlmodel import SQLModel, Field

class Base(SQLModel):
    id: UUID = Field(default_factory=None, primary_key=True)