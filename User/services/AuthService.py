from datetime import datetime, timedelta, timezone
import os
import re
from typing import Annotated
from fastapi import Depends
import jwt
import hmac
import hashlib
import secrets
from uuid import uuid4
from data.Database import SessionDep, get_redis
from data.entities.SmsCode import SmsCode
import httpx
from sqlmodel.ext.asyncio.session import AsyncSession
from data.repositories.AuthRepo import AuthRepository
from services.Exeptions import InvalidToken, InvalidTokenType, OtpRateLimitError, SmsProviderInternalError, SmsProviderResponseError, SmsProviderTimeoutError, TokenHasExpired

SMS_API_URL = os.getenv("SMS_API_URL")
SMS_API_KEY = os.getenv("SMS_API_KEY")
SMS_OTP_SECRET = os.getenv("SMS_OTP_SECRET")
OTP_TTL_SECONDS = os.getenv("OTP_TTL_SECONDS")
OTP_MAX_ATTEMPTS = os.getenv("OTP_MAX_ATTEMPTS")
SMS_SOURCE = os.getenv("SMS_SOURCE")


JWT_BLACKLIST_PREFIX = os.getenv("JWT_BLACKLIST_PREFIX")
SECRET_JWT_KEY = os.getenv("SECRET_JWT_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")


class AuthService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.authRepo = AuthRepository(session)

    def create_access_token(self, user_id: str, version: int) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)),
            "jti": str(uuid4()),
            "ver": version,
        }
        return jwt.encode(payload, SECRET_JWT_KEY, algorithm=JWT_ALGORITHM)


    def create_refresh_token(self, user_id: str, version: int) -> str:
        now = datetime.now(timezone.utc)
        payload = {
            "sub": user_id,
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=int(REFRESH_TOKEN_EXPIRE_DAYS)),
            "jti": str(uuid4()),
            "ver": version,
        }
        return jwt.encode(payload, SECRET_JWT_KEY, algorithm=JWT_ALGORITHM)

    def decode_token(self, token: str, expected_type: str) -> dict:
        try:
            payload = jwt.decode(
                token,
                SECRET_JWT_KEY,
                algorithms=[JWT_ALGORITHM],
                options={"require": ["sub", "type", "exp", "iat", "jti"]},
            )
        except jwt.ExpiredSignatureError:
            raise TokenHasExpired(status_code=401, message="Токен истёк")
        except jwt.InvalidTokenError:
            raise InvalidToken(status_code=401, message="Некорректный токен")

        if payload.get("type") != expected_type:
            raise InvalidTokenType(status_code=401, message="Неверный тип токена")

        return payload

    def normalize_phone(self, phone: str) -> str:
        phone = phone.strip()

        if not phone:
            raise ValueError("Некорректный номер телефона")

        # Разрешаем только цифры и обычные разделители
        if re.search(r"[^\d\s()+\-]", phone):
            raise ValueError("Некорректный номер телефона")

        # "+" может быть только в начале и только один
        if phone.count("+") > 1 or ("+" in phone and not phone.startswith("+")):
            raise ValueError("Некорректный номер телефона")

        digits = re.sub(r"\D", "", phone)

        # 10 цифр -> считаем, что это российский номер без 7/8
        if len(digits) == 10:
            digits = "7" + digits

        # 11 цифр с 8 или 7 -> приводим к формату 7XXXXXXXXXX   
        elif len(digits) == 11 and digits[0] in ("7", "8"):
            digits = "7" + digits[1:]

        else:
            raise ValueError("Некорректный номер телефона")

        return digits


    def generate_code(self) -> str:
        return str(secrets.randbelow(900000) + 100000)  # 6 цифр


    def hash_code(self, phone: str, code: str) -> str:
        raw = f"{phone}:{code}".encode()
        return hmac.new(SMS_OTP_SECRET.encode(), raw, hashlib.sha256).hexdigest()




    async def send_sms(destination: str, text: str) -> dict:
        payload = {
            "number": SMS_SOURCE,
            "text": text,
            "destination": destination,
        }

        headers = {
            "Authorization": f"Bearer {SMS_API_KEY}",
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    SMS_API_URL,
                    json=payload,
                    headers=headers,
                    timeout=10.0,
                )
                response.raise_for_status()
                return response.json()

            except httpx.TimeoutException:
                raise SmsProviderTimeoutError(status_code=504, detail="SMS провайдер не ответил вовремя")
            except httpx.HTTPStatusError as e:
                raise SmsProviderResponseError(
                    status_code=e.response.status_code,
                    detail=f"Ошибка SMS провайдера: {e.response.text}",
                )
            except Exception as e:
                raise SmsProviderInternalError(status_code=500, detail=f"Внутренняя ошибка: {str(e)}")
            
    async def invalide_old_codes(self, phone: str):
        self.authRepo.invalidate_old_sms_codes(phone)

    async def add_new_sms_code(self, phone: str, code_hash: str, expires_at: datetime):
        otp = SmsCode(
            phone=phone,
            code_hash=code_hash,
            expires_at=expires_at,
        )
        await self.authRepo.add(otp)


    async def resending_prot(self, phone: str):
        last_code = await self.authRepo.get_last_code_result(phone)
        if last_code and (datetime.utcnow() - last_code.SmsCode.created_at).seconds < 60:
            raise OtpRateLimitError("Попробуйте запросить код чуть позже")
        
    async def get_actual_sms_code(self, phone: str):
        last_code = await self.authRepo.get_actual_sms_code(phone)
        return last_code


    def _blacklist_key(self, jti: str) -> str:
        return f"{JWT_BLACKLIST_PREFIX}:{jti}"

    async def is_token_blacklisted(self, jti: str) -> bool:
        key = self._blacklist_key(jti)
        return bool(await get_redis().exists(key))


    async def add_token_to_blacklist(self, jti: str, exp_ts: int) -> None:
        from time import time

        now_ts = int(time())
        if exp_ts <= now_ts:
            return

        key = self._blacklist_key(jti)
        await get_redis().set(key, "1", exat=exp_ts)


def get_auth_service(
    session: SessionDep,
) -> AuthService:
    return AuthService(session)
    
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]