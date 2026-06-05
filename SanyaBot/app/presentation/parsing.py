"""Парсинг пользовательского ввода (числа, даты)."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation

from app.domain.exceptions import BotError


class InputError(BotError):
    pass


def parse_positive_decimal(raw: str) -> Decimal:
    try:
        value = Decimal(raw.replace(",", ".").strip())
    except (InvalidOperation, ValueError) as exc:
        raise InputError("Введите число, например 12.5") from exc
    if value <= 0:
        raise InputError("Значение должно быть больше нуля")
    return value


def parse_future_date(raw: str) -> datetime:
    raw = raw.strip()
    for fmt in ("%d.%m.%Y", "%d.%m.%Y %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw, fmt)
        except ValueError:
            continue
    raise InputError("Введите дату в формате ДД.ММ.ГГГГ, например 25.12.2026")
