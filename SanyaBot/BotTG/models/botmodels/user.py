from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class User:
    telegram_id: int
    phone_number: str
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_registered: bool = False
    created_at: datetime = None
    updated_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()