from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from api.routes import ADMINS, API_V1_PREFIX
from api.v1.dependencies import CurrentAdminDep, CurrentPersonDep, get_current_person
from data.schemas.Admin import AdminCreate, AdminCreateWithPerson, AdminRead, AdminUpdate
from data.schemas.Common import DeleteResponse
from services.AdminService import AdminServiceDep


router = APIRouter(
    prefix=f"{API_V1_PREFIX}{ADMINS}", tags=["Admins"],
    dependencies=[Depends(get_current_person)]
)




@router.post("", response_model=AdminRead, status_code=status.HTTP_201_CREATED)
async def add_admin(driver: AdminCreateWithPerson, driverService: AdminServiceDep):
    try:
        new_admin = await driverService.create_full(driver)
        await driverService.session.commit()
        return new_admin
    except Exception as e:
        await driverService.session.rollback()
        raise HTTPException(status_code=409, detail=str(e))
    
@router.get("", response_model=List[AdminRead], status_code=status.HTTP_200_OK)
async def get_admins_list(driverService: AdminServiceDep):
    driver = await driverService.get_list()
    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="admins not found",
        )
    return driver



@router.get("/by-id/{id}", response_model=AdminRead)
async def get_admin(id: UUID, driverService: AdminServiceDep):
    driver = await driverService.get(id)
    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="admin not found",
        )
    return driver


@router.get("/my_profile", response_model=AdminRead)
async def get_my_profile(driverService: AdminServiceDep, current_person: CurrentPersonDep):
    driver = await driverService.get(current_person.id)
    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Admin not found",
        )
    return driver

@router.post("/add_role/{id}", response_model=AdminRead)
async def add_admin_role(id: UUID, payload: AdminCreate, adminService: AdminServiceDep, current_person: CurrentAdminDep):
    try:
        admin = await adminService.create_for_existing_person(id, payload)
        await adminService.session.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    return admin

@router.patch("", response_model=AdminRead)
async def edit_admin(id: UUID, driver: AdminUpdate, driverService: AdminServiceDep):
    driver = await driverService.update(id, driver)
    await driverService.session.commit()
    if driver is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="admin not found",
        )
    return driver

@router.delete("", response_model=DeleteResponse)
async def delete_admin(id: UUID, driverService: AdminServiceDep):
    succ = await driverService.delete(id)
    if succ:
        await driverService.session.commit()
        return DeleteResponse(success=succ, status="Admin deleted. Person already exist.")
    else:
        return DeleteResponse(success=succ, status="Fail. Admin not exist")