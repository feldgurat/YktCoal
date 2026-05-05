from uuid import UUID

from sqlmodel import SQLModel, Field


class ApplicationCreate(SQLModel):
    vehicle_brand: str = Field(min_length=1, max_length=100)
    vehicle_model: str = Field(min_length=1, max_length=100)
    vehicle_plate: str = Field(min_length=1, max_length=20)
    vehicle_capacity_tons: float = Field(ge=0)
    license_url: str | None = None
    insurance_url: str | None = None
    comment: str = Field(default="", max_length=1000)


class ApplicationRead(SQLModel):
    id: UUID
    user_id: UUID
    vehicle_brand: str
    vehicle_model: str
    vehicle_plate: str
    vehicle_capacity_tons: float
    license_url: str | None
    insurance_url: str | None
    comment: str
    reject_reason: str | None
    status: int
    status_label: str
    created_at: str
    updated_at: str


class ApplicationReject(SQLModel):
    reason: str = Field(min_length=1, max_length=1000)
