"""DTO-команды для операций создания.

Отделяют намерение пользователя от транспортного формата API.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True, slots=True)
class NewOrder:
    resource_id: str
    dest_address: str
    volume: Decimal
    cost: Decimal
    requested_delivery_date: datetime
    comment: str | None = None
    latitude: Decimal | None = None
    longitude: Decimal | None = None


@dataclass(frozen=True, slots=True)
class NewOffer:
    order_id: str
    price: Decimal
    delivery_date: datetime
    comment: str | None = None


@dataclass(frozen=True, slots=True)
class RegisterUser:
    telegram_user_id: str
    phone: str
    name: str
    address: str | None = None
