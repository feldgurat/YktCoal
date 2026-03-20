from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status

from api.routes import API_V1_PREFIX, PERSONS
from api.v1.dependencies import CurrentPersonDep, get_current_person
from data.schemas.Common import DeleteResponse
from data.schemas.Person import PersonCreate, PersonRead, PersonUpdate
from services.PersonService import PersonServiceDep


router = APIRouter(
    prefix=f"{API_V1_PREFIX}{PERSONS}", tags=["Persons"],
    dependencies=[Depends(get_current_person)]
)




@router.post("", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
async def add_person(person: PersonCreate, personService: PersonServiceDep):
    try:
        new_person = await personService.create(person)
        await personService.session.commit()
        return new_person
    except Exception as e:
        await personService.session.rollback()
        raise HTTPException(status_code=409, detail=str(e))
    
@router.get("", response_model=List[PersonRead], status_code=status.HTTP_200_OK)
async def get_persons_list(personService: PersonServiceDep):
    person = await personService.get_list()
    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="persons not found",
        )
    return person



@router.get("/by-id/{id}", response_model=PersonRead)
async def get_person(id: UUID, personService: PersonServiceDep):
    person = await personService.get(id)
    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="person not found",
        )
    return person


# @router.get("/my_profile", response_model=PersonRead)
# async def get_my_profile(personService: PersonServiceDep, current_person: CurrentPersonDep):
#     person = await personService.get(current_person.id)
#     if person is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Person not found",
#         )
#     return person

@router.patch("", response_model=PersonRead)
async def edit_person(id: UUID, person: PersonUpdate, personService: PersonServiceDep):
    person = await personService.update(id, person)
    await personService.session.commit()
    if person is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Person not found",
        )
    return person

@router.delete("", response_model=DeleteResponse)
async def delete_person(id: UUID, personService: PersonServiceDep):
    succ = await personService.delete(id)
    if succ:
        await personService.session.commit()
        return DeleteResponse(success=succ, status="Person and his roles deleted.")
    else:
        return DeleteResponse(success=succ, status="Fail. Person not exist")