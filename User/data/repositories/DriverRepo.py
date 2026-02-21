from typing import Optional
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from .BaseRepo import BaseRepository
from data.entities.Driver import Driver


class DriverRepository(BaseRepository[Driver]):
    def __init__(self):
        super().__init__(Driver)

    def get_driver_by_license(self, license_number: str, session: AsyncSession) -> Optional[Driver]:
        stmt = select(Driver).where(Driver.licenseNumber == license_number)
        return self.session.exec(stmt).first()
