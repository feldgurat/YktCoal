from uuid import UUID

from sqlmodel import SQLModel, Field

from data.entities.Order import STATUS_LABELS, OrderStatus
from data.schemas.Resource import ResourceRead


class OrderCreate(SQLModel):
    dest_address: str = Field(min_length=1, max_length=512)
    latitude: float | None = None
    longitude: float | None = None
    resource_id: UUID
    volume: float = Field(gt=0)
    delivery_date: str | None = None
    comment: str = Field(default="", max_length=1000)


class OrderUpdate(SQLModel):
    dest_address: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    volume: float | None = Field(default=None, gt=0)
    delivery_date: str | None = None
    comment: str | None = None


class OrderStatusUpdate(SQLModel):
    status: int


class OrderAssignDriver(SQLModel):
    driver_id: UUID


class OrderRead(SQLModel):
    id: UUID
    client_id: UUID
    driver_id: UUID | None
    dest_address: str
    latitude: float | None
    longitude: float | None
    resource: ResourceRead | None
    volume: float
    cost: int
    delivery_date: str | None
    comment: str
    status: int
    status_label: str
    created_at: str
    updated_at: str


class MessageResponse(SQLModel):
    success: bool
    message: str
