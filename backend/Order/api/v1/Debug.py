from fastapi import APIRouter, HTTPException
from sqlmodel import SQLModel

from api.routes import ADMIN, API_V1_PREFIX
from api.v1.dependencies import CurrentAdminDep
from config import settings
from data.Database import engine
from data.schemas.common import MessageResponse

router = APIRouter(prefix=f"{API_V1_PREFIX}{ADMIN}", tags=["Debug"])


@router.post("/reset-database", response_model=MessageResponse)
async def reset_database(_admin: CurrentAdminDep):
    if settings.is_production:
        raise HTTPException(status_code=404)

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
    return MessageResponse(success=True, message="База очищена")
