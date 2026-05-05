import uuid

from sqlmodel import Field, SQLModel


class Resource(SQLModel, table=True):
    __tablename__ = "resources"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, index=True)
    unit: str = Field(default="тонна", max_length=50)
    price_per_unit: int = Field(default=0)
    is_active: bool = Field(default=True)
