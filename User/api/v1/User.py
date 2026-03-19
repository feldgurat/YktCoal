from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from api.routes import API_V1_PREFIX, USERS
from api.v1.dependencies import CurrentPersonDep, get_current_person
from data.Database import SessionDep
from data.schemas.Common import DeleteResponse
from data.schemas.User import UserCreateWithPerson, UserRead, UserUpdate
from services.UserService import UserServiceDep


router = APIRouter(
    prefix=f"{API_V1_PREFIX}{USERS}", tags=["Users"],
    #dependencies=[Depends(get_current_person)]
)




@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def add_user(user: UserCreateWithPerson, userService: UserServiceDep):
    try:
        new_user = await userService.create_full(user)
        await userService.session.commit()
        return new_user
    except Exception as e:
        await userService.session.rollback()
        raise HTTPException(status_code=409, detail=str(e))
    
@router.get("", response_model=List[UserRead], status_code=status.HTTP_200_OK)
async def get_users_list(userService: UserServiceDep):
    user = await userService.get_list()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Users not found",
        )
    return user



@router.get("/by-id/{id}", response_model=UserRead)
async def get_user(id: UUID, userService: UserServiceDep):
    user = await userService.get(id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.get("/my_profile", response_model=UserRead)
async def get_my_profile(userService: UserServiceDep, current_person: CurrentPersonDep):
    user = await userService.get(current_person.id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

@router.patch("", response_model=UserRead)
async def edit_user(id: UUID, user: UserUpdate, userService: UserServiceDep):
    user = await userService.update(id, user)
    await userService.session.commit()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user

@router.delete("", response_model=DeleteResponse)
async def delete_user(id: UUID, userService: UserServiceDep):
    succ = await userService.delete(id)
    if succ:
        await userService.session.commit()
        return DeleteResponse(success=succ, status="User deleted. Person already exist.")
    else:
        return DeleteResponse(success=succ, status="Fail. User not exist")