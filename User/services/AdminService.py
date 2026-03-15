from typing import Annotated
from uuid import UUID
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from data.Database import SessionDep
from data.entities.Admin import Admin
from data.entities.Person import Person
from data.repositories.AdminRepo import AdminRepository
from data.repositories.PersonRepo import PersonRepository
from data.schemas.Admin import AdminCreate, AdminCreateWithPerson, AdminUpdate





class AdminService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.personsRepo = PersonRepository(session)
        self.adminsRepo = AdminRepository(session)

    async def create_for_existing_person(
            self,
            person_id: UUID,
            payload: AdminCreate
    ) -> Admin:
        person = await self.personsRepo.get(person_id)
        if person is None:
            raise ValueError("Person с таким id не существует")
        if await self.adminsRepo.exists_for_person(person_id):
            raise ValueError("Admin для этого Person уже существует")
        admin = Admin(
            person=person
        )
        await self.adminsRepo.add(admin)
        await self.session.flush()
        admin = await self.adminsRepo.get_with_person(person_id)
        assert admin is not None
        return admin
    
    async def create_full(
            self,
            payload: AdminCreateWithPerson
    ) -> Admin:
        admin = Admin(
            person=Person(**payload.person.model_dump())
        )
        if await self.personsRepo.get_by_contact_number(admin.contact_number) is not None:
            raise ValueError("Person с таким contact_number уже существует")
        
        if admin.telegram_user_id is not None and await self.personsRepo.get_by_telegram_user_id(admin.telegram_user_id) is not None:
            raise ValueError("Person с таким telegram_user_id уже существует")
        
        if await self.adminsRepo.get_by_contact_number(admin.contact_number) is not None:
            raise ValueError("User с таким contact_number уже существует")
        await self.adminsRepo.add(admin)
        await self.session.flush()

        admin = await self.adminsRepo.get_with_person(admin.person_id)
        assert admin is not None
        return admin
    
    async def get(self, person_id: UUID) -> Admin | None:
        return await self.adminsRepo.get_with_person(person_id)
    
    async def update(
            self,
            person_id: UUID,
            payload: AdminUpdate
    ) -> Admin | None:
        admin = await self.adminsRepo.get_with_person(person_id)
        if admin is None:
            return None
        data = payload.model_dump(exclude_unset=True)

        if "person" in data and data["person"] is not None:
            person_data = data["person"]
            for field, value in person_data.items():
                setattr(admin.person, field, value)
        await self.session.flush()
        admin = await self.adminsRepo.get_with_person(person_id)
        return admin
    
    async def delete(self, person_id: UUID) -> bool:
        user = await self.adminsRepo.get_with_person(person_id)
        if user is None:
            return False

        await self.adminsRepo.delete(user)
        await self.session.flush()
        return True


def get_admin_service(
    session: SessionDep,
) -> AdminService:
    return AdminService(session)
    
AdminServiceDep = Annotated[AdminService, Depends(get_admin_service)]