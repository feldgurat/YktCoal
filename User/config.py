from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./db/app.db"
    REDIS_URL: str = "redis://redis:6379/0"

    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    OTP_TTL_SECONDS: int = 300
    OTP_RATE_LIMIT_SECONDS: int = 60
    OTP_CODE_LENGTH: int = 4

    DEFAULT_ADMIN_NAME: str = "Admin"
    DEFAULT_ADMIN_PHONE: str = "+70000000000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
