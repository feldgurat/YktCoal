"""Хендлеры заказчика: создание заказа, просмотр заказов и предложений."""

from __future__ import annotations

from collections.abc import Sequence

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.domain.commands import NewOrder
from app.domain.models import Resource, User
from app.presentation import formatters as fmt
from app.presentation.callbacks import (
    MenuCB,
    OfferAcceptCB,
    OrderActionCB,
    ResourcePickCB,
)
from app.presentation.keyboards.common import back_to_menu_kb, main_menu_kb
from app.presentation.keyboards.customer import (
    offers_kb,
    order_actions_kb,
    resources_kb,
)
from app.presentation.parsing import parse_future_date, parse_positive_decimal
from app.presentation.states import CreateOrder
from app.services.customer_service import CustomerService

router = Router(name="customer")


def _require(current_user: User | None) -> User:
    if current_user is None:
        from app.domain.exceptions import UserNotRegisteredError

        raise UserNotRegisteredError("Сначала отправьте /start для регистрации.")
    return current_user


async def _resource_map(service: CustomerService) -> dict[str, str]:
    return {r.id: r.name for r in await service.list_resources()}


# ── Создание заказа ────────────────────────────────────────────


@router.callback_query(MenuCB.filter(F.section == "new_order"))
async def start_new_order(
    callback: CallbackQuery,
    state: FSMContext,
    current_user: User | None,
    customer_service: CustomerService,
) -> None:
    _require(current_user)
    resources: Sequence[Resource] = await customer_service.list_resources()
    if not resources:
        await callback.message.answer(
            "Сейчас нет доступных видов угля. Загляните позже.",
            reply_markup=back_to_menu_kb(),
        )
        await callback.answer()
        return

    await state.set_state(CreateOrder.choosing_resource)
    await callback.message.answer("Выберите вид угля:", reply_markup=resources_kb(resources))
    await callback.answer()


@router.callback_query(CreateOrder.choosing_resource, ResourcePickCB.filter())
async def pick_resource(
    callback: CallbackQuery,
    callback_data: ResourcePickCB,
    state: FSMContext,
    customer_service: CustomerService,
) -> None:
    resources = await customer_service.list_resources()
    chosen = next((r for r in resources if r.id == callback_data.resource_id), None)
    if chosen is None:
        await callback.answer("Этот вид угля уже недоступен", show_alert=True)
        return

    await state.update_data(
        resource_id=chosen.id,
        resource_name=chosen.name,
        resource_price=str(chosen.price),
    )
    await state.set_state(CreateOrder.entering_volume)
    await callback.message.answer(
        f"Выбрано: <b>{chosen.name}</b> ({chosen.price} ₽/т).\n"
        "Введите объём в тоннах (например, 5 или 12.5):"
    )
    await callback.answer()


@router.message(CreateOrder.entering_volume, F.text)
async def enter_volume(message: Message, state: FSMContext) -> None:
    volume = parse_positive_decimal(message.text)
    await state.update_data(volume=str(volume))
    await state.set_state(CreateOrder.entering_address)
    await message.answer("Укажите адрес доставки:")


@router.message(CreateOrder.entering_address, F.text)
async def enter_address(message: Message, state: FSMContext) -> None:
    address = message.text.strip()
    if not address:
        await message.answer("Адрес не может быть пустым.")
        return
    await state.update_data(dest_address=address)
    await state.set_state(CreateOrder.entering_date)
    await message.answer("Желаемая дата доставки (ДД.ММ.ГГГГ):")


@router.message(CreateOrder.entering_date, F.text)
async def enter_date(message: Message, state: FSMContext) -> None:
    date = parse_future_date(message.text)
    await state.update_data(requested_delivery_date=date.isoformat())
    await state.set_state(CreateOrder.entering_comment)
    await message.answer("Комментарий к заказу (или «-», чтобы пропустить):")


