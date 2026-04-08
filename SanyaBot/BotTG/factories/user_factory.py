from typing import Optional
from models.botmodels.user import User
from datetime import datetime


class UserFactory:
    @staticmethod
    def create_from_telegram(
        telegram_id: int,
        phone_number: str,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> User:
        return User(
            telegram_id=telegram_id,
            phone_number=phone_number,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_registered=True,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )