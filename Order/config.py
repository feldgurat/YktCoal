from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    INTERNAL_SERVICE_KEY: str
    INTERNAL_TELEGRAM_SERVICE_KEY: str

    CORS_ALLOWED_ORIGINS: list[str]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
