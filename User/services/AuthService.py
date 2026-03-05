from datetime import datetime, timedelta, timezone
import re
import jwt
import hmac
import hashlib
import secrets
from uuid import uuid4
from sqlmodel.ext.asyncio.session import AsyncSession
from data.Database import get_redis
from data.entities.Auth import SmsCode
import httpx
from data.repositories.AuthRepo import AuthRepository
from services.Exeptions import InvalidToken, InvalidTokenType, OtpRateLimitError, SmsProviderInternalError, SmsProviderResponseError, SmsProviderTimeoutError, TokenHasExpired

EXOLVE_API_URL = "https://api.exolve.ru/messaging/v1/SendSMS"
EXOLVE_API_KEY = "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJRV05sMENiTXY1SHZSV29CVUpkWjVNQURXSFVDS0NWODRlNGMzbEQtVHA0In0.eyJleHAiOjIwODcxOTAwNzksImlhdCI6MTc3MTgzMDA3OSwianRpIjoiNzM1YTZjYTktY2Y0Yi00ZDljLTk0MWItYzkzN2E5NDU5YjFhIiwiaXNzIjoiaHR0cHM6Ly9zc28uZXhvbHZlLnJ1L3JlYWxtcy9FeG9sdmUiLCJhdWQiOiJhY2NvdW50Iiwic3ViIjoiYmNkMjFlYTUtYTQ0Ny00MWQ4LTk2ZTgtN2FmMWE2NTc0OGU3IiwidHlwIjoiQmVhcmVyIiwiYXpwIjoiYzk5NjJkNjUtYzdiZC00YzU0LWFkZDItNTBlY2U1ZDU2NDk5Iiwic2Vzc2lvbl9zdGF0ZSI6IjQ4ZTVjN2Y1LTI2MWYtNGMzNi04ZDQzLTA1ZDVhNDIwYTc4OCIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsiZGVmYXVsdC1yb2xlcy1leG9sdmUiLCJvZmZsaW5lX2FjY2VzcyIsInVtYV9hdXRob3JpemF0aW9uIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsiYWNjb3VudCI6eyJyb2xlcyI6WyJtYW5hZ2UtYWNjb3VudCIsIm1hbmFnZS1hY2NvdW50LWxpbmtzIiwidmlldy1wcm9maWxlIl19fSwic2NvcGUiOiJleG9sdmVfYXBwIHByb2ZpbGUgZW1haWwiLCJzaWQiOiI0OGU1YzdmNS0yNjFmLTRjMzYtOGQ0My0wNWQ1YTQyMGE3ODgiLCJ1c2VyX3V1aWQiOiI1MzI1N2FkMy1mNzVkLTQ0MmUtYWUwMS1jNDhlMGZjNDNmOTAiLCJjbGllbnRIb3N0IjoiMTcyLjE2LjE2MS4xOSIsImVtYWlsX3ZlcmlmaWVkIjpmYWxzZSwiY2xpZW50SWQiOiJjOTk2MmQ2NS1jN2JkLTRjNTQtYWRkMi01MGVjZTVkNTY0OTkiLCJhcGlfa2V5Ijp0cnVlLCJhcGlmb25pY2Ffc2lkIjoiYzk5NjJkNjUtYzdiZC00YzU0LWFkZDItNTBlY2U1ZDU2NDk5IiwiYmlsbGluZ19udW1iZXIiOiIxMzU3Njc0IiwiYXBpZm9uaWNhX3Rva2VuIjoiYXV0ZWRiYzZjYjgtNGNiYy00YzUzLThlYTEtMGJjZGFmM2NkNjZiIiwicHJlZmVycmVkX3VzZXJuYW1lIjoic2VydmljZS1hY2NvdW50LWM5OTYyZDY1LWM3YmQtNGM1NC1hZGQyLTUwZWNlNWQ1NjQ5OSIsImN1c3RvbWVyX2lkIjoiMTU1Njg4IiwiY2xpZW50QWRkcmVzcyI6IjE3Mi4xNi4xNjEuMTkifQ.fXlQNRyi4c7lzvjHGj2XWNkiumRgJ1QIhuU4sCsUKZvV6KBkTNB1JefWY6pBnLphSjyMLzHOBLryFqj-0IJcxn3naLFN8_38Bm4Ai5CE417Ltv2YYIiby4G-JZ03wxls4TOOn8BVChAtwWNNknhA1EGluIgjCxs5PfdmYqjkZUy0bifRAUtVxfY20KYqOaAOVcrd72IkZ48y1DZPeaEx8-hc69lz95CHNCTFk7LmSMJQt5yeV4Jgl-vYKIIWk5Q6PA6ktDfL09vOjvdn3sXaB8GK37LHuq-Ci6sMGmniaDAWUdKh-kkhoDwwL5hE0UKdf7OtWK1lf_DLOl2OrUguZA"  # используйте os.getenv("EXOLVE_API_KEY")

