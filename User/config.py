from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    ENVIRONMENT: Literal["production", "staging", "development"] = "production"

    DATABASE_URL: str
    REDIS_URL: str

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    OTP_TTL_SECONDS: int = 300
    OTP_RATE_LIMIT_SECONDS: int = 60
    OTP_CODE_LENGTH: int = 6
    OTP_MAX_ATTEMPTS: int = 5
    # Только для разработки: если True — OTP-код пишется в лог сервера.
    # В проде ДОЛЖНО быть False, иначе код можно достать из логов.
    OTP_DEBUG: bool = False

    DEFAULT_ADMIN_NAME: str
    DEFAULT_ADMIN_PHONE: str

    INTERNAL_SERVICE_KEY: str
    INTERNAL_TELEGRAM_SERVICE_KEY: str
    CORS_ALLOWED_ORIGINS: list[str]
    COOKIE_SECURE: bool = False

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
