"""Клавиатуры общего назначения и главное меню."""

from __future__ import annotations

from aiogram.types import (
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.domain.models import User
from app.presentation.callbacks import MenuCB


def request_phone_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="📱 Поделиться номером", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Нажмите кнопку, чтобы поделиться номером",
    )


def main_menu_kb(user: User) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="🧾 Создать заказ", callback_data=MenuCB(section="new_order"))
    builder.button(text="📦 Мои заказы", callback_data=MenuCB(section="my_orders"))
    if user.is_driver:
        builder.button(
            text="🚚 Доступные заказы",
            callback_data=MenuCB(section="available"),
        )
        builder.button(
            text="📨 Мои предложения",
            callback_data=MenuCB(section="my_offers"),
        )
        builder.button(text="🛠 Мои рейсы", callback_data=MenuCB(section="driver_orders"))
    builder.adjust(1)
    return builder.as_markup()


def back_to_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ В меню", callback_data=MenuCB(section="main"))
    return builder.as_markup()
