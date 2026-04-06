from typing import Annotated, Sequence

from fastapi import Depends
from sqlmodel import SQLModel, select

from data.Database import SessionDep
from data.entities.Role import role_name_to_bit
from data.entities.User import User
from data.repositories.BaseRepo import BaseRepository


class UserRepository(BaseRepository[User]):
    async def get_by_contact_number(self, phone: str) -> User | None:
        result = await self._session.execute(
            select(User).where(User.contact_number == phone)
        )
        return result.scalar_one_or_none()

    async def get_by_role(self, role_name: str) -> Sequence[User]:
        bit = role_name_to_bit(role_name)
        result = await self._session.execute(
            select(User).where(User.roles.op("&")(bit) != 0)
        )
        return result.scalars().all()



def get_user_repository(session: SessionDep) -> UserRepository:
    return UserRepository(session)


UserRepositoryDep = Annotated[UserRepository, Depends(get_user_repository)]
