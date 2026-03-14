from uuid import UUID

from sqlmodel import select
from sqlalchemy.orm import selectinload

from data.entities.Admin import Admin
from data.repositories.BaseRepo import BaseRepository


class AdminRepository(BaseRepository[Admin]):
    model = Admin

    async def get_with_person(self, person_id: UUID) -> Admin | None:
        stmt = (
            select(Admin)
            .where(Admin.person_id == person_id)
            .options(selectinload(Admin.person))
        )
        result = await self.session.exec(stmt)
        return result.first()

    async def exists_for_person(self, person_id: UUID) -> bool:
        p = await self.get_by_person_id(person_id)
        return p is not None