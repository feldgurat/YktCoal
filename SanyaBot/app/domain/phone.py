"""Нормализация телефона к каноническому виду +7XXXXXXXXXX.

Повторяет правило бэкенда, чтобы номер из Telegram-контакта совпадал с тем,
под которым пользователь мог зарегистрироваться через веб.
"""

from __future__ import annotations

import re

from app.domain.exceptions import BotError


class InvalidPhoneError(BotError):
    pass


def normalize_phone(raw: str) -> str:
    digits = re.sub(r"\D", "", raw)
    if digits.startswith("8") and len(digits) == 11:
        digits = "7" + digits[1:]
    if not digits.startswith("7") or len(digits) != 11:
        raise InvalidPhoneError("Некорректный номер телефона")
    return f"+{digits}"
