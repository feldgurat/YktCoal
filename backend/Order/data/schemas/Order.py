import uuid
from datetime import datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel

from data.entities.Order import OrderStatus


class OrderCreate(SQLModel):
    resource_id: uuid.UUID
    dest_address: str = Field(min_length=1, max_length=512)
    volume: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    requested_delivery_date: datetime
    comment: str | None = Field(default=None, max_length=1024)
    latitude: Decimal | None = Field(default=None, max_digits=9, decimal_places=6)
    longitude: Decimal | None = Field(default=None, max_digits=9, decimal_places=6)


class OrderUpdate(SQLModel):
    resource_id: uuid.UUID | None = None
    dest_address: str | None = Field(default=None, min_length=1, max_length=512)
    volume: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    requested_delivery_date: datetime | None = None
    comment: str | None = Field(default=None, max_length=1024)
    latitude: Decimal | None = Field(default=None, max_digits=9, decimal_places=6)
    longitude: Decimal | None = Field(default=None, max_digits=9, decimal_places=6)


class OrderRead(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    accepted_driver_id: uuid.UUID | None
    resource_id: uuid.UUID
    dest_address: str
    volume: Decimal
    cost: Decimal
    final_price: Decimal | None
    requested_delivery_date: datetime
    order_date: datetime
    status: OrderStatus
    comment: str | None
    latitude: Decimal | None
    longitude: Decimal | None
    created_at: datetime
    updated_at: datetime


# Telegram-вариант: user_id передаётся ботом.
class TgOrderCreate(OrderCreate):
    user_id: uuid.UUID
