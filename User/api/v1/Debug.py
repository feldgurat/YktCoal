from fastapi import APIRouter, HTTPException
from sqlmodel import SQLModel

from api.routes import ADMIN, API_V1_PREFIX
from api.v1.dependencies import CurrentAdminDep
from config import settings
from data.Database import async_session_factory, engine
from data.schemas.Common import MessageResponse
from services.Startup import create_default_admin

router = APIRouter(prefix=f"{API_V1_PREFIX}{ADMIN}", tags=["Debug"])


@router.post("/reset-database", response_model=MessageResponse)
async def reset_database(_admin: CurrentAdminDep):
    if settings.is_production:
        raise HTTPException(status_code=404)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    async with async_session_factory() as session:
        await create_default_admin(session)

    return MessageResponse(success=True, message="База очищена, админ создан")
