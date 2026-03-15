from typing import Optional

from sqlmodel import select
from data.entities.SmsCode import SmsCode
from data.repositories.BaseRepo import BaseRepository


class AuthRepository(BaseRepository[SmsCode]):
    model = SmsCode
    
    async def invalidate_old_sms_codes(self, phone: str) -> None:
        result = await self.session.exec(
            select(SmsCode).where(
                SmsCode.phone == phone,
                SmsCode.consumed == False,
            )
        )
        codes = result.all()
        for item in codes:
            item.consumed = True
        await self.session.flush()
            
    async def get_last_code_result(self, phone: str) -> Optional[SmsCode]:
        last_code_result = await self.session.exec(
        select(SmsCode)
        .where(SmsCode.phone == phone)
        .order_by(SmsCode.created_at.desc())
        )
        last_code = last_code_result.first()
        if last_code is not None:
            return last_code
        return None
        
    async def get_actual_sms_code(self, phone: str) -> Optional[SmsCode]:
        stmt = (
            select(SmsCode)
            .where(
                SmsCode.phone == phone,
                SmsCode.consumed == False,
            )
            .order_by(SmsCode.created_at.desc())
            .limit(1)
        )
        result = await self.session.exec(stmt)
        return result.first()