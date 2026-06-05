"""Хендлеры старта и регистрации (онбординг)."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.domain.models import User
from app.domain.phone import InvalidPhoneError
from app.presentation.callbacks import MenuCB
from app.presentation.keyboards.common import (
    main_menu_kb,
    request_phone_kb,
)
from app.presentation.states import Onboarding
from app.services.auth_service import AuthService

router = Router(name="start")


async def show_main_menu(message: Message, user: User) -> None:
    roles = "Заказчик" + (" + Водитель" if user.is_driver else "")
    await message.answer(
        f"👋 Здравствуйте, <b>{user.name}</b>!\n"
        f"Роль: {roles}\n\nВыберите действие:",
        reply_markup=main_menu_kb(user),
    )


@router.message(CommandStart())
async def cmd_start(
    message: Message, state: FSMContext, current_user: User | None
) -> None:
    await state.clear()
    if current_user is not None:
        await show_main_menu(message, current_user)
        return

    await message.answer(
        "Добро пожаловать в сервис доставки угля! 🪨\n\n"
        "Чтобы продолжить, поделитесь номером телефона — это ваш вход в систему.",
        reply_markup=request_phone_kb(),
    )
    await state.set_state(Onboarding.waiting_phone)


@router.message(Onboarding.waiting_phone, F.contact)
async def on_contact(
    message: Message, state: FSMContext, auth_service: AuthService
) -> None:
    phone = message.contact.phone_number

    # Телефон, привязанный к чужому Telegram-аккаунту, не принимаем.
    if message.contact.user_id and message.contact.user_id != message.from_user.id:
        await message.answer("Пожалуйста, поделитесь СВОИМ номером телефона.")
        return

    try:
        known = await auth_service.phone_belongs_to_known_user(phone)
    except InvalidPhoneError:
        await message.answer("Не удалось распознать номер. Попробуйте ещё раз.")
        return

    await state.update_data(phone=phone)

    if known:
        # Аккаунт уже есть (например, регистрация через веб) — привяжем сразу.
        user = await auth_service.complete_onboarding(
            telegram_user_id=str(message.from_user.id), raw_phone=phone, name=""
        )
        await state.clear()
        await message.answer("Аккаунт найден и привязан ✅")
        await show_main_menu(message, user)
        return

    await message.answer("Как вас зовут? Напишите имя.")
    await state.set_state(Onboarding.waiting_name)


@router.message(Onboarding.waiting_phone)
async def phone_not_shared(message: Message) -> None:
    await message.answer(
        "Нажмите кнопку «📱 Поделиться номером» внизу экрана.",
        reply_markup=request_phone_kb(),
    )


@router.message(Onboarding.waiting_name, F.text)
async def on_name(message: Message, state: FSMContext) -> None:
    name = message.text.strip()
    if not name:
        await message.answer("Имя не может быть пустым. Введите имя.")
        return
    await state.update_data(name=name)
    await message.answer(
        "Укажите адрес доставки по умолчанию (можно пропустить — отправьте «-»)."
    )
    await state.set_state(Onboarding.waiting_address)


@router.message(Onboarding.waiting_address, F.text)
async def on_address(
    message: Message, state: FSMContext, auth_service: AuthService
) -> None:
    address_raw = message.text.strip()
    address = None if address_raw in {"-", ""} else address_raw

    data = await state.get_data()
    user = await auth_service.complete_onboarding(
        telegram_user_id=str(message.from_user.id),
        raw_phone=data["phone"],
        name=data["name"],
        address=address,
    )
    await state.clear()
    await message.answer("Регистрация завершена ✅")
    await show_main_menu(message, user)


@router.callback_query(MenuCB.filter(F.section == "main"))
async def back_to_main(
    callback: CallbackQuery, state: FSMContext, current_user: User | None
) -> None:
    await state.clear()
    await callback.message.answer(
        "Главное меню:",
        reply_markup=main_menu_kb(current_user) if current_user else None,
    )
    await callback.answer()
