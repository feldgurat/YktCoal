import uuid
from datetime import datetime, timezone
from enum import IntEnum

from sqlmodel import Field, SQLModel


class ApplicationStatus(IntEnum):
    PENDING = 1
    APPROVED = 2
    REJECTED = 3


APPLICATION_STATUS_LABELS: dict[ApplicationStatus, str] = {
    ApplicationStatus.PENDING: "На рассмотрении",
    ApplicationStatus.APPROVED: "Одобрена",
    ApplicationStatus.REJECTED: "Отклонена",
}


class Application(SQLModel, table=True):
    __tablename__ = "applications"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(index=True)

    # Данные о транспорте
    vehicle_brand: str = Field(max_length=100)
    vehicle_model: str = Field(max_length=100)
    vehicle_plate: str = Field(max_length=20)
    vehicle_capacity_tons: float = Field(ge=0)

    # Документы
    license_url: str | None = Field(default=None, max_length=512)
    insurance_url: str | None = Field(default=None, max_length=512)

    comment: str = Field(default="", max_length=1000)
    reject_reason: str | None = Field(default=None, max_length=1000)

    status: int = Field(default=int(ApplicationStatus.PENDING))

    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )

    @property
    def application_status(self) -> ApplicationStatus:
        return ApplicationStatus(self.status)
