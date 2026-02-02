from fastapi import Depends, FastAPI, HTTPException, status
import uvicorn

from sqlalchemy.ext.asyncio import AsyncSession
from data.Database import get_session, init_db
from data.entities.Person import Person
from data.repositories.BaseRepo import BaseRepository
from data.repositories.exeptions import UniqueViolationError
from data.schemas.Person import PersonCreate, PersonRead


from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from argon2 import Type
# Настройки можно подбирать под вашу нагрузку/сервер.
# Ниже — разумный старт, но лучше калибровать под вашу среду.
ph = PasswordHasher(
    time_cost=3,          # число итераций
    memory_cost=64 * 1024,# KiB (64 MiB)
    parallelism=2,
    hash_len=32,
    salt_len=16,
    type=Type.ID          # <-- это и есть Argon2id
)


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
    entity.password_hash = ph.hash(person.password)
    print(person)
    print(entity)
    try:
        await r.save_entity(entity)
        await session.commit()
        await session.refresh(entity)
        return entity
    except UniqueViolationError as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "unique_violation",
                "field": getattr(e, "field", "unknown"),
                "value": getattr(e, "value", None),
            },
        )


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)