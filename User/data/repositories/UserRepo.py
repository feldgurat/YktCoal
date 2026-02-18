from typing import Optional
from uuid import UUID

from .BaseRepo import BaseRepository
from data.entities.User import User


class UserRepository(BaseRepository[User]):
    def __init__(self, session):
        super().__init__(User, session)

    def get_user_address(self, id: UUID) -> Optional[str]:
        user = self.session.get(User, id)
        return None if user is None else user.address
