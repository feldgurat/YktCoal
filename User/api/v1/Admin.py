from typing import List
from uuid import UUID
from fastapi import APIRouter, HTTPException, status

from api.routes import ADMINS, API_V1_PREFIX
from api.v1.dependencies import CurrentPersonDep
from data.schemas.Admin import AdminCreateWithPerson, AdminRead, AdminUpdate
from data.schemas.Common import DeleteResponse
from services.AdminService import AdminServiceDep


router = APIRouter(
    prefix=f"{API_V1_PREFIX}{ADMINS}", tags=["Admins"],
    #dependencies=[Depends(get_current_person)]
)




@router.post("", response_model=AdminRead, status_code=status.HTTP_201_CREATED)
async def add_user(driver: AdminCreateWithPerson, driverService: AdminServiceDep):
    try:
        new_user = await driverService.create_full(driver)
        await driverService.session.commit()
        return new_user
    except Exception as e:
        await driverService.session.rollback()
        raise HTTPException(status_code=409, detail=str(e))
    
@router.get("", response_model=List[AdminRead], status_code=status.HTTP_200_OK)
async def get_users_list(driverService: AdminServiceDep):
    driver = await driverService.get_list()
    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Users not found",
        )
    return driver



@router.get("/by-id/{id}", response_model=AdminRead)
async def get_user(id: UUID, driverService: AdminServiceDep):
    driver = await driverService.get(id)
    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return driver


@router.get("/my_profile", response_model=AdminRead)
async def get_my_profile(driverService: AdminServiceDep, current_person: CurrentPersonDep):
    driver = await driverService.get(current_person.id)
    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return driver

@router.patch("", response_model=AdminRead)
async def edit_user(id: UUID, driver: AdminUpdate, driverService: AdminServiceDep):
    driver = await driverService.update(id, driver)
    await driverService.session.commit()
    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return driver

@router.delete("", response_model=DeleteResponse)
async def delete_user(id: UUID, driverService: AdminServiceDep):
    succ = await driverService.delete(id)
    if succ:
        await driverService.session.commit()
        return DeleteResponse(success=succ, status="Admin deleted. Person already exist.")
    else:
        return DeleteResponse(success=succ, status="Fail. Admin not exist")