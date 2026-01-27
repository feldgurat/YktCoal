from typing import Optional
from uuid import UUID

from sqlmodel import select

from .BaseRepo import BaseRepository
from data.entities.Driver import Driver


class DriverRepository(BaseRepository[Driver, UUID]):
    def __init__(self, session):
        super().__init__(Driver, session)

    def get_driver_by_license(self, license_number: str) -> Optional[Driver]:
        stmt = select(Driver).where(Driver.licenseNumber == license_number)
        return self.session.exec(stmt).first()
