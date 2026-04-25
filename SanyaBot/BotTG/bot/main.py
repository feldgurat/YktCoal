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
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
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

