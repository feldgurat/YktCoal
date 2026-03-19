from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from api.routes import API_V1_PREFIX, DRIVERS
from api.v1.dependencies import CurrentPersonDep
from data.schemas.Common import DeleteResponse
from data.schemas.Driver import DriverCreateWithPerson, DriverRead, DriverUpdate
from services.DriverService import DriverServiceDep


router = APIRouter(
    prefix=f"{API_V1_PREFIX}{DRIVERS}", tags=["Drivers"],
    #dependencies=[Depends(get_current_person)]
)




@router.post("", response_model=DriverRead, status_code=status.HTTP_201_CREATED)
async def add_user(driver: DriverCreateWithPerson, driverService: DriverServiceDep):
    try:
        new_user = await driverService.create_full(driver)
        await driverService.session.commit()
        return new_user
    except Exception as e:
        await driverService.session.rollback()
        raise HTTPException(status_code=409, detail=str(e))
    
@router.get("", response_model=List[DriverRead], status_code=status.HTTP_200_OK)
async def get_users_list(driverService: DriverServiceDep):
    driver = await driverService.get_list()
    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Users not found",
        )
    return driver



@router.get("/by-id/{id}", response_model=DriverRead)
async def get_user(id: UUID, driverService: DriverServiceDep):
    driver = await driverService.get(id)
    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return driver


@router.get("/my_profile", response_model=DriverRead)
async def get_my_profile(driverService: DriverServiceDep, current_person: CurrentPersonDep):
    driver = await driverService.get(current_person.id)
    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return driver

@router.patch("", response_model=DriverRead)
async def edit_user(id: UUID, driver: DriverUpdate, driverService: DriverServiceDep):
    driver = await driverService.update(id, driver)
    await driverService.session.commit()
    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return driver

@router.delete("", response_model=DeleteResponse)
async def delete_user(id: UUID, driverService: DriverServiceDep):
    succ = await driverService.delete(id)
    if succ:
        await driverService.session.commit()
        return DeleteResponse(success=succ, status="Driver deleted. Person already exist.")
    else:
        return DeleteResponse(success=succ, status="Fail. Driver not exist")