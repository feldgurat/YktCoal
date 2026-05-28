import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel


from enum import StrEnum


class OrderStatus(StrEnum):
    NEW = "new"
    ACCEPTED = "accepted"
    IN_PROCESS = "in_process"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Order(SQLModel, table=True):
    __tablename__ = "orders"
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(index=True)
    accepted_driver_id: uuid.UUID | None = Field(default=None, index=True)
    resource_id: uuid.UUID = Field(foreign_key="resources.id", index=True)
    dest_address: str = Field(max_length=512)
    volume: Decimal = Field(max_digits=12, decimal_places=2, gt=0)
    cost: Decimal = Field(max_digits=12, decimal_places=2, ge=0)
    final_price: Decimal | None = Field(default=None, max_digits=12, decimal_places=2)
    requested_delivery_date: datetime
    order_date: datetime = Field(default_factory=lambda: datetime.now(UTC))
    status: OrderStatus = Field(default=OrderStatus.NEW, index=True)
    comment: str | None = Field(default=None, max_length=1024)

    latitude: Decimal | None = Field(default=None, max_digits=9, decimal_places=6)
    longitude: Decimal | None = Field(default=None, max_digits=9, decimal_places=6)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
