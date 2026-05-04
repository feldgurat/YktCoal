import uuid
from datetime import datetime, timezone
from enum import IntEnum

from sqlmodel import Field, Relationship, SQLModel

from data.entities.Resource import Resource


class OrderStatus(IntEnum):
    NEW = 1           # клиент создал заявку, водители могут предлагать офферы
    ACCEPTED = 2      # клиент принял оффер, водитель назначен
    IN_PROGRESS = 3   # водитель в пути / доставляет
    COMPLETED = 4     # доставка завершена
    CANCELLED = 5     # клиент отменил
    REJECTED = 6      # админ отклонил


STATUS_LABELS: dict[OrderStatus, str] = {
    OrderStatus.NEW: "Новый",
    OrderStatus.ACCEPTED: "Принят",
    OrderStatus.IN_PROGRESS: "В пути",
    OrderStatus.COMPLETED: "Выполнен",
    OrderStatus.CANCELLED: "Отменён",
    OrderStatus.REJECTED: "Отклонён",
}

ALLOWED_TRANSITIONS: dict[OrderStatus, list[OrderStatus]] = {
    OrderStatus.NEW: [OrderStatus.ACCEPTED, OrderStatus.CANCELLED, OrderStatus.REJECTED],
    OrderStatus.ACCEPTED: [OrderStatus.IN_PROGRESS, OrderStatus.CANCELLED, OrderStatus.REJECTED],
    OrderStatus.IN_PROGRESS: [OrderStatus.COMPLETED, OrderStatus.CANCELLED],
    OrderStatus.COMPLETED: [],
    OrderStatus.CANCELLED: [],
    OrderStatus.REJECTED: [],
}


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    client_id: uuid.UUID = Field(index=True)
    driver_id: uuid.UUID | None = Field(default=None, index=True)

    dest_address: str = Field(max_length=512)
    latitude: float | None = Field(default=None)
    longitude: float | None = Field(default=None)

    resource_id: uuid.UUID = Field(foreign_key="resources.id", index=True)
    resource: Resource | None = Relationship()

    volume: float = Field(default=1.0)

    # cost = 0 при создании; заполняется ценой из принятого оффера
    cost: int = Field(default=0)

    delivery_date: str | None = Field(default=None)
    comment: str = Field(default="", max_length=1000)

    status: int = Field(default=int(OrderStatus.NEW))

    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def order_status(self) -> OrderStatus:
        return OrderStatus(self.status)

    def can_transition_to(self, new_status: OrderStatus) -> bool:
        return new_status in ALLOWED_TRANSITIONS.get(self.order_status, [])
