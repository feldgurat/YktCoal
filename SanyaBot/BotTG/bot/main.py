<<<<<<< HEAD
import asyncio
import logging
import re

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, CommandStart
=======
import sys
import os
from pathlib import Path

# Добавляем корневую папку проекта в путь поиска модулей
root_path = str(Path(__file__).parent.parent)
if root_path not in sys.path:
    sys.path.append(root_path)

import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
>>>>>>> main
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

<<<<<<< HEAD
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
=======
# Импортируем из правильных путей
from services.user_service import UserService
from factories.auth_answer_factory import AuthAnswerFactory
from bot.config import BOT_TOKEN  # теперь это работает, потому что bot - это папка

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Сервисы
user_service = UserService()

# Состояния FSM
class RegistrationStates(StatesGroup):
    waiting_for_phone = State()


@dp.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    telegram_id = message.from_user.id
    
    # Проверяем, зарегистрирован ли пользователь
    if await user_service.is_user_registered(telegram_id):
        # Если зарегистрирован, показываем главное меню
        user = await user_service.get_user(telegram_id)
        welcome_text = (
            f"👋 С возвращением, {user.first_name or 'пользователь'}!\n"
            f"Ваш номер: {user.phone_number}"
        )
        await message.answer(
            welcome_text,
            reply_markup=AuthAnswerFactory.get_main_menu_keyboard()
        )
    else:
        # Если не зарегистрирован, начинаем регистрацию
        await state.set_state(RegistrationStates.waiting_for_phone)
        await message.answer(
            AuthAnswerFactory.get_registration_required_message(),
            reply_markup=AuthAnswerFactory.get_phone_keyboard()
        )


@dp.message(RegistrationStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Обработка номера телефона"""
    telegram_id = message.from_user.id
    phone_number = None
    
    # Проверяем, отправил ли пользователь контакт
    if message.contact:
        phone_number = message.contact.phone_number
        logger.info(f"Получен контакт: {phone_number}")
    else:
        # Если это текстовое сообщение, проверяем, является ли оно номером
        text = message.text.strip()
        if await user_service.validate_phone_number(text):
            phone_number = text
        else:
            await message.answer(
                AuthAnswerFactory.get_invalid_phone_message(),
                reply_markup=AuthAnswerFactory.get_phone_keyboard()
            )
            return
    
    try:
        # Регистрируем пользователя
        user = await user_service.register_user(
            telegram_id=telegram_id,
            phone_number=phone_number,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name
        )
        
        # Очищаем состояние
        await state.clear()
        
        # Отправляем приветственное сообщение
        await message.answer(
            AuthAnswerFactory.get_welcome_message({
                'first_name': user.first_name,
                'phone_number': user.phone_number
            }),
            reply_markup=AuthAnswerFactory.get_main_menu_keyboard()
        )
        
        logger.info(f"Пользователь {telegram_id} успешно зарегистрирован с номером {phone_number}")
        
    except Exception as e:
        logger.error(f"Ошибка при регистрации пользователя {telegram_id}: {e}")
        await message.answer(
            "❌ Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.",
            reply_markup=AuthAnswerFactory.get_phone_keyboard()
        )


@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = (
        "🔍 Доступные команды:\n"
        "/start - Начать работу с ботом\n"
        "/help - Показать это сообщение\n"
        "/profile - Просмотр профиля\n"
        "/logout - Выйти из аккаунта"
    )
    await message.answer(help_text)


@dp.message(Command("profile"))
async def cmd_profile(message: Message):
    """Просмотр профиля"""
    telegram_id = message.from_user.id
    
    if not await user_service.is_user_registered(telegram_id):
        await message.answer(
            "❌ Вы не зарегистрированы. Используйте /start для регистрации."
        )
        return
    
    user = await user_service.get_user(telegram_id)
    profile_text = (
        f"👤 Ваш профиль:\n\n"
        f"📱 Телефон: {user.phone_number}\n"
        f"🆔 Telegram ID: {user.telegram_id}\n"
        f"👤 Username: @{user.username if user.username else 'не указан'}\n"
        f"📅 Зарегистрирован: {user.created_at.strftime('%d.%m.%Y %H:%M')}"
    )
    await message.answer(profile_text)


@dp.message(Command("logout"))
async def cmd_logout(message: Message, state: FSMContext):
    """Выход из аккаунта"""
    telegram_id = message.from_user.id
    
    # Очищаем состояние
    await state.clear()
    
    # Удаляем сессию авторизации если есть
    await user_service.clear_auth_session(telegram_id)
    
    await message.answer(
        "👋 Вы вышли из аккаунта. Для повторной регистрации используйте /start",
        reply_markup=types.ReplyKeyboardRemove()
    )


@dp.message()
async def handle_other_messages(message: Message):
    """Обработка остальных сообщений"""
    telegram_id = message.from_user.id
    
    if await user_service.is_user_registered(telegram_id):
        # Если пользователь зарегистрирован, но отправил что-то другое
        await message.answer(
            "Используйте меню для навигации или /help для списка команд",
            reply_markup=AuthAnswerFactory.get_main_menu_keyboard()
        )
    else:
        # Если не зарегистрирован, предлагаем зарегистрироваться
        await message.answer(
            "❓ Для начала работы используйте команду /start"
        )


async def main():
    """Запуск бота"""
    logger.info("Запуск бота...")
    
    # Создаем необходимые директории
    data_path = Path(__file__).parent.parent / "data"
    data_path.mkdir(exist_ok=True)
    
    # Запускаем бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
>>>>>>> main
