from uuid import UUID

from sqlmodel import select
from sqlalchemy.orm import selectinload

from data.entities.Driver import Driver
from data.entities.Person import Person
from data.repositories.RoleBaseRepo import RoleBaseRepository


class DriverRepository(RoleBaseRepository[Driver]):
    model = Driver


    async def get_by_license_number(self, license_number: str) -> Driver | None:
        stmt = (
            select(Driver)
            .where(Driver.license_number == license_number)
            .options(selectinload(Driver.person))
        )
        result = await self.session.exec(stmt)
        return result.first()
    