OTP_SECRET = "super-secret-key"          # лучше брать из env
OTP_TTL_SECONDS = 300                    # 5 минут
OTP_MAX_ATTEMPTS = 5
EXOLVE_SOURCE_NUMBER = "79587363725"     # твой номер/имя отправителя


BLACKLIST_PREFIX = "jwt:blacklist"


SECRET_KEY = "super-secret"
ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = 15
REFRESH_TOKEN_EXPIRE_DAYS = 30


def create_access_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,                # id пользователя
        "type": "access",              # тип токена
        "iat": now,                    # issued at
        "exp": now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "jti": str(uuid4()),           # уникальный id токена
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(user_id: str, version: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "type": "refresh",
        "iat": now,
        "exp": now + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS),
        "jti": str(uuid4()),
        "ver": version,                # версия учётных данных / токенов
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str, expected_type: str) -> dict:
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={
                "require": ["sub", "type", "exp", "iat", "jti"],
            },
        )
    except jwt.ExpiredSignatureError:
        raise TokenHasExpired(
            status_code=401,
            detail="Токен истёк",
        )
    except jwt.InvalidTokenError:
        raise InvalidToken(
            status_code=401,
            detail="Некорректный токен",
        )

    if payload.get("type") != expected_type:
        raise InvalidTokenType(
            status_code=401,
            detail="Неверный тип токена",
        )

    return payload

def normalize_phone(phone: str) -> str:
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


def generate_code() -> str:
    return str(secrets.randbelow(900000) + 100000)  # 6 цифр


def hash_code(phone: str, code: str) -> str:
    raw = f"{phone}:{code}".encode()
    return hmac.new(OTP_SECRET.encode(), raw, hashlib.sha256).hexdigest()




async def send_sms_via_exolve(destination: str, text: str) -> dict:
    payload = {
        "number": EXOLVE_SOURCE_NUMBER,
        "text": text,
        "destination": destination,
    }

    headers = {
        "Authorization": f"Bearer {EXOLVE_API_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                EXOLVE_API_URL,
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
        
async def invalide_old_codes(phone: str, session: AsyncSession):
    # инвалидируем старые коды
    authRepo: AuthRepository = AuthRepository()
    authRepo.invlide_old_sms_codes(phone, session)

async def add_new_sms_code(phone: str, code_hash: str, expires_at: datetime, session: AsyncSession):
    authRepo: AuthRepository = AuthRepository()
    otp = SmsCode(
        phone=phone,
        code_hash=code_hash,
        expires_at=expires_at,
    )
    await authRepo.save_entity(otp, session)


async def resending_prot(phone: str, session: AsyncSession):
    authRepo: AuthRepository = AuthRepository()
    last_code = await authRepo.get_last_code_result(phone, session)
    if last_code and (datetime.utcnow() - last_code.SmsCode.created_at).seconds < 60:
        raise OtpRateLimitError("Попробуйте запросить код чуть позже")
    
async def get_actual_sms_code(phone: str, session: AsyncSession):
    authRepo: AuthRepository = AuthRepository()
    last_code = await authRepo.get_actual_sms_code(phone, session)
    return last_code


def _blacklist_key(jti: str) -> str:
    return f"{BLACKLIST_PREFIX}:{jti}"

async def is_token_blacklisted(jti: str) -> bool:
    key = _blacklist_key(jti)
    return bool(await get_redis().exists(key))


async def add_token_to_blacklist(jti: str, exp_ts: int) -> None:
    from time import time

    now_ts = int(time())
    if exp_ts <= now_ts:
        return

    key = _blacklist_key(jti)
    await get_redis().set(key, "1", exat=exp_ts)
