import uuid
from datetime import datetime, timezone
from enum import IntEnum

from sqlmodel import Field, Relationship, SQLModel


class OfferStatus(IntEnum):
    PENDING = 1
    ACCEPTED = 2
    REJECTED = 3
    WITHDRAWN = 4


OFFER_STATUS_LABELS: dict[OfferStatus, str] = {
    OfferStatus.PENDING: "Ожидает",
    OfferStatus.ACCEPTED: "Принят",
    OfferStatus.REJECTED: "Отклонён",
    OfferStatus.WITHDRAWN: "Отозван",
}


class Offer(SQLModel, table=True):
    __tablename__ = "offers"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    order_id: uuid.UUID = Field(foreign_key="orders.id", index=True)
    driver_id: uuid.UUID = Field(index=True)

    price: int = Field(ge=0)
    delivery_date: str | None = Field(default=None)
    comment: str = Field(default="", max_length=1000)

    status: int = Field(default=int(OfferStatus.PENDING))

    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def offer_status(self) -> OfferStatus:
        return OfferStatus(self.status)
