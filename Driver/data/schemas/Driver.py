from uuid import UUID

from sqlmodel import SQLModel, Field


class DriverRead(SQLModel):
    id: UUID
    user_id: UUID
    vehicle_brand: str
    vehicle_model: str
    vehicle_plate: str
    vehicle_capacity_tons: float
    license_url: str | None
    insurance_url: str | None
    rating: float
    total_reviews: int
    status: int
    status_label: str
    created_at: str
    updated_at: str


class DriverUpdate(SQLModel):
    vehicle_brand: str | None = None
    vehicle_model: str | None = None
    vehicle_plate: str | None = None
    vehicle_capacity_tons: float | None = Field(default=None, ge=0)
    license_url: str | None = None
    insurance_url: str | None = None


class DriverStatusRead(SQLModel):
    """Лёгкая схема для проверки статуса из Order-сервиса."""
    user_id: UUID
    status: int
    status_label: str
