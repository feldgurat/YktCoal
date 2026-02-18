from fastapi import HTTPException, status
from data.schemas.Person import PersonCreate, PersonRead
from main import app
from services.PersonService import add_new_person


@app.get("/")
def root():
    return "1234567890"

@app.post("/persons", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
async def add_person(person: PersonCreate):
    try:
        await add_new_person(person)
    except:
