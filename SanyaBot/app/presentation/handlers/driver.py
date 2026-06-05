"""Хендлеры водителя: доступные заказы, предложения, выполнение рейсов."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.domain.commands import NewOffer
from app.domain.exceptions import AccessDeniedError, UserNotRegisteredError
from app.domain.models import User
from app.presentation import formatters as fmt
from app.presentation.callbacks import MenuCB, OfferActionCB, OrderActionCB
from app.presentation.keyboards.common import back_to_menu_kb, main_menu_kb
from app.presentation.keyboards.driver import (
    available_orders_kb,
    driver_order_actions_kb,
    my_offers_kb,
)
from app.presentation.parsing import parse_future_date, parse_positive_decimal
from app.presentation.states import CreateOffer
from app.services.driver_service import DriverService

router = Router(name="driver")


def _require_driver(current_user: User | None) -> User:
    if current_user is None:
        raise UserNotRegisteredError("Сначала отправьте /start для регистрации.")
    if not current_user.is_driver:
        raise AccessDeniedError("Этот раздел доступен только водителям.")
    return current_user


# ── Доступные заказы ───────────────────────────────────────────


@router.callback_query(MenuCB.filter(F.section == "available"))
async def available(
    callback: CallbackQuery,
    current_user: User | None,
    driver_service: DriverService,
) -> None:
    _require_driver(current_user)
    orders = await driver_service.available_orders()
    if not orders:
        await callback.message.answer(
            "Сейчас нет доступных заказов.", reply_markup=back_to_menu_kb()
        )
        await callback.answer()
        return

    text = "\n\n".join(fmt.short_order(o) for o in orders)
    await callback.message.answer(
        "🚚 Доступные заказы:\n\n" + text,
        reply_markup=available_orders_kb(orders),
    )
    await callback.answer()


# ── Подача предложения ─────────────────────────────────────────


@router.callback_query(OfferActionCB.filter(F.action == "make"))
async def start_offer(
    callback: CallbackQuery,
    callback_data: OfferActionCB,
    state: FSMContext,
    current_user: User | None,
) -> None:
    _require_driver(current_user)
    await state.update_data(order_id=callback_data.target_id)
    await state.set_state(CreateOffer.entering_price)
    await callback.message.answer(
        f"Предложение по заказу #{callback_data.target_id[:8]}.\n"
        "Введите вашу цену в рублях:"
    )
    await callback.answer()


@router.message(CreateOffer.entering_price, F.text)
async def offer_price(message: Message, state: FSMContext) -> None:
    price = parse_positive_decimal(message.text)
    await state.update_data(price=str(price))
    await state.set_state(CreateOffer.entering_date)
    await message.answer("Дата доставки (ДД.ММ.ГГГГ):")


@router.message(CreateOffer.entering_date, F.text)
async def offer_date(message: Message, state: FSMContext) -> None:
    date = parse_future_date(message.text)
    await state.update_data(delivery_date=date.isoformat())
    await state.set_state(CreateOffer.entering_comment)
    await message.answer("Комментарий (или «-», чтобы пропустить):")


@router.message(CreateOffer.entering_comment, F.text)
async def offer_comment(
    message: Message,
    state: FSMContext,
    current_user: User | None,
    driver_service: DriverService,
) -> None:
    user = _require_driver(current_user)
    raw = message.text.strip()
    comment = None if raw in {"-", ""} else raw

    data = await state.get_data()
    command = NewOffer(
        order_id=data["order_id"],
        price=Decimal(data["price"]),
        delivery_date=datetime.fromisoformat(data["delivery_date"]),
        comment=comment,
    )
    offer = await driver_service.make_offer(user.id, command)
    await state.clear()
    await message.answer(
        "✅ Предложение отправлено заказчику!\n\n" + fmt.offer_card(offer),
        reply_markup=main_menu_kb(user),
    )


# ── Мои предложения ────────────────────────────────────────────


@router.callback_query(MenuCB.filter(F.section == "my_offers"))
async def my_offers(
    callback: CallbackQuery,
    current_user: User | None,
    driver_service: DriverService,
) -> None:
    user = _require_driver(current_user)
    offers = await driver_service.my_offers(user.id)
    if not offers:
        await callback.message.answer(
            "У вас пока нет предложений.", reply_markup=back_to_menu_kb()
        )
        await callback.answer()
        return

    text = "\n\n".join(fmt.offer_card(o) for o in offers)
    await callback.message.answer(
        "📨 Ваши предложения:\n\n" + text,
        reply_markup=my_offers_kb(offers),
    )
    await callback.answer()


@router.callback_query(OfferActionCB.filter(F.action == "withdraw"))
async def withdraw_offer(
    callback: CallbackQuery,
    callback_data: OfferActionCB,
    current_user: User | None,
    driver_service: DriverService,
) -> None:
    user = _require_driver(current_user)
    offer = await driver_service.withdraw_offer(user.id, callback_data.target_id)
    await callback.message.answer(
        "Предложение отозвано.\n\n" + fmt.offer_card(offer),
        reply_markup=back_to_menu_kb(),
    )
    await callback.answer()


# ── Мои рейсы (назначенные заказы) ─────────────────────────────


@router.callback_query(MenuCB.filter(F.section == "driver_orders"))
async def driver_orders(
    callback: CallbackQuery,
    current_user: User | None,
    driver_service: DriverService,
) -> None:
    user = _require_driver(current_user)
    orders = await driver_service.my_orders(user.id)
    if not orders:
        await callback.message.answer(
            "У вас нет назначенных рейсов.", reply_markup=back_to_menu_kb()
        )
        await callback.answer()
        return

    for order in orders:
        await callback.message.answer(
            fmt.order_card(order),
            reply_markup=driver_order_actions_kb(order),
        )
    await callback.answer()


@router.callback_query(OrderActionCB.filter(F.action == "start"))
async def start_order(
    callback: CallbackQuery,
    callback_data: OrderActionCB,
    current_user: User | None,
    driver_service: DriverService,
) -> None:
    user = _require_driver(current_user)
    order = await driver_service.start_order(user.id, callback_data.order_id)
    await callback.message.answer(
        "🚚 Рейс начат. Удачной дороги!\n\n" + fmt.order_card(order),
        reply_markup=back_to_menu_kb(),
    )
    await callback.answer()


@router.callback_query(OrderActionCB.filter(F.action == "withdraw"))
async def withdraw_from_order(
    callback: CallbackQuery,
    callback_data: OrderActionCB,
    current_user: User | None,
    driver_service: DriverService,
) -> None:
    user = _require_driver(current_user)
    order = await driver_service.withdraw_from_order(user.id, callback_data.order_id)
    await callback.message.answer(
        "Вы отказались от заказа, он снова доступен другим водителям.\n\n"
        + fmt.order_card(order),
        reply_markup=back_to_menu_kb(),
    )
    await callback.answer()
