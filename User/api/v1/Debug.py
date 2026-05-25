from data.Database import async_session_factory, engine
from data.schemas.Common import MessageResponse
from fastapi import APIRouter
from services.Startup import create_default_admin
from sqlmodel import SQLModel

from api.routes import ADMIN, API_V1_PREFIX
from api.v1.dependencies import CurrentAdminDep

router = APIRouter(prefix=f"{API_V1_PREFIX}{ADMIN}", tags=["Auth"])


@router.post("/reset-database", response_model=MessageResponse)
async def reset_database(_admin: CurrentAdminDep):
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session_factory() as session:
        await create_default_admin(session)

    return MessageResponse(success=True, message="База очищена, админ создан")