@router.message(CreateOrder.entering_comment, F.text)
async def enter_comment(
    message: Message,
    state: FSMContext,
    current_user: User | None,
    customer_service: CustomerService,
) -> None:
    from datetime import datetime
    from decimal import Decimal

    user = _require(current_user)
    raw = message.text.strip()
    comment = None if raw in {"-", ""} else raw

    data = await state.get_data()
    volume = Decimal(data["volume"])
    price = Decimal(data["resource_price"])
    cost = (volume * price).quantize(Decimal("0.01"))

    command = NewOrder(
        resource_id=data["resource_id"],
        dest_address=data["dest_address"],
        volume=volume,
        cost=cost,
        requested_delivery_date=datetime.fromisoformat(data["requested_delivery_date"]),
        comment=comment,
    )
    order = await customer_service.create_order(user.id, command)
    await state.clear()
    await message.answer(
        "✅ Заказ создан!\n\n" + fmt.order_card(order, data["resource_name"]),
        reply_markup=main_menu_kb(user),
    )


# ── Мои заказы ─────────────────────────────────────────────────


@router.callback_query(MenuCB.filter(F.section == "my_orders"))
async def my_orders(
    callback: CallbackQuery,
    current_user: User | None,
    customer_service: CustomerService,
) -> None:
    user = _require(current_user)
    orders = await customer_service.my_orders(user.id)
    if not orders:
        await callback.message.answer("У вас пока нет заказов.", reply_markup=back_to_menu_kb())
        await callback.answer()
        return

    names = await _resource_map(customer_service)
    for order in orders:
        await callback.message.answer(
            fmt.order_card(order, names.get(order.resource_id)),
            reply_markup=order_actions_kb(order),
        )
    await callback.answer()


@router.callback_query(OrderActionCB.filter(F.action == "view_offers"))
async def view_offers(
    callback: CallbackQuery,
    callback_data: OrderActionCB,
    current_user: User | None,
    customer_service: CustomerService,
) -> None:
    user = _require(current_user)
    offers = await customer_service.offers_for_order(user.id, callback_data.order_id)
    active = [o for o in offers if o.status.value == "pending"]
    if not active:
        await callback.message.answer(
            "По этому заказу пока нет активных предложений.",
            reply_markup=back_to_menu_kb(),
        )
        await callback.answer()
        return

    text = "\n\n".join(fmt.offer_card(o) for o in active)
    await callback.message.answer(
        "📨 Предложения по заказу:\n\n" + text,
        reply_markup=offers_kb(callback_data.order_id, active),
    )
    await callback.answer()


@router.callback_query(OfferAcceptCB.filter())
async def accept_offer(
    callback: CallbackQuery,
    callback_data: OfferAcceptCB,
    current_user: User | None,
    customer_service: CustomerService,
) -> None:
    user = _require(current_user)
    order = await customer_service.accept_offer(
        user.id, callback_data.order_id, callback_data.offer_id
    )
    await callback.message.answer(
        "✅ Предложение принято! Водитель назначен.\n\n" + fmt.order_card(order),
        reply_markup=order_actions_kb(order),
    )
    await callback.answer("Готово")


@router.callback_query(OrderActionCB.filter(F.action == "cancel"))
async def cancel_order(
    callback: CallbackQuery,
    callback_data: OrderActionCB,
    current_user: User | None,
    customer_service: CustomerService,
) -> None:
    user = _require(current_user)
    order = await customer_service.cancel_order(user.id, callback_data.order_id)
    await callback.message.answer(
        "Заказ отменён.\n\n" + fmt.order_card(order),
        reply_markup=back_to_menu_kb(),
    )
    await callback.answer()


@router.callback_query(OrderActionCB.filter(F.action == "complete"))
async def complete_order(
    callback: CallbackQuery,
    callback_data: OrderActionCB,
    current_user: User | None,
    customer_service: CustomerService,
) -> None:
    user = _require(current_user)
    order = await customer_service.complete_order(user.id, callback_data.order_id)
    await callback.message.answer(
        "🏁 Получение подтверждено, заказ выполнен. Спасибо!\n\n" + fmt.order_card(order),
        reply_markup=back_to_menu_kb(),
    )
    await callback.answer()
