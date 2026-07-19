"""Конфигурация бота. Единственный источник настроек (SRP)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ── Telegram ───────────────────────────────────────────────
    BOT_TOKEN: str

    # ── Backend services ───────────────────────────────────────
    USER_SERVICE_URL: str = "http://user-backend:8000"
    ORDER_SERVICE_URL: str = "http://order-backend:8001"

    # Сервисный ключ, общий для всех Telegram-эндпоинтов бэкенда
    # (заголовок X-Service-Key). Должен совпадать с
    # INTERNAL_TELEGRAM_SERVICE_KEY в User- и Order-сервисах.
    INTERNAL_TELEGRAM_SERVICE_KEY: str

    # ── HTTP ───────────────────────────────────────────────────
    HTTP_TIMEOUT_SECONDS: float = 10.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
