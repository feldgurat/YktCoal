import hashlib
import hmac
import logging
import secrets
import uuid
from datetime import UTC, datetime, timedelta
from typing import Annotated, Any

import jwt
from fastapi import Depends

from config import settings
from data.entities.Role import Role
from data.entities.User import User
from data.repositories.AuthRepo import AuthRepository, AuthRepositoryDep
from data.repositories.UserRepo import UserRepository, UserRepositoryDep
from data.schemas.Auth import RegisterIn
from services.Exeptions import (
    AppException,
    InvalidTokenError,
    InvalidTokenTypeError,
    OtpInvalidError,
    OtpRateLimitError,
    TokenExpiredError,
    TokenRevokedError,
    UserAlreadyExistsError,
    UserNotFoundError,
)

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, auth_repo: AuthRepository, user_repo: UserRepository) -> None:
        self._auth_repo = auth_repo
        self._user_repo = user_repo

    # ── OTP ────────────────────────────────────────────────────

    @staticmethod
    def generate_code() -> str:
        upper = 10**settings.OTP_CODE_LENGTH - 1
        return str(secrets.randbelow(upper)).zfill(settings.OTP_CODE_LENGTH)

    @staticmethod
    def hash_code(phone: str, code: str) -> str:
        return hashlib.sha256(f"{phone}:{code}".encode()).hexdigest()

    async def send_otp(self, phone: str) -> None:
        if await self._auth_repo.is_rate_limited(phone):
            raise OtpRateLimitError()

        code = self.generate_code()
        code_hash = self.hash_code(phone, code)

        await self._auth_repo.save_otp(phone, code_hash)
        await self._auth_repo.set_rate_limit(phone)

        await self._deliver_code(phone, code)

    @staticmethod
    async def _deliver_code(phone: str, code: str) -> None:
        # TODO: интеграция с SMS-провайдером (МТС Exolve):
        #   await send_sms_via_exolve(destination=phone, text=f"Код: {code}")
        if settings.OTP_DEBUG:
            logger.warning("OTP %s = %s (OTP_DEBUG, только для dev)", phone, code)
        else:
            logger.info("OTP отправлен на %s", phone)

    async def verify_otp(self, phone: str, code: str) -> None:
        stored_hash = await self._auth_repo.get_otp(phone)
        if stored_hash is None:
            raise OtpInvalidError("Код не найден или истёк")

        if not hmac.compare_digest(stored_hash, self.hash_code(phone, code)):
            attempts = await self._auth_repo.incr_attempts(phone)
            if attempts >= settings.OTP_MAX_ATTEMPTS:
                await self._auth_repo.delete_otp(phone)
                await self._auth_repo.reset_attempts(phone)
            raise OtpInvalidError()

        await self._auth_repo.delete_otp(phone)
        await self._auth_repo.reset_attempts(phone)

    # ── JWT ────────────────────────────────────────────────────

    def create_access_token(self, user_id: str, token_version: int, roles: list[str]) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": user_id,
            "type": "access",
            "ver": token_version,
            "roles": roles,
            "jti": str(uuid.uuid4()),
            "iat": now,
            "exp": now + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    def create_refresh_token(self, user_id: str, token_version: int) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": user_id,
            "type": "refresh",
            "ver": token_version,
            "jti": str(uuid.uuid4()),
            "iat": now,
            "exp": now + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
        }
        return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    def decode_token(self, token: str, expected_type: str) -> dict[str, Any]:
        try:
            payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        except jwt.ExpiredSignatureError:
            raise TokenExpiredError() from None
        except jwt.InvalidTokenError:
            raise InvalidTokenError() from None

        if payload.get("type") != expected_type:
            raise InvalidTokenTypeError()

        return payload

    def create_token_pair(
        self, user_id: str, token_version: int, roles: list[str]
    ) -> tuple[str, str]:
        return (
            self.create_access_token(user_id, token_version, roles),
            self.create_refresh_token(user_id, token_version),
        )

    # ── Token blacklist ────────────────────────────────────────

    async def is_token_revoked(self, jti: str) -> bool:
        return await self._auth_repo.is_token_blacklisted(jti)

    async def revoke_token(self, jti: str, exp_ts: int) -> None:
        now_ts = int(datetime.now(UTC).timestamp())
        ttl = max(exp_ts - now_ts, 1)
        await self._auth_repo.blacklist_token(jti, ttl)

    # ── High-level flows ───────────────────────────────────────

    async def request_sign_in_code(self, phone: str) -> None:
        user = await self._user_repo.get_by_contact_number(phone)
        if user is None:
            raise UserNotFoundError("Пользователя с таким номером нет в системе")
        await self.send_otp(phone)

    async def verify_sign_in_code(self, phone: str, code: str) -> tuple[User, str, str]:
        user = await self._user_repo.get_by_contact_number(phone)
        if user is None:
            raise UserNotFoundError()

        await self.verify_otp(phone, code)
        access, refresh = self.create_token_pair(str(user.id), user.token_version, user.role_names)
        await self._auth_repo.set_token_version(str(user.id), user.token_version)
        return user, access, refresh

    async def refresh_tokens(self, raw_refresh_token: str) -> tuple[str, str]:
        payload = self.decode_token(raw_refresh_token, expected_type="refresh")

        jti = payload["jti"]
        user_id = payload["sub"]
        token_version = payload.get("ver")

        if await self.is_token_revoked(jti):
            raise TokenRevokedError()

        user = await self._user_repo.get_by_id(uuid.UUID(user_id))
        if user is None:
            raise UserNotFoundError()

        if token_version != user.token_version:
            raise InvalidTokenError("Токен устарел")

        await self.revoke_token(jti, payload["exp"])
        user.token_version += 1
        await self._auth_repo.set_token_version(str(user.id), user.token_version)

        return self.create_token_pair(str(user.id), user.token_version, user.role_names)

    async def register(self, data: RegisterIn) -> User:
        existing = await self._user_repo.get_by_contact_number(data.contact_number)
        if existing is not None:
            raise UserAlreadyExistsError()

        user = User(
            name=data.name,
            contact_number=data.contact_number,
            telegram_user_id=data.telegram_user_id,
            address=data.address,
            roles=int(Role.USER),
        )
        await self._user_repo.create(user)

        await self.send_otp(data.contact_number)
        return user

    async def logout(self, access_payload: dict | None, refresh_token: str | None) -> None:
        """
        Отзывает access и refresh токены, если они валидны.+
        """
        if access_payload is not None:
            try:
                await self.revoke_token(access_payload["jti"], access_payload["exp"])
            except Exception:
                logger.warning("Failed to revoke access token during logout", exc_info=True)

        if refresh_token:
            try:
                refresh_payload = self.decode_token(refresh_token, expected_type="refresh")
                await self.revoke_token(refresh_payload["jti"], refresh_payload["exp"])
            except AppException:
                pass


def get_auth_service(auth_repo: AuthRepositoryDep, user_repo: UserRepositoryDep) -> AuthService:
    return AuthService(auth_repo, user_repo)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
