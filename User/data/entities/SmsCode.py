from datetime import datetime
from sqlmodel import Field, SQLModel


class SmsCode(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    phone: str = Field(index=True)
    code_hash: str
    expires_at: datetime
    attempts: int = 0
    consumed: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)