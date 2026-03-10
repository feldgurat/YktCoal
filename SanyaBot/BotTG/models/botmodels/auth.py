from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class AuthSession:
    telegram_id: int
    phone_number: Optional[str] = None
    step: str = "phone"
    created_at: datetime = None
    expires_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()