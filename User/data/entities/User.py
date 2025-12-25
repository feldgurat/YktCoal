

from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship


class User(SQLModel, table=True):
    __tablename__ = "users"


    id: int = Field(primary_key=True, foreign_key="persons.id")


    address: Optional[str] = Field(default=None, max_length=512)


    person: "Person" = Relationship(back_populates="user")
