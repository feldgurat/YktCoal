from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./db/orders.db"
    REDIS_URL: str = "redis://redis:6379/0"

    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"

    DRIVER_SERVICE_URL: str = "http://driver-backend:8002"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
