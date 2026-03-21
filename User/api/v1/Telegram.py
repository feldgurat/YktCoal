from fastapi import APIRouter, Depends, status
from api.routes import API_V1_PREFIX, REGISTER, TELEGRAM
from api.v1.dependencies import CurrentAdminDep, get_current_person
from data.Database import SessionDep
from data.schemas.Person import PersonCreate, PersonRead


router = APIRouter(
    prefix=f"{API_V1_PREFIX}{TELEGRAM}",
    tags=["Telegram"]
)

@router.get(REGISTER, response_model=PersonRead, status_code=status.HTTP_201_CREATED)
def telegram_register(telegram_token: str, person: PersonCreate, session: SessionDep):
    return "1234567890"