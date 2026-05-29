import uuid
from datetime import datetime

from sqlmodel import SQLModel


class DriverRead(SQLModel):
    id: uuid.UUID
    user_id: uuid.UUID
    application_id: uuid.UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
