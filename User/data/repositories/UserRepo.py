from typing import Annotated, Sequence

from fastapi import Depends
from sqlmodel import SQLModel, select

from data.Database import SessionDep
from data.entities.Role import RoleHelpers
from data.entities.User import User
from data.repositories.BaseRepo import BaseRepository


class UserRepository(BaseRepository[User]):
    async def get_by_contact_number(self, phone: str) -> User | None:
        result = await self._session.exec(
            select(User).where(User.contact_number == phone)
        )
        return result.one_or_none()

    async def get_by_telegram_user_id(self, tg_id: str) -> User | None:
        result = await self._session.exec(
            select(User).where(User.telegram_user_id == tg_id)
        )
        return result.one_or_none()

    async def get_by_role(self, role_name: str) -> Sequence[User]:
        bit = RoleHelpers.role_name_to_bit(role_name)
        result = await self._session.exec(
            select(User).where(User.roles.op("&")(bit) != 0)
        )
        return result.all()



def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session, User)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
