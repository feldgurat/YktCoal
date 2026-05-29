from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    REDIS_URL: str

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"

    INTERNAL_SERVICE_KEY: str
    INTERNAL_TELEGRAM_SERVICE_KEY: str

    USER_SERVICE_URL: str

    CORS_ALLOWED_ORIGINS: list[str]

    UPLOADS_DIR: str = "/data/uploads"
    UPLOAD_MAX_BYTES: int = 10 * 1024 * 1024

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
