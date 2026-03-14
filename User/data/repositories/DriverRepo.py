from uuid import UUID

from sqlmodel import select
from sqlalchemy.orm import selectinload

from data.entities.Driver import Driver
from data.repositories.BaseRepo import BaseRepository


class DriverRepository(BaseRepository[Driver]):
    model = Driver

    async def get_with_person(self, person_id: UUID) -> Driver | None:
        stmt = (
            select(Driver)
            .where(Driver.person_id == person_id)
            .options(selectinload(Driver.person))
        )
        result = await self.session.exec(stmt)
        return result.first()

    async def get_by_license_number(self, license_number: str) -> Driver | None:
        stmt = (
            select(Driver)
            .where(Driver.license_number == license_number)
            .options(selectinload(Driver.person))
        )
        result = await self.session.exec(stmt)
        return result.first()

    async def exists_for_person(self, person_id: UUID) -> bool:
        p = await self.get_by_person_id(person_id)
        return p is not None