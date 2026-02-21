from typing import Optional
from uuid import UUID

from .BaseRepo import BaseRepository
from data.entities.User import User
from sqlmodel.ext.asyncio.session import AsyncSession

class UserRepository(BaseRepository[User]):
    def __init__(self):
        super().__init__(User)

    def get_user_address(self, id: UUID, session: AsyncSession) -> Optional[str]:
        user = session.get(User, id)
        return None if user is None else user.address
