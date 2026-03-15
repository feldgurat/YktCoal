from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel





class Person(SQLModel, table=True):
    __tablename__ = "persons"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(nullable=False, max_length=255)
    contact_number: str = Field(nullable=False, max_length=30, index=True)
    telegram_user_id: Optional[str] = Field(
        default=None, nullable=True, index=True, unique=True
    )
    token_version: int = Field(default=0, nullable=False)
    
    user: Optional["User"] = Relationship( # type: ignore
        back_populates="person",
        sa_relationship_kwargs={"uselist": False},
    )
    driver: Optional["Driver"] = Relationship( # type: ignore
        back_populates="person",
        sa_relationship_kwargs={"uselist": False},
    )
    admin: Optional["Admin"] = Relationship( # type: ignore
        back_populates="person",
        sa_relationship_kwargs={"uselist": False},
    )
