import uuid
from datetime import UTC, datetime
from decimal import Decimal

from sqlalchemy import Column, DateTime
from sqlmodel import Field, SQLModel


from enum import StrEnum


class OfferStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

class Offer(SQLModel, table=True):
    __tablename__ = "offers"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    order_id: uuid.UUID = Field(foreign_key="orders.id", index=True)
    driver_user_id: uuid.UUID = Field(index=True)

    price: Decimal = Field(max_digits=12, decimal_places=2, gt=0)
    comment: str | None = Field(default=None, max_length=512)
    delivery_date: datetime = Field(sa_column=Column(DateTime(timezone=True)))

    status: OfferStatus = Field(default=OfferStatus.PENDING, index=True)

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True)),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        sa_column=Column(DateTime(timezone=True)),
    )