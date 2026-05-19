from uuid import UUID

from sqlmodel import SQLModel, Field

from data.entities.Offer import OFFER_STATUS_LABELS, OfferStatus


class OfferCreate(SQLModel):
    price: int = Field(ge=0)
    delivery_date: str | None = None
    comment: str = Field(default="", max_length=1000)


class OfferRead(SQLModel):
    id: UUID
    order_id: UUID
    driver_id: UUID
    price: int
    delivery_date: str | None
    comment: str
    status: int
    status_label: str
    created_at: str
    updated_at: str
