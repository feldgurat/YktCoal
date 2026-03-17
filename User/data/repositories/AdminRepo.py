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
        p = await self.get_with_person(person_id)
        return p is not None
    
    async def list_with_person(self) -> list[Admin]:
        stmt = select(Admin).options(selectinload(Admin.person))
        result = await self.session.exec(stmt)
        return list(result.all())
    
    async def get_by_contact_number(self, contact_number: str) -> Admin | None:
        stmt = (
            select(Admin)
            .where(Admin.contact_number == contact_number)
            .options(selectinload(Admin.person))
        )
        result = await self.session.exec(stmt)
        return result.first()
    
    async def get_by_telegram_user_id(self, telegram_user_id: str) -> Admin | None:
        stmt = (
            select(Admin)
            .where(Admin.telegram_user_id == telegram_user_id)
            .options(selectinload(Admin.person))
        )
        result = await self.session.exec(stmt)
        return result.first()
    