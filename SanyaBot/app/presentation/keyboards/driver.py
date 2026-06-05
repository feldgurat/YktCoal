"""Клавиатуры водителя."""

from __future__ import annotations

from collections.abc import Sequence

from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.domain.models import Offer, OfferStatus, Order, OrderStatus
from app.presentation.callbacks import MenuCB, OfferActionCB, OrderActionCB


def available_orders_kb(orders: Sequence[Order]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for o in orders:
        builder.button(
            text=f"➕ Предложить по #{o.id[:6]} ({o.volume} т)",
            callback_data=OfferActionCB(action="make", target_id=o.id),
        )
    builder.button(text="⬅️ В меню", callback_data=MenuCB(section="main"))
    builder.adjust(1)
    return builder.as_markup()


def my_offers_kb(offers: Sequence[Offer]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for o in offers:
        if o.status == OfferStatus.PENDING:
            builder.button(
                text=f"↩️ Отозвать #{o.id[:6]}",
                callback_data=OfferActionCB(action="withdraw", target_id=o.id),
            )
    builder.button(text="⬅️ В меню", callback_data=MenuCB(section="main"))
    builder.adjust(1)
    return builder.as_markup()


def driver_order_actions_kb(order: Order) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if order.status == OrderStatus.ACCEPTED:
        builder.button(
            text="🚚 Начать выполнение",
            callback_data=OrderActionCB(action="start", order_id=order.id),
        )
        builder.button(
            text="↩️ Отказаться",
            callback_data=OrderActionCB(action="withdraw", order_id=order.id),
        )
    builder.button(text="⬅️ В меню", callback_data=MenuCB(section="main"))
    builder.adjust(1)
    return builder.as_markup()
