import asyncio
import logging
import re

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import BOT_TOKEN
from factories.ui import Keyboards, Messages
from services import auth_service, api_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# ── FSM States ─────────────────────────────────────────────────

class AuthStates(StatesGroup):
    waiting_phone = State()
    waiting_code = State()


# ── /start ─────────────────────────────────────────────────────

@dp.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    tg_id = message.from_user.id

    if auth_service.is_logged_in(tg_id):
        ok, data = await auth_service.get_profile(tg_id)
        if ok:
            await message.answer(
                Messages.already_logged_in(data.get("name", "")),
                reply_markup=Keyboards.main_menu(),
            )
            return

    # Не авторизован — начинаем
    await state.set_state(AuthStates.waiting_phone)
    await message.answer(Messages.ask_phone(), reply_markup=Keyboards.phone())


# ── Приём телефона ─────────────────────────────────────────────

@dp.message(AuthStates.waiting_phone, F.contact)
async def on_contact(message: types.Message, state: FSMContext):
    phone = message.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone
    await _process_phone(message, state, phone)


@dp.message(AuthStates.waiting_phone, F.text)
async def on_phone_text(message: types.Message, state: FSMContext):
    phone = message.text.strip()
    if not re.match(r"^\+?\d{10,15}$", phone):
        await message.answer(
            Messages.error("Введите номер кнопкой или в формате +71234567890"),
            reply_markup=Keyboards.phone(),
        )
        return
    if not phone.startswith("+"):
        phone = "+" + phone
    await _process_phone(message, state, phone)


async def _process_phone(message: types.Message, state: FSMContext, phone: str):
    tg_id = message.from_user.id
    name = message.from_user.full_name or "User"

    # 1. Пробуем зарегистрировать (если уже есть — бэк вернёт 409)
    ok, msg = await auth_service.register_and_get_code(
        name=name, phone=phone, telegram_user_id=tg_id,
    )
    if not ok and "уже существует" not in msg.lower():
        await message.answer(Messages.error(msg), reply_markup=Keyboards.phone())
        return

    # 2. Запрашиваем OTP для входа
    ok, code_or_err = await auth_service.request_code(phone)
    if not ok:
        await message.answer(Messages.error(code_or_err), reply_markup=Keyboards.phone())
        return

    await state.update_data(phone=phone, debug_code=code_or_err)
    await state.set_state(AuthStates.waiting_code)

    # Пока debug_code возвращается бэкендом — подсказываем
    hint = f"\n\n🔑 (debug) код: {code_or_err}" if code_or_err else ""
    await message.answer(
        Messages.ask_code() + hint,
        reply_markup=Keyboards.remove(),
    )


# ── Приём OTP-кода ─────────────────────────────────────────────

@dp.message(AuthStates.waiting_code, F.text)
async def on_code(message: types.Message, state: FSMContext):
    code = message.text.strip()
    data = await state.get_data()
    phone = data["phone"]
    tg_id = message.from_user.id

    ok, msg = await auth_service.verify_code(tg_id, phone, code)
    if not ok:
        await message.answer(Messages.error(msg))
        return

    await state.clear()

    # Получаем профиль, чтобы поприветствовать по имени
    ok, profile = await auth_service.get_profile(tg_id)
    name = profile.get("name", "") if ok else ""

    await message.answer(
        Messages.welcome(name),
        reply_markup=Keyboards.main_menu(),
    )


# ── /profile и кнопка «Профиль» ───────────────────────────────

@dp.message(Command("profile"))
@dp.message(F.text == "👤 Профиль")
async def cmd_profile(message: types.Message):
    tg_id = message.from_user.id

    ok, data = await auth_service.get_profile(tg_id)
    if ok:
        await message.answer(Messages.profile(data))
    else:
        await message.answer(Messages.not_authorized())


# ── /logout ────────────────────────────────────────────────────

@dp.message(Command("logout"))
async def cmd_logout(message: types.Message, state: FSMContext):
    await state.clear()
    auth_service.logout(message.from_user.id)
    await message.answer(Messages.logged_out(), reply_markup=Keyboards.remove())


# ── /help ──────────────────────────────────────────────────────

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    await message.answer(
        "📖 Команды:\n"
        "/start — вход / регистрация\n"
        "/profile — ваш профиль\n"
        "/logout — выход\n"
        "/help — эта справка"
    )


# ── Всё остальное ─────────────────────────────────────────────

@dp.message()
async def fallback(message: types.Message):
    if auth_service.is_logged_in(message.from_user.id):
        await message.answer(
            "Используйте меню или /help",
            reply_markup=Keyboards.main_menu(),
        )
    else:
        await message.answer("Для начала работы — /start")


# ── Entrypoint ─────────────────────────────────────────────────

async def main():
    logger.info("Bot starting…")
    try:
        await dp.start_polling(bot)
    finally:
        await api_client.close_session()
        logger.info("Bot stopped")


if __name__ == "__main__":
    asyncio.run(main())
