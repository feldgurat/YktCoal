"""Высокоуровневые операции: регистрация, вход, получение профиля."""

import logging

from services import api_client, token_store

logger = logging.getLogger(__name__)


async def register_and_get_code(
    name: str,
    phone: str,
    telegram_user_id: int,
) -> tuple[bool, str]:
    """Регистрирует пользователя. Возвращает (ok, message)."""
    resp = await api_client.register(
        name=name,
        phone=phone,
        telegram_user_id=telegram_user_id,
    )
    if resp["status"] == 201:
        msg = resp["body"].get("message", "")
        return True, msg
    detail = resp["body"].get("detail", "Ошибка регистрации")
    return False, detail


async def request_code(phone: str) -> tuple[bool, str]:
    """Запрашивает OTP-код для входа."""
    resp = await api_client.request_sign_in_code(phone)
    if resp["status"] == 200:
        # debug_code приходит пока TODO не убран
        code = resp["body"].get("debug_code", "")
        return True, code
    detail = resp["body"].get("detail", "Ошибка")
    return False, detail


async def verify_code(telegram_id: int, phone: str, code: str) -> tuple[bool, str]:
    """Проверяет OTP и сохраняет токены."""
    resp = await api_client.verify_sign_in_code(phone, code)
    if resp["status"] == 200:
        body = resp["body"]
        token_store.save(
            telegram_id,
            body["access_token"],
            body["refresh_token"],
        )
        return True, "Авторизация успешна"
    detail = resp["body"].get("detail", "Неверный код")
    return False, detail


async def _ensure_token(telegram_id: int) -> str | None:
    """Возвращает access_token, при необходимости обновляя через refresh."""
    pair = token_store.get(telegram_id)
    if pair is None:
        return None

    # Пробуем текущий access
    test = await api_client.get_me(pair.access_token)
    if test["status"] == 200:
        return pair.access_token

    # Пробуем refresh
    resp = await api_client.refresh_tokens(pair.refresh_token)
    if resp["status"] == 200:
        body = resp["body"]
        token_store.save(telegram_id, body["access_token"], body["refresh_token"])
        return body["access_token"]

    # Оба протухли
    token_store.remove(telegram_id)
    return None


async def get_profile(telegram_id: int) -> tuple[bool, dict | str]:
    """Получает профиль текущего пользователя. Возвращает (ok, data|error)."""
    access = await _ensure_token(telegram_id)
    if access is None:
        return False, "Вы не авторизованы. Используйте /start"

    resp = await api_client.get_me(access)
    if resp["status"] == 200:
        return True, resp["body"]
    return False, resp["body"].get("detail", "Ошибка")


def is_logged_in(telegram_id: int) -> bool:
    return token_store.has(telegram_id)


def logout(telegram_id: int) -> None:
    token_store.remove(telegram_id)
