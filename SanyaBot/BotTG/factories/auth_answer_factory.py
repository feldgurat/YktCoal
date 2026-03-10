from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from models.botmodels.auth import AuthSession


class AuthAnswerFactory:
    @staticmethod
    def get_phone_keyboard() -> ReplyKeyboardMarkup:
        """Клавиатура для отправки номера телефона"""
        keyboard = [
            [KeyboardButton(text="📱 Отправить номер телефона", request_contact=True)]
        ]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    
    @staticmethod
    def get_skip_keyboard() -> ReplyKeyboardMarkup:
        """Клавиатура для пропуска шага"""
        keyboard = [
            [KeyboardButton(text="⏭ Пропустить")]
        ]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    
    @staticmethod
    def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
        """Главное меню после регистрации"""
        keyboard = [
            [KeyboardButton(text="🚚 Заказать уголь")],
            [KeyboardButton(text="📋 Мои заказы"), KeyboardButton(text="👤 Профиль")]
        ]
        return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)
    
    @staticmethod
    def get_welcome_message(user_data: dict) -> str:
        """Приветственное сообщение"""
        first_name = user_data.get('first_name', '')
        return (
            f"👋 Добро пожаловать, {first_name}!\n\n"
            f"Вы успешно зарегистрированы с номером:\n"
            f"📱 {user_data.get('phone_number')}\n\n"
            f"Теперь вы можете пользоваться всеми функциями бота."
        )
    
    @staticmethod
    def get_registration_required_message() -> str:
        """Сообщение о необходимости регистрации"""
        return (
            "🔐 Для доступа к функциям бота необходимо зарегистрироваться.\n\n"
            "Пожалуйста, отправьте свой номер телефона, нажав на кнопку ниже:"
        )
    
    @staticmethod
    def get_invalid_phone_message() -> str:
        """Сообщение о неверном номере телефона"""
        return (
            "❌ Пожалуйста, используйте кнопку 'Отправить номер телефона' "
            "для регистрации или введите номер в формате +71234567890"
        )