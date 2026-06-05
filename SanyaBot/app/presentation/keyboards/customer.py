"""Клавиатуры заказчика."""

from __future__ import annotations

from collections.abc import Sequence

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.domain.models import Offer, Order, OrderStatus, Resource
from app.presentation.callbacks import (
    MenuCB,
    OfferAcceptCB,
    OrderActionCB,
    ResourcePickCB,
)


def resources_kb(resources: Sequence[Resource]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for r in resources:
        builder.button(
            text=f"{r.name} ({r.price} ₽/т)",
            callback_data=ResourcePickCB(resource_id=r.id),
        )
    builder.button(text="⬅️ Отмена", callback_data=MenuCB(section="main"))
    builder.adjust(1)
    return builder.as_markup()


def order_actions_kb(order: Order) -> InlineKeyboardMarkup:
    """Кнопки действий заказчика над конкретным заказом, зависят от статуса."""
    builder = InlineKeyboardBuilder()
    if order.status == OrderStatus.NEW:
        builder.button(
            text="📨 Предложения",
            callback_data=OrderActionCB(action="view_offers", order_id=order.id),
        )
        builder.button(
            text="❌ Отменить",
            callback_data=OrderActionCB(action="cancel", order_id=order.id),
        )
    elif order.status == OrderStatus.ACCEPTED:
        builder.button(
            text="❌ Отменить",
            callback_data=OrderActionCB(action="cancel", order_id=order.id),
        )
    elif order.status == OrderStatus.IN_PROCESS:
        builder.button(
            text="🏁 Подтвердить получение",
            callback_data=OrderActionCB(action="complete", order_id=order.id),
        )
    builder.button(text="⬅️ В меню", callback_data=MenuCB(section="main"))
    builder.adjust(1)
    return builder.as_markup()


def offers_kb(order_id: str, offers: Sequence[Offer]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for o in offers:
        builder.button(
            text=f"✅ Принять {o.price} ₽ (#{o.id[:6]})",
            callback_data=OfferAcceptCB(order_id=order_id, offer_id=o.id),
        )
    builder.button(text="⬅️ В меню", callback_data=MenuCB(section="main"))
    builder.adjust(1)
    return builder.as_markup()
