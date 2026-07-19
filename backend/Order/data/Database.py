from typing import Annotated

from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from config import settings
from ykt_common.database import Database

_db = Database(settings.DATABASE_URL)

engine = _db.engine
async_session_factory = _db.session_factory
create_tables = _db.create_tables
get_session = _db.get_session

SessionDep = Annotated[AsyncSession, Depends(get_session)]
