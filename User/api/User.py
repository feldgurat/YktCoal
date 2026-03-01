from typing import List
from fastapi import APIRouter, HTTPException, status
from data.Database import SessionDep
from data.schemas.Person import PersonCreate, PersonRead
from data.schemas.User import UserCreateForExistingPerson, UserRead
from services.PersonService import add_new_person, get_all_persons
from services.UserService import add_new_user, get_all_users

router = APIRouter()


@router.get("/")
def root():
    return "1234567890"




@router.post("/persons", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
async def add_person(person: PersonCreate, session: SessionDep):
    try:
        new_person = await add_new_person(person, session)
        return new_person
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))

@router.get("/persons", response_model=List[PersonRead], status_code=status.HTTP_200_OK)
async def get_persons_list(session: SessionDep):
    try:
        return await get_all_persons(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def add_user(user: UserCreateForExistingPerson, session: SessionDep):
    try:
        new_user = await add_new_user(user, session)
        return new_user
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))
    
@router.get("/users", response_model=List[UserRead], status_code=status.HTTP_200_OK)
async def get_users_list(session: SessionDep):
    try:
        return await get_all_users(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/users/{id}")
async def get_users_list(session: SessionDep):
    pass 