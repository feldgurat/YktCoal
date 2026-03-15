from fastapi import APIRouter, Depends
from api.v1.dependencies import CurrentAdminDep, get_current_person
from data.Database import SessionDep


router = APIRouter()

@router.get("/api/telegram/register", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
def telegram_register(person: PersonCreate, session: SessionDep):
    return "1234567890"