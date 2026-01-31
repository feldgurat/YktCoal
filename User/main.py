from fastapi import Depends, FastAPI, status
import uvicorn

from sqlalchemy.ext.asyncio import AsyncSession
from data.Database import get_session, init_db
from data.entities.Person import Person
from data.repositories.BaseRepo import BaseRepository
from data.schemas.Person import PersonCreate, PersonRead


app = FastAPI()

@app.on_event("startup")
async def startup() ->None:
    await init_db()

@app.get("/")
def root():
    return "1234567890"

@app.post("/persons", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
async def add_person(person: PersonCreate, session: AsyncSession = Depends(get_session)):
    r = BaseRepository(Person, session)
    entity = Person(**person.model_dump())
    entity.password_hash = "123"
    print(person)
    print(entity)
    r.save_entity(entity)
    await session.commit()
    await session.refresh(entity)
    return entity


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)