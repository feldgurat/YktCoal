"""Преобразование между JSON бэкенда и доменными моделями.

Изолирует доменный слой от формата API: если бэкенд изменит имена полей,
правки коснутся только этого модуля (SRP).
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from app.domain.commands import NewOffer, NewOrder, RegisterUser
from app.domain.models import (
    Offer,
    OfferStatus,
    Order,
    OrderStatus,
    Resource,
    User,
)


def _dec(value: Any) -> Decimal | None:
    return None if value is None else Decimal(str(value))


def _dt(value: Any) -> datetime:
    return datetime.fromisoformat(value)


# ── JSON → domain ──────────────────────────────────────────────


def to_user(data: dict[str, Any]) -> User:
    return User(
        id=str(data["id"]),
        name=data["name"],
        contact_number=data["contact_number"],
        telegram_user_id=data.get("telegram_user_id"),
        address=data.get("address"),
        roles=tuple(data.get("roles", ())),
        is_active=bool(data.get("is_active", True)),
    )


def to_resource(data: dict[str, Any]) -> Resource:
    return Resource(
        id=str(data["id"]),
        name=data["name"],
        price=_dec(data["price"]),
        is_active=bool(data.get("is_active", True)),
    )


def to_order(data: dict[str, Any]) -> Order:
    return Order(
        id=str(data["id"]),
        user_id=str(data["user_id"]),
        accepted_driver_id=(
            str(data["accepted_driver_id"]) if data.get("accepted_driver_id") else None
        ),
        resource_id=str(data["resource_id"]),
        dest_address=data["dest_address"],
        volume=_dec(data["volume"]),
        cost=_dec(data["cost"]),
        final_price=_dec(data.get("final_price")),
        requested_delivery_date=_dt(data["requested_delivery_date"]),
        order_date=_dt(data["order_date"]),
        status=OrderStatus(data["status"]),
        comment=data.get("comment"),
        latitude=_dec(data.get("latitude")),
        longitude=_dec(data.get("longitude")),
    )


def to_offer(data: dict[str, Any]) -> Offer:
    return Offer(
        id=str(data["id"]),
        order_id=str(data["order_id"]),
        driver_user_id=str(data["driver_user_id"]),
        price=_dec(data["price"]),
        comment=data.get("comment"),
        delivery_date=_dt(data["delivery_date"]),
        status=OfferStatus(data["status"]),
    )


# ── domain command → JSON ──────────────────────────────────────


def order_create_payload(user_id: str, command: NewOrder) -> dict[str, Any]:
    return {
        "user_id": user_id,
        "resource_id": command.resource_id,
        "dest_address": command.dest_address,
        "volume": str(command.volume),
        "cost": str(command.cost),
        "requested_delivery_date": command.requested_delivery_date.isoformat(),
        "comment": command.comment,
        "latitude": None if command.latitude is None else str(command.latitude),
        "longitude": None if command.longitude is None else str(command.longitude),
    }


def offer_create_payload(user_id: str, command: NewOffer) -> dict[str, Any]:
    return {
        "user_id": user_id,
        "order_id": command.order_id,
        "price": str(command.price),
        "delivery_date": command.delivery_date.isoformat(),
        "comment": command.comment,
    }


def register_payload(command: RegisterUser) -> dict[str, Any]:
    return {
        "telegram_user_id": command.telegram_user_id,
        "phone": command.phone,
        "name": command.name,
        "address": command.address,
    }
