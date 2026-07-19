"""Доменные сущности бота.

Это самый внутренний слой чистой архитектуры: чистые объекты Python
без зависимостей от aiogram, httpx или конкретного бэкенда. Всё остальное
зависит от этого слоя, а не наоборот.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import StrEnum


class Role(StrEnum):
    USER = "user"
    ADMIN = "admin"
    DRIVER = "driver"


class OrderStatus(StrEnum):
    NEW = "new"
    ACCEPTED = "accepted"
    IN_PROCESS = "in_process"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class OfferStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"


@dataclass(frozen=True, slots=True)
class User:
    id: str
    name: str
    contact_number: str
    telegram_user_id: str | None
    address: str | None
    roles: tuple[str, ...]
    is_active: bool

    def has_role(self, role: Role) -> bool:
        return role.value in self.roles

    @property
    def is_driver(self) -> bool:
        return self.has_role(Role.DRIVER)


@dataclass(frozen=True, slots=True)
class Resource:
    id: str
    name: str
    price: Decimal
    unit: str
    is_active: bool


@dataclass(frozen=True, slots=True)
class Order:
    id: str
    user_id: str
    accepted_driver_id: str | None
    resource_id: str
    dest_address: str
    volume: Decimal
    cost: Decimal
    final_price: Decimal | None
    requested_delivery_date: datetime
    order_date: datetime
    status: OrderStatus
    comment: str | None
    latitude: Decimal | None
    longitude: Decimal | None


@dataclass(frozen=True, slots=True)
class Offer:
    id: str
    order_id: str
    driver_user_id: str
    price: Decimal
    comment: str | None
    delivery_date: datetime
    status: OfferStatus
