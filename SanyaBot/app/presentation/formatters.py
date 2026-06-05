"""Форматирование доменных объектов в текст для пользователя.

Отделяет «как выглядит сообщение» от «что делает хендлер» (SRP).
"""
from __future__ import annotations

from collections.abc import Mapping

from app.domain.models import Offer, OfferStatus, Order, OrderStatus, Resource

_ORDER_STATUS_RU: Mapping[OrderStatus, str] = {
    OrderStatus.NEW: "🆕 Новый",
    OrderStatus.ACCEPTED: "✅ Принят (ждёт начала)",
    OrderStatus.IN_PROCESS: "🚚 В пути",
    OrderStatus.COMPLETED: "🏁 Выполнен",
    OrderStatus.CANCELLED: "❌ Отменён",
}

_OFFER_STATUS_RU: Mapping[OfferStatus, str] = {
    OfferStatus.PENDING: "⏳ Ожидает",
    OfferStatus.ACCEPTED: "✅ Принято",
    OfferStatus.REJECTED: "🚫 Отклонено",
    OfferStatus.WITHDRAWN: "↩️ Отозвано",
}


def order_status(status: OrderStatus) -> str:
    return _ORDER_STATUS_RU.get(status, status.value)


def offer_status(status: OfferStatus) -> str:
    return _OFFER_STATUS_RU.get(status, status.value)


def _date(value) -> str:
    return value.strftime("%d.%m.%Y")


def short_order(order: Order, resource_name: str | None = None) -> str:
    res = resource_name or "—"
    return (
        f"<b>Заказ #{order.id[:8]}</b> · {order_status(order.status)}\n"
        f"Уголь: {res}\n"
        f"Объём: {order.volume} т · Адрес: {order.dest_address}\n"
        f"Желаемая дата: {_date(order.requested_delivery_date)}"
    )


def order_card(order: Order, resource_name: str | None = None) -> str:
    res = resource_name or "—"
    lines = [
        f"<b>Заказ #{order.id[:8]}</b>",
        f"Статус: {order_status(order.status)}",
        f"Уголь: {res}",
        f"Объём: {order.volume} т",
        f"Адрес доставки: {order.dest_address}",
        f"Желаемая дата: {_date(order.requested_delivery_date)}",
        f"Ориентировочная стоимость: {order.cost} ₽",
    ]
    if order.final_price is not None:
        lines.append(f"Итоговая цена: {order.final_price} ₽")
    if order.comment:
        lines.append(f"Комментарий: {order.comment}")
    return "\n".join(lines)


def offer_card(offer: Offer) -> str:
    lines = [
        f"<b>Предложение #{offer.id[:8]}</b>",
        f"Статус: {offer_status(offer.status)}",
        f"Цена: {offer.price} ₽",
        f"Дата доставки: {_date(offer.delivery_date)}",
    ]
    if offer.comment:
        lines.append(f"Комментарий: {offer.comment}")
    return "\n".join(lines)


def resource_line(resource: Resource) -> str:
    return f"{resource.name} — {resource.price} ₽/т"
