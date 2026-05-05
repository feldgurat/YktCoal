import uuid
from datetime import datetime, timezone
from enum import IntEnum

from sqlmodel import Field, SQLModel


class DriverStatus(IntEnum):
    ACTIVE = 1
    BLOCKED = 2


DRIVER_STATUS_LABELS: dict[DriverStatus, str] = {
    DriverStatus.ACTIVE: "Активен",
    DriverStatus.BLOCKED: "Заблокирован",
}


class Driver(SQLModel, table=True):
    __tablename__ = "drivers"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(unique=True, index=True)

    # Транспорт
    vehicle_brand: str = Field(max_length=100)
    vehicle_model: str = Field(max_length=100)
    vehicle_plate: str = Field(max_length=20)
    vehicle_capacity_tons: float = Field(ge=0)

    # Документы (ссылки на файлы)
    license_url: str | None = Field(default=None, max_length=512)
    insurance_url: str | None = Field(default=None, max_length=512)

    rating: float = Field(default=0.0, ge=0, le=5)
    total_reviews: int = Field(default=0)

    status: int = Field(default=int(DriverStatus.ACTIVE))

    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def driver_status(self) -> DriverStatus:
        return DriverStatus(self.status)
