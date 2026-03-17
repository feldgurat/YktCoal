from typing import Annotated, List
from uuid import UUID
from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from data.Database import SessionDep
from data.entities.Driver import Driver
from data.entities.Person import Person
from data.repositories.DriverRepo import DriverRepository
from data.repositories.PersonRepo import PersonRepository
from data.schemas.Driver import DriverCreate, DriverCreateWithPerson, DriverRead, DriverUpdate





class DriverService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.personsRepo = PersonRepository(session)
        self.driversRepo = DriverRepository(session)

    def _to_driver_read(self, driver: Driver) -> DriverRead:
        return DriverRead(
            id=driver.person_id,
            name=driver.name,
            contact_number=driver.contact_number,
            telegram_user_id=driver.telegram_user_id,
            license_number=driver.license_number,
        )
    
    async def create_for_existing_person(
            self,
            person_id: UUID,
            payload: DriverCreate
    ) -> DriverRead:
        person = await self.personsRepo.get(person_id)
        if person is None:
            raise ValueError("Person с таким id не существует")
        if await self.driversRepo.exists_for_person(person_id):
            raise ValueError("Driver для этого Person уже существует")
        driver = Driver(
            person=person,
            license_number=payload.license_number
        )
        await self.driversRepo.add(driver)
        await self.session.flush()
        driver = await self.driversRepo.get_with_person(person_id)
        assert driver is not None
        return self._to_driver_read(driver)
    
    async def create_full(
            self,
            payload: DriverCreateWithPerson
    ) -> DriverRead:
        driver = Driver(
            license_number=payload.license_number,
            person=Person(**payload.person.model_dump())
        )
        if await self.personsRepo.get_by_contact_number(driver.contact_number) is not None:
            raise ValueError("Person с таким contact_number уже существует")
        
        if driver.telegram_user_id is not None and await self.personsRepo.get_by_telegram_user_id(driver.telegram_user_id) is not None:
            raise ValueError("Person с таким telegram_user_id уже существует")
        
        if await self.driversRepo.get_by_contact_number(driver.contact_number) is not None:
            raise ValueError("User с таким contact_number уже существует")
        await self.driversRepo.add(driver)
        await self.session.flush()

        driver = await self.driversRepo.get_with_person(driver.person_id)
        assert driver is not None
        return self._to_driver_read(driver)
    
    async def get(self, person_id: UUID) -> DriverRead | None:
        return self._to_driver_read(await self.driversRepo.get_with_person(person_id))
    
    async def get_list(self) -> List[DriverRead]:
        drivers = await self.driversRepo.list_with_person()
        resps = [
            self._to_driver_read(driver)
            for driver in drivers
        ]
        return resps
    
    async def update(
            self,
            person_id: UUID,
            payload: DriverUpdate
    ) -> DriverRead | None:
        driver = await self.driversRepo.get_with_person(person_id)
        if driver is None:
            return None
        data = payload.model_dump(exclude_unset=True)

        if "license_number" in data:
            driver.license_number = data["license_number"]

        if "person" in data and data["person"] is not None:
            person_data = data["person"]
            for field, value in person_data.items():
                setattr(driver.person, field, value)
        await self.session.flush()
        user = await self.driversRepo.get_with_person(person_id)
        return self._to_driver_read(user)
    
    async def delete(self, person_id: UUID) -> bool:
        user = await self.driversRepo.get_with_person(person_id)
        if user is None:
            return False

        await self.driversRepo.delete(user)
        await self.session.flush()
        return True


def get_driver_service(
    session: SessionDep,
) -> DriverService:
    return DriverService(session)
    
DriverServiceDep = Annotated[DriverService, Depends(get_driver_service)]