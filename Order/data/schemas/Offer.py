import uuid
from datetime import datetime
from decimal import Decimal

from sqlmodel import Field, SQLModel

from data.entities.Offer import OfferStatus


class OfferCreate(SQLModel):
    order_id: uuid.UUID
    price: Decimal = Field(gt=0, max_digits=12, decimal_places=2)
    comment: str | None = Field(default=None, max_length=512)
    delivery_date: datetime


class OfferRead(SQLModel):
    id: uuid.UUID
    order_id: uuid.UUID
    driver_user_id: uuid.UUID
    price: Decimal
    comment: str | None
    delivery_date: datetime
    status: OfferStatus
    created_at: datetime
    updated_at: datetime


# Telegram: user_id водителя передаётся ботом.
class TgOfferCreate(OfferCreate):
    user_id: uuid.UUID
