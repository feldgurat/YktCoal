from typing import Optional

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from data.entities.Auth import SmsCode
from data.repositories.BaseRepo import BaseRepository


class AuthRepository(BaseRepository[SmsCode]):
    def __init__(self):
        super().__init__(SmsCode)
    async def invlide_old_sms_codes(self, phone: str, session: AsyncSession):
        old_codes_result = await session.exec(
            select(SmsCode).where(
                SmsCode.phone == phone,
                SmsCode.consumed == False,  # noqa: E712
            )
        )
        old_codes = old_codes_result.all()
        for item in old_codes:
            item.consumed = True
        await session.flush()
        
    async def get_last_code_result(self, phone: str, session: AsyncSession) -> Optional[SmsCode]:
        last_code_result = await session.execute(
        select(SmsCode)
        .where(SmsCode.phone == phone)
        .order_by(SmsCode.created_at.desc()) # type: ignore
        )
        last_code = last_code_result.first()
        if last_code != None:
            return last_code
        
    async def get_actual_sms_code(self, phone: str, session) -> Optional[SmsCode]:
        stmt = (
            select(SmsCode)
            .where(
                SmsCode.phone == phone,
                SmsCode.consumed == False,  # noqa: E712
            )
            .order_by(SmsCode.created_at.desc())
            .limit(1)
        )
        result = await session.execute(stmt)
        return result.scalar_one_or_none